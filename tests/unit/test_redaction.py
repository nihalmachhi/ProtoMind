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
