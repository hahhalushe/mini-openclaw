"""LangGraph StateGraph agent engine -- the teaching core."""

from __future__ import annotations

from typing import Any, AsyncIterator

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langgraph.graph import START, END, StateGraph
from typing_extensions import TypedDict

from graph.engines.base import BaseEngine, AgentEvent
from graph.nodes.reason import reason_node
from graph.nodes.act import act_node
from graph.nodes.retrieve import retrieve_node
from graph.nodes.reflect import reflect_node
from graph.nodes.memory_flush import memory_flush_node

MAX_ITERATIONS = 20

# 定义智能体的状态结构，这是在图中流转的唯一数据对象
class AgentState(TypedDict):
    messages: list          # 对话消息列表（System, Human, AI, Tool）
    llm: Any                # 大语言模型实例
    tools: list             # 可用的工具列表
    retriever: Any          # RAG 检索器
    memory_dir: str         # 记忆存储目录
    last_response: Any      # LLM 最近一次的原始响应
    reflection: str         # 反思环节生成的文本
    retrieval_results: list # 检索到的知识片段
    flushed_memories: list  # 准备写入长期记忆的内容
    iteration: int          # 当前迭代次数，用于防止无限工具调用循环


def should_continue(state: AgentState) -> str:
    """条件边路由逻辑：判断是继续执行工具还是进入结束环节"""
    """Route: if last response has tool_calls -> 'act', else -> 'reflect'."""
    # 如果模型最后一条消息包含 tool_calls（工具调用请求）
    last = state.get("last_response")
    if last and hasattr(last, "tool_calls") and last.tool_calls:
        # 且迭代次数未超过最大限制（默认 20 次）
        if state.get("iteration", 0) < MAX_ITERATIONS:
            return "act"  # 跳转到 'act' 节点执行工具
    return "reflect"      # 否则跳转到 'reflect' 节点进行总结/反思


