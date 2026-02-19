"""Layer 1: Daily Logs -- append-only markdown files per day."""

from datetime import date, timedelta
from pathlib import Path


class DailyLog:
    def __init__(self, logs_dir: str | Path):
        self.dir = Path(logs_dir)
        self.dir.mkdir(parents=True, exist_ok=True)

    def append(self, content: str) -> None:
        """Append a memory entry to today's daily log."""
        log_path = self.dir / f"{date.today().isoformat()}.md"
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"- {content}\n")

    def read_recent(self, days: int = 7) -> str:
        """Read daily logs from the last N days."""
        lines = []
        for i in range(days):
            d = date.today() - timedelta(days=i)
            path = self.dir / f"{d.isoformat()}.md"
            if path.is_file():
                lines.append(f"## {d.isoformat()}\n")
                lines.append(path.read_text(encoding="utf-8"))
        return "\n".join(lines)

    def list_logs(self) -> list[str]:
        """Return list of log filenames sorted by date."""
        return sorted([f.name for f in self.dir.glob("*.md")], reverse=True)
