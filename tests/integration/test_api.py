from conftest import write_tinykv_capture
from fastapi.testclient import TestClient

from protomind.api.main import create_app
from protomind.api.settings import Settings


def test_upload_runs_pipeline_and_exposes_artifacts(tmp_path):
    capture = write_tinykv_capture(tmp_path / "tinykv.pcap")
    settings = Settings(
        database=str(tmp_path / "runs.sqlite"),
        capture_dir=str(tmp_path / "captures"),
        run_dir=str(tmp_path / "outputs"),
    )
    with TestClient(create_app(settings)) as client:
        response = client.post(
            "/captures",
            files={"file": ("tinykv.pcap", capture.read_bytes(), "application/octet-stream")},
        )
        assert response.status_code == 201
        run_id = response.json()["run_id"]
        assert client.get(f"/runs/{run_id}").json()["status"] == "complete"
        assert client.get(f"/runs/{run_id}/artifacts/markdown").status_code == 200
