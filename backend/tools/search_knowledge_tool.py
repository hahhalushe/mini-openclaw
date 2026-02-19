"""Knowledge base search tool — placeholder until RAG is wired in Task 13."""

from langchain_core.tools import tool as lc_tool, BaseTool


def create_search_knowledge_tool(retriever=None) -> BaseTool:

    @lc_tool
    def search_knowledge_base(query: str) -> str:
        """Search the knowledge base for relevant information using hybrid retrieval."""
        if retriever is None:
            return "(Knowledge base not yet initialized. Place documents in knowledge/ directory.)"
        try:
            docs = retriever.invoke(query)
            if not docs:
                return "No relevant results found."
            results = []
            for i, doc in enumerate(docs[:3], 1):
                source = doc.metadata.get("source", "unknown")
                results.append(f"[{i}] {source}\n{doc.page_content[:500]}")
            return "\n---\n".join(results)
        except Exception as e:
            return f"Search error: {e}"

    return search_knowledge_base
