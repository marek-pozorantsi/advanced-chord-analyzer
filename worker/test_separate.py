"""API contract tests: fake Demucs output, no model weights required."""
import io
import os
from pathlib import Path
from unittest.mock import patch
import zipfile
from fastapi.testclient import TestClient
import separate

client = TestClient(separate.app)

def test_health():
    assert client.get("/health").json()["weights_verified"] is False

def test_auth_required():
    with patch.dict(os.environ, {"ACA_WORKER_TOKEN": "private"}):
        response = client.post("/separate", files={"file": ("x.wav", b"RIFF", "audio/wav")})
    assert response.status_code == 401

def test_unsupported_format():
    with patch.dict(os.environ, {"ACA_WORKER_TOKEN": "private"}):
        response = client.post("/separate", headers={"Authorization": "Bearer private"},
                               files={"file": ("x.exe", b"abc", "application/octet-stream")})
    assert response.status_code == 415

def test_archive_contains_all_four_stems():
    def fake_run(cmd, **kwargs):
        out = Path(cmd[cmd.index("-o") + 1]) / "htdemucs" / "input"
        out.mkdir(parents=True)
        for stem in ("bass", "drums", "vocals", "other"):
            (out / (stem + ".wav")).write_bytes(b"RIFFfake")
        return type("Result", (), {"returncode": 0})()
    with patch.dict(os.environ, {"ACA_WORKER_TOKEN": "private"}), patch.object(separate.subprocess, "run", side_effect=fake_run):
        response = client.post("/separate", headers={"Authorization": "Bearer private"},
                               files={"file": ("music.wav", b"RIFF", "audio/wav")})
    assert response.status_code == 200
    with zipfile.ZipFile(io.BytesIO(response.content)) as archive:
        assert set(archive.namelist()) == {"bass.wav", "drums.wav", "vocals.wav", "other.wav"}
