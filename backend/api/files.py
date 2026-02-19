# backend/api/files.py
"""File operations and skills listing API."""

from pathlib import Path

from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel

router = APIRouter(tags=["files"])

# Whitelist of accessible directories (relative to base_dir)
ALLOWED_DIRS = {"workspace", "memory", "skills", "knowledge"}
ALLOWED_FILES = {"SKILLS_SNAPSHOT.md"}


class FileWriteRequest(BaseModel):
    path: str
    content: str


@router.get("/api/files")
async def read_file(path: str, request: Request):
    """Read a file from whitelisted directories."""
    base_dir: Path = request.app.state.base_dir
    target = (base_dir / path).resolve()

    # Security: verify path is within allowed directories
    if not _is_allowed(path, base_dir, target):
        raise HTTPException(status_code=403, detail="Access denied: path not in whitelist")

    if not target.is_file():
        raise HTTPException(status_code=404, detail=f"File not found: {path}")

    try:
        content = target.read_text(encoding="utf-8")
        return {"path": path, "content": content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/files")
async def write_file(req: FileWriteRequest, request: Request):
    """Write to a file in whitelisted directories."""
    base_dir: Path = request.app.state.base_dir
    target = (base_dir / req.path).resolve()

    if not _is_allowed(req.path, base_dir, target):
        raise HTTPException(status_code=403, detail="Access denied: path not in whitelist")

    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(req.content, encoding="utf-8")
        return {"path": req.path, "status": "saved"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/skills")
async def list_skills(request: Request):
    """List all available skills."""
    from tools.skills_scanner import scan_skills
    base_dir: Path = request.app.state.base_dir
    skills = scan_skills(base_dir / "skills")
    return {"skills": skills}


def _is_allowed(path: str, base_dir: Path, resolved: Path) -> bool:
    """Check if a path is within allowed directories."""
    # Prevent path traversal
    if not str(resolved).startswith(str(base_dir)):
        return False

    # Check against whitelist
    parts = Path(path).parts
    if not parts:
        return False

    if parts[0] in ALLOWED_DIRS:
        return True
    if path in ALLOWED_FILES:
        return True

    return False
