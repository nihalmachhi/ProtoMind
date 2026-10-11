from __future__ import annotations

import sqlite3
from pathlib import Path


class RunStore:
    def __init__(self, database: str) -> None:
        self.path = Path(database)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS runs (
                run_id TEXT PRIMARY KEY,
                capture_name TEXT NOT NULL,
                sha256 TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                status TEXT NOT NULL,
                result_json TEXT,
                error TEXT
            )""")
            db.execute("""CREATE TABLE IF NOT EXISTS experiments (
                experiment_id TEXT PRIMARY KEY,
                target TEXT NOT NULL,
                input_symbol TEXT NOT NULL,
                output_symbol TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )""")

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        return connection

    def create_run(self, run_id: str, name: str, digest: str) -> None:
        with self.connect() as db:
            db.execute(
                "INSERT INTO runs(run_id,capture_name,sha256,status) VALUES(?,?,?,'running')",
                (run_id, name, digest),
            )

    def finish_run(self, run_id: str, result_json: str) -> None:
        with self.connect() as db:
            db.execute(
                "UPDATE runs SET status='complete',result_json=? WHERE run_id=?",
                (result_json, run_id),
            )

    def fail_run(self, run_id: str, error: str) -> None:
        with self.connect() as db:
            db.execute(
                "UPDATE runs SET status='failed',error=? WHERE run_id=?", (error[:1000], run_id)
            )

    def log_experiment(self, experiment_id: str, target: str, sent: str, received: str) -> None:
        with self.connect() as db:
            db.execute(
                "INSERT INTO experiments(experiment_id, target, input_symbol, output_symbol) "
                "VALUES(?,?,?,?)",
                (experiment_id, target, sent, received),
            )

    def get_run(self, run_id: str) -> dict | None:
        with self.connect() as db:
            row = db.execute("SELECT * FROM runs WHERE run_id=?", (run_id,)).fetchone()
        return dict(row) if row else None
