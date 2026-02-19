# backend/api/compress.py
"""Conversation compression endpoint."""

from fastapi import APIRouter, Request

router = APIRouter(tags=["compress"])


@router.post("/api/sessions/{session_id}/compress")
async def compress_session(session_id: str, request: Request):
    """Compress older messages in a session."""
    am = request.app.state.agent_manager
    messages = am.session_manager.load_session(session_id)

    if len(messages) < 4:
        return {"compressed": 0, "message": "Too few messages to compress"}

    n = len(messages) // 2  # Compress front half

    # Generate summary
    llm = am.llm
    if llm:
        try:
            msgs_text = "\n".join(
                [f"{m['role']}: {m['content'][:200]}" for m in messages[:n]]
            )
            prompt = (
                "Summarize this conversation in 2-3 concise sentences, "
                "preserving key facts and decisions:\n\n"
                f"{msgs_text}\n\nSummary:"
            )
            response = await llm.ainvoke(prompt)
            summary = response.content.strip()
        except Exception:
            summary = f"(Compressed {n} messages)"
    else:
        summary = f"(Compressed {n} messages)"

    archived = am.session_manager.compress_history(session_id, summary=summary, n=n)

    remaining = am.session_manager.load_session(session_id)
    compressed_ctx = am.session_manager.get_compressed_context(session_id)

    return {
        "compressed": archived,
        "remaining_messages": len(remaining),
        "summary": summary,
        "compressed_context": compressed_ctx,
    }
