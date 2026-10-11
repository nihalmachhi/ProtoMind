from __future__ import annotations

import asyncio
import hashlib
import json
from pathlib import Path
from typing import Annotated
from uuid import uuid4

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from protomind.api.settings import Settings
from protomind.pipeline import analyze_capture
from protomind.safety.allowlist import LabTargetGuard, TargetRefused
from protomind.safety.redact import redact_message
from protomind.storage.db import RunStore


class ProbeRequest(BaseModel):
    target: str
    message: str = Field(min_length=1, max_length=1024)


def create_app(settings: Settings | None = None) -> FastAPI:
    config = settings or Settings()
    store = RunStore(config.database)
    target_guard = LabTargetGuard(max_queries_per_minute=30)
    captures, runs = Path(config.capture_dir), Path(config.run_dir)
    captures.mkdir(parents=True, exist_ok=True)
    runs.mkdir(parents=True, exist_ok=True)
    app = FastAPI(title="ProtoMind", version="0.1.0")
    app.state.store = store
    app.add_middleware(
        CORSMiddleware, allow_origins=config.origins(), allow_methods=["*"], allow_headers=["*"]
    )

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "project": "ProtoMind"}

    @app.post("/captures", status_code=201)
    async def upload_capture(file: Annotated[UploadFile, File()]) -> dict[str, object]:
        suffix = Path(file.filename or "capture.pcap").suffix.lower()
        if suffix not in {".pcap", ".pcapng"}:
            raise HTTPException(415, "Upload a .pcap or .pcapng capture")
        content = await file.read(config.max_upload_mb * 1024 * 1024 + 1)
        if len(content) > config.max_upload_mb * 1024 * 1024:
            raise HTTPException(413, "Capture exceeds the configured upload limit")
        if not content:
            raise HTTPException(400, "Capture file is empty")
        run_id = uuid4().hex
        digest = hashlib.sha256(content).hexdigest()
        capture_path = captures / f"{run_id}{suffix}"
        capture_path.write_bytes(content)
        store.create_run(run_id, Path(file.filename or "capture").name, digest)
        try:
            result = analyze_capture(capture_path, runs / run_id)
            store.finish_run(run_id, json.dumps(result))
        except Exception as exc:
            store.fail_run(run_id, str(exc))
            raise HTTPException(422, f"Capture analysis failed: {exc}") from exc
        return {"run_id": run_id, "sha256": digest, "status": "complete", "result": result}

    @app.get("/runs/{run_id}")
    def get_run(run_id: str) -> dict[str, object]:
        row = store.get_run(run_id)
        if row is None:
            raise HTTPException(404, "Run not found")
        result = json.loads(row["result_json"]) if row["result_json"] else None
        return {
            "run_id": run_id,
            "capture_name": row["capture_name"],
            "sha256": row["sha256"],
            "status": row["status"],
            "created_at": row["created_at"],
            "result": result,
            "error": row["error"],
        }

    @app.get("/runs/{run_id}/artifacts/{artifact}")
    def artifact(run_id: str, artifact: str) -> FileResponse:
        names = {"json": "model.json", "mermaid": "machine.mmd", "markdown": "spec.md"}
        if artifact not in names:
            raise HTTPException(404, "Unknown artifact")
        path = runs / run_id / names[artifact]
        if not path.is_file():
            raise HTTPException(404, "Artifact not found")
        return FileResponse(path, filename=names[artifact])

    @app.post("/experiments/query")
    async def probe(request: ProbeRequest) -> dict[str, str]:
        if "\r" in request.message or "\n" in request.message:
            raise HTTPException(400, "Send one protocol symbol per query")
        try:
            host, port = target_guard.validate(request.target)
        except TargetRefused as exc:
            raise HTTPException(403, str(exc)) from exc
        try:
            reader, writer = await asyncio.wait_for(asyncio.open_connection(host, port), timeout=2)
            writer.write(request.message.encode("utf-8") + b"\r\n")
            await writer.drain()
            output = (
                (await asyncio.wait_for(reader.readline(), timeout=2))[:4096]
                .decode("utf-8", "replace")
                .rstrip()
            )
            writer.close()
            await writer.wait_closed()
        except (OSError, TimeoutError) as exc:
            raise HTTPException(502, "The local lab target did not return a reply") from exc
        safe_input = redact_message(request.message.encode()).decode("utf-8", "replace")
        store.log_experiment(uuid4().hex, request.target, safe_input, output)
        return {"target": request.target, "input": request.message, "output": output}

    return app


app = create_app()
