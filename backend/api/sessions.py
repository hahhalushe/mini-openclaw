# backend/api/sessions.py
"""Session management API endpoints."""

from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/sessions", tags=["sessions"])


class CreateSessionRequest(BaseModel):
    title: str = "New Chat"


class RenameSessionRequest(BaseModel):
    title: str


@router.get("")
async def list_sessions(request: Request):
    sm = request.app.state.agent_manager.session_manager
    return sm.list_sessions()


@router.post("")
async def create_session(req: CreateSessionRequest, request: Request):
    sm = request.app.state.agent_manager.session_manager
    sid = sm.create_session(title=req.title)
    return {"id": sid, "title": req.title}


@router.get("/{session_id}/messages")
async def get_messages(session_id: str, request: Request):
    sm = request.app.state.agent_manager.session_manager
    messages = sm.load_session(session_id)
    return {"session_id": session_id, "messages": messages}


@router.get("/{session_id}/history")
async def get_history(session_id: str, request: Request):
    sm = request.app.state.agent_manager.session_manager
    messages = sm.load_session(session_id)
    compressed = sm.get_compressed_context(session_id)
    return {
        "session_id": session_id,
        "messages": messages,
        "compressed_context": compressed,
    }


@router.put("/{session_id}")
async def rename_session(session_id: str, req: RenameSessionRequest, request: Request):
    sm = request.app.state.agent_manager.session_manager
    sm.rename_session(session_id, req.title)
    return {"id": session_id, "title": req.title}


@router.delete("/{session_id}")
async def delete_session(session_id: str, request: Request):
    sm = request.app.state.agent_manager.session_manager
    sm.delete_session(session_id)
    return {"deleted": session_id}


@router.post("/{session_id}/generate-title")
async def generate_title(session_id: str, request: Request):
    """Use LLM to generate a title from the first few messages."""
    sm = request.app.state.agent_manager.session_manager
    llm = request.app.state.agent_manager.llm

    messages = sm.load_session(session_id)
    if not messages:
        return {"session_id": session_id, "title": "New Chat"}

    if not llm:
        # Fallback: use first user message truncated
        for m in messages:
            if m["role"] == "user":
                title = m["content"][:30] + ("..." if len(m["content"]) > 30 else "")
                sm.rename_session(session_id, title)
                return {"session_id": session_id, "title": title}
        return {"session_id": session_id, "title": "New Chat"}

    # Use LLM to generate title
    try:
        first_msgs = messages[:4]
        conversation = "\n".join([f"{m['role']}: {m['content'][:200]}" for m in first_msgs])
        prompt = (
            "Given this conversation, generate a very short title "
            "(5-10 words, in the language of the conversation):\n\n"
            f"{conversation}\n\nTitle:"
        )
        response = await llm.ainvoke(prompt)
        title = response.content.strip().strip('"').strip("'")[:50]
        sm.rename_session(session_id, title)
        return {"session_id": session_id, "title": title}
    except Exception:
        return {"session_id": session_id, "title": "New Chat"}
