import sqlite3

import pytest

from protomind.storage.db import RunStore


def test_store_closes_connections_after_each_operation(tmp_path):
    store = RunStore(str(tmp_path / "runs.sqlite3"))
    with store.connect() as db:
        assert db.execute("SELECT 1").fetchone()[0] == 1
    with pytest.raises(sqlite3.ProgrammingError):
        db.execute("SELECT 1")


def test_runs_and_experiments_round_trip(tmp_path):
    store = RunStore(str(tmp_path / "runs.sqlite3"))
    store.create_run("run-1", "demo.pcap", "a" * 64)
    assert store.get_run("run-1")["status"] == "running"
    store.finish_run("run-1", '{"ok": true}')
    assert store.get_run("run-1")["status"] == "complete"
    store.create_run("run-2", "broken.pcap", "b" * 64)
    store.fail_run("run-2", "bad capture")
    assert store.get_run("run-2")["error"] == "bad capture"
    store.log_experiment("exp-1", "127.0.0.1:9100", "AUTH *** ******", "AUTH *** ******")
    with store.connect() as db:
        row = db.execute("SELECT * FROM experiments WHERE experiment_id='exp-1'").fetchone()
    assert row["input_symbol"] == "AUTH *** ******"
