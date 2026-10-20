"""Explicit local notes, shared by the CLI and optional Hermes provider."""

from pathlib import Path
from contextlib import contextmanager
import sqlite3


class MemoryStore:
    def recent(self, limit: int = 20):
        if not 1 <= limit <= 100:
            raise ValueError("limit має бути від 1 до 100")
        with self._connect() as db:
            db.row_factory = sqlite3.Row
            return [dict(row) for row in db.execute(
                "SELECT id, project, content, source, created_at FROM notes ORDER BY id DESC LIMIT ?",
                (limit,),
            )]

    def __init__(self, path: Path):
        path = path.expanduser().resolve()
        path.parent.mkdir(parents=True, exist_ok=True)
        self.path = path
        with self._connect() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY, project TEXT NOT NULL,
                content TEXT NOT NULL, source TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
            )""")
        path.chmod(0o600)

    @contextmanager
    def _connect(self):
        db = sqlite3.connect(self.path)
        try:
            with db:
                yield db
        finally:
            db.close()

    def add(self, content: str, *, project: str, source: str) -> int:
        if not content.strip() or not project.strip() or not source.strip():
            raise ValueError("content, project та source не можуть бути порожніми")
        with self._connect() as db:
            cursor = db.execute(
                "INSERT INTO notes(project, content, source) VALUES (?, ?, ?)",
                (project.strip(), content.strip(), source.strip()),
            )
            return int(cursor.lastrowid)

    def search(self, query: str, *, project: str | None = None, limit: int = 10):
        if not query.strip():
            raise ValueError("Пошуковий запит порожній")
        if not 1 <= limit <= 100:
            raise ValueError("limit має бути від 1 до 100")
        # Literal substring search; %, _ and quotes are not interpreted as SQL.
        sql = "SELECT id, project, content, source, created_at FROM notes WHERE instr(content, ?) > 0"
        args: list = [query]
        if project is not None:
            sql += " AND project = ?"
            args.append(project)
        sql += " ORDER BY id DESC LIMIT ?"
        args.append(limit)
        with self._connect() as db:
            db.row_factory = sqlite3.Row
            return [dict(row) for row in db.execute(sql, args)]
