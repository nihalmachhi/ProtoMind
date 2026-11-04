from fastapi.testclient import TestClient

from protomind.api.main import create_app
from protomind.api.settings import Settings
from protomind.safety.redact import redact_message


def test_auth_credentials_are_masked_without_changing_lengths():
    assert redact_message(b"AUTH alice secret\r\n") == b"AUTH ***** ******\r\n"


def test_experiment_endpoint_refuses_non_loopback(tmp_path):
    app = create_app(
        Settings(
            database=str(tmp_path / "db.sqlite"),
            capture_dir=str(tmp_path / "captures"),
            run_dir=str(tmp_path / "runs"),
        )
    )
    with TestClient(app) as client:
        response = client.post(
            "/experiments/query", json={"target": "192.0.2.1:9100", "message": "HELLO demo"}
        )
    assert response.status_code == 403


class FakeWriter:
    def __init__(self) -> None:
        self.written = b""
        self.closed = False

    def write(self, data: bytes) -> None:
        self.written += data

    async def drain(self) -> None:
        return None

    def close(self) -> None:
        self.closed = True

    async def wait_closed(self) -> None:
        return None


class FakeReader:
    async def readline(self) -> bytes:
        return b"AUTH bob hunter2\r\n"


def test_experiment_records_redacted_input_and_output(tmp_path, monkeypatch):
    async def fake_open_connection(host: str, port: int) -> tuple[FakeReader, FakeWriter]:
        return FakeReader(), FakeWriter()

    monkeypatch.setattr("protomind.api.main.asyncio.open_connection", fake_open_connection)
    app = create_app(
        Settings(
            database=str(tmp_path / "db.sqlite"),
            capture_dir=str(tmp_path / "captures"),
            run_dir=str(tmp_path / "runs"),
        )
    )
    with TestClient(app) as client:
        response = client.post(
            "/experiments/query", json={"target": "127.0.0.1:9100", "message": "AUTH alice secret"}
        )
        assert response.status_code == 200
        assert response.json()["output"] == "AUTH bob hunter2"
        with app.state.store.connect() as db:
            row = db.execute("SELECT * FROM experiments").fetchone()
    assert "secret" not in row["input_symbol"]
    assert "hunter2" not in row["output_symbol"]
    assert row["input_symbol"] == "AUTH ***** ******"
    assert row["output_symbol"] == "AUTH *** *******"
