# backend/tests/test_session_manager.py
import tempfile
from pathlib import Path


def test_create_and_load_session():
    from graph.session_manager import SessionManager
    with tempfile.TemporaryDirectory() as td:
        sm = SessionManager(sessions_dir=td)
        sid = sm.create_session()
        assert sid is not None
        messages = sm.load_session(sid)
        assert messages == []


def test_save_and_load_messages():
    from graph.session_manager import SessionManager
    with tempfile.TemporaryDirectory() as td:
        sm = SessionManager(sessions_dir=td)
        sid = sm.create_session()
        sm.save_message(sid, "user", "Hello")
        sm.save_message(sid, "assistant", "Hi there!")
        messages = sm.load_session(sid)
        assert len(messages) == 2
        assert messages[0]["role"] == "user"


def test_list_sessions():
    from graph.session_manager import SessionManager
    with tempfile.TemporaryDirectory() as td:
        sm = SessionManager(sessions_dir=td)
        sm.create_session()
        sm.create_session()
        sessions = sm.list_sessions()
        assert len(sessions) == 2


def test_compress_history():
    from graph.session_manager import SessionManager
    with tempfile.TemporaryDirectory() as td:
        sm = SessionManager(sessions_dir=td)
        sid = sm.create_session()
        for i in range(6):
            sm.save_message(sid, "user" if i % 2 == 0 else "assistant", f"msg {i}")
        archived = sm.compress_history(sid, summary="Summary of conversation", n=4)
        assert archived == 4
        remaining = sm.load_session(sid)
        assert len(remaining) == 2  # 6 - 4 = 2
        ctx = sm.get_compressed_context(sid)
        assert "Summary of conversation" in ctx