class LangGraphEngine(BaseEngine):
    def __init__(self, llm, tools, retriever=None, memory_dir: str = ""):
        self.llm = llm
        self.tools = tools
        self.retriever = retriever
        self.memory_dir = memory_dir
        self.graph = self._build_graph()   # 初始化时编译状态图

    def _build_graph(self): 
        """核心逻辑：像搭积木一样定义 AI 的思考流程"""
        builder = StateGraph(AgentState)
        # 1. 添加功能节点（每个节点对应一个具体的 Python 函数） 
        builder.add_node("retrieve", retrieve_node)     # 检索节点：从知识库找资料
        builder.add_node("reason", reason_node)         # 推理节点：模型思考并说话
        builder.add_node("act", act_node)              # 行动节点：调用物理工具（如终端）
        builder.add_node("reflect", reflect_node)        # 反思节点：对话结束后总结得失
        builder.add_node("memory_flush", memory_flush_node)    # 刷新节点：将有用信息存入 MEMORY.md

        # 2. 定义执行顺序（边）
        builder.add_edge(START, "retrieve")   # 起点 -> 检索
        builder.add_edge("retrieve", "reason")   # 检索完成 -> 模型推理
        
        # 3. 添加条件跳转（推理后的分支）
        builder.add_conditional_edges(
            "reason", should_continue, {"act": "act", "reflect": "reflect"}   # 根据此函数判断去向
        )
        builder.add_edge("act", "reason")     # 工具执行完 -> 回到推理节点（让模型看结果）
        builder.add_edge("reflect", "memory_flush")    # 反思完 -> 刷新记忆
        builder.add_edge("memory_flush", END)    # 记忆保存完 -> 结束流程

        return builder.compile()   # 编译为可执行的图

    async def astream(
        self,
        message: str,
        history: list[dict],
        system_prompt: str,
    ) -> AsyncIterator[AgentEvent]:
        # Convert history dicts to LangChain messages
        messages = [SystemMessage(content=system_prompt)]
        for msg in history:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                messages.append(AIMessage(content=msg["content"]))
        messages.append(HumanMessage(content=message))

        initial_state: AgentState = {
            "messages": messages,
            "llm": self.llm,
            "tools": self.tools,
            "retriever": self.retriever,
            "memory_dir": self.memory_dir,
            "last_response": None,
            "reflection": "",
            "retrieval_results": [],
            "flushed_memories": [],
            "iteration": 0,
        }

        try:
            async for event in self._stream_with_events(initial_state):
                yield event
        except Exception:
            # Fallback to node-level streaming if astream_events fails
            async for event in self._stream_with_updates(initial_state):
                yield event

    # Nodes whose LLM calls should NOT be streamed to the user
    # 定义“内部节点”，这些节点产生的 LLM 调用不应该让用户看到（后台静默执行）
    _INTERNAL_NODES = frozenset({"reflect", "memory_flush"})

    async def _stream_with_events(
        self, initial_state: AgentState
    ) -> AsyncIterator[AgentEvent]:
        """Real token-level streaming via astream_events."""
        current_parts: list[str] = []
        final_content = ""
        had_tool_execution = False    # 标记是否已经执行了工具调用
        done_sent = False    # 标记是否已经向用户发送了“回答完成”信号

        async for event in self.graph.astream_events(initial_state, version="v2"):
            kind = event["event"]
            # Skip LLM events from internal nodes (reflect, memory_flush)
            # 获取当前产生事件的节点名称
            node = event.get("metadata", {}).get("langgraph_node", "")
            # 【用户体验优化】如果进入了反思或记忆刷新节点
            # Emit done early when internal nodes start — user-facing content is complete
            if node in self._INTERNAL_NODES and not done_sent:
                # 立即向前端发送 done，前端会停止加载动画，尽管后台还在跑反思逻辑
                yield AgentEvent(type="done", data={"content": final_content})
                done_sent = True
                continue

            if done_sent:
                continue  # Skip all remaining events from internal nodes# 如果已经“完成”了，就跳过后续所有内部节点的细节流
            # 处理 Token 流（模型说话）
            if kind == "on_chat_model_stream":
                chunk = event["data"]["chunk"]
                content = getattr(chunk, "content", "")
                if isinstance(content, str) and content:
                    # 如果刚才刚跑完工具，现在模型回应工具结果，发送信号让前端分段显示
                    if had_tool_execution:
                        yield AgentEvent(type="new_response", data={})
                        had_tool_execution = False
                    yield AgentEvent(type="token", data={"content": content})
                    current_parts.append(content)
            # 处理模型结束（检查是否要调工具）
            elif kind == "on_chat_model_end":
                output = event["data"]["output"]
                # Fallback: if no streaming tokens were captured, yield full content
                # 兜底：处理非流式输出
                if not current_parts:
                    content = getattr(output, "content", "")
                    if content:
                        if had_tool_execution:
                            yield AgentEvent(type="new_response", data={})
                            had_tool_execution = False
                        yield AgentEvent(type="token", data={"content": content})
                        current_parts.append(content)

                final_content = "".join(current_parts)
                current_parts.clear()

                # Check for tool calls
                # 发现工具调用，告知前端显示“思考链”
                if hasattr(output, "tool_calls") and output.tool_calls:
                    for tc in output.tool_calls:
                        yield AgentEvent(
                            type="tool_start",
                            data={"tool": tc["name"], "input": tc.get("args", {})},
                        )
            # 工具运行结束，回传结果
            elif kind == "on_tool_end":
                tool_name = event.get("name", "tool")
                output = event["data"].get("output", "")
                yield AgentEvent(
                    type="tool_end",
                    data={"tool": tool_name, "output": str(output)},
                )
                had_tool_execution = True
            # 检索结束，回传参考文档（UI 会显示“已检索 X 条资料”）
            elif kind == "on_retriever_end":
                docs = event["data"].get("output", [])
                if docs:
                    yield AgentEvent(
                        type="retrieval",
                        data={
                            "results": [
                                {"text": d.page_content, "score": d.metadata.get("score", 0)}
                                for d in docs[:3]
                            ]
                        },
                    )
        # 如果流程走完还没发过 done（比如没有进入内部节点），则补发
        if not done_sent:
            yield AgentEvent(type="done", data={"content": final_content})

    async def _stream_with_updates(
        self, initial_state: AgentState
    ) -> AsyncIterator[AgentEvent]:
        """Fallback: node-level streaming (no token-by-token, but still functional)."""
        final_content = ""
        seen_tool_msg_ids: set[str] = set()
        done_sent = False
        async for event in self.graph.astream(initial_state, stream_mode="updates"):
            for node_name, node_output in event.items():
                # Emit done early when internal nodes start
                if node_name in self._INTERNAL_NODES and not done_sent:
                    yield AgentEvent(type="done", data={"content": final_content})
                    done_sent = True
                    continue

                if done_sent:
                    continue

                if node_name == "retrieve" and node_output.get("retrieval_results"):
                    yield AgentEvent(
                        type="retrieval",
                        data={"results": node_output["retrieval_results"]},
                    )

                if node_name == "reason":
                    last = node_output.get("last_response")
                    if last:
                        content = last.content if hasattr(last, "content") else ""
                        if content:
                            yield AgentEvent(
                                type="token", data={"content": content}
                            )
                            final_content = content
                        if hasattr(last, "tool_calls") and last.tool_calls:
                            for tc in last.tool_calls:
                                yield AgentEvent(
                                    type="tool_start",
                                    data={"tool": tc["name"], "input": tc["args"]},
                                )

                if node_name == "act":
                    msgs = node_output.get("messages", [])
                    for m in msgs:
                        if isinstance(m, ToolMessage):
                            msg_id = getattr(m, "tool_call_id", id(m))
                            if msg_id not in seen_tool_msg_ids:
                                seen_tool_msg_ids.add(msg_id)
                                yield AgentEvent(
                                    type="tool_end",
                                    data={"tool": getattr(m, "name", "tool"), "output": m.content},
                                )
                    yield AgentEvent(type="new_response", data={})

        if not done_sent:
            yield AgentEvent(type="done", data={"content": final_content})
            
"""Stateful Memory（状态记忆）：通过 AgentState 携带 retrieval_results 和 reflection，使得 AI 的推理过程不仅基于对话历史，还基于实时的“草稿本”。

User-facing vs. Internal（面向用户 vs. 内部）：利用 _INTERNAL_NODES 机制，将反思（Reflect）和记忆清理（Flush）等耗时操作放在“后台”完成，用户在看到回答后即可开始下一次提问，无需等待记忆写入完成。

标准化翻译：该类本质上是一个翻译器，将 LangGraph 复杂的各种 on_xxx_end 事件翻译成前端能够理解并渲染的 AgentEvent。"""
