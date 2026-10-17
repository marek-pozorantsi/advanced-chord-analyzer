"""Independent Demucs separation worker. Not deployed on the main Render service."""
from pathlib import Path
from tempfile import TemporaryDirectory
import os
import subprocess
import sys
import zipfile

from fastapi import FastAPI, File, HTTPException, UploadFile, Header
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask

app = FastAPI(title="ACA separation worker", version="0.1")
MAX_UPLOAD = 40 * 1024 * 1024
EXTENSIONS = {".mp3", ".wav", ".flac", ".ogg", ".m4a"}

@app.get("/health")
def health():
    return {"status": "ok", "model": "htdemucs", "weights_verified": False}

@app.post("/separate")
async def separate(file: UploadFile = File(...), authorization: str | None = Header(None)):
    token = os.environ.get("ACA_WORKER_TOKEN")
    if not token or authorization != f"Bearer {token}":
        raise HTTPException(401, "Unauthorized")
    ext = Path(file.filename or "").suffix.lower()
    if ext not in EXTENSIONS:
        raise HTTPException(415, "Unsupported format")
    temporary = TemporaryDirectory()
    root = Path(temporary.name)
    try:
        source = root / f"input{ext}"
        total = 0
        with source.open("wb") as out:
            while piece := await file.read(1024 * 1024):
                total += len(piece)
                if total > MAX_UPLOAD:
                    raise HTTPException(413, "Audio file too large")
                out.write(piece)
        cmd = [sys.executable, "-m", "demucs", "-n", "htdemucs", "-o", str(root / "output"), str(source)]
        try:
            process = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
        except subprocess.TimeoutExpired:
            raise HTTPException(504, "Separation timed out")
        if process.returncode:
            raise HTTPException(500, "Demucs separation failed")
        stemdir = root / "output" / "htdemucs" / "input"
        required = ["bass.wav", "drums.wav", "vocals.wav", "other.wav"]
        if not all((stemdir / name).is_file() for name in required):
            raise HTTPException(500, "Missing separated stems")
        output = root / "stems.zip"
        with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_STORED) as archive:
            for name in required:
                archive.write(stemdir / name, arcname=name)
        return FileResponse(output, media_type="application/zip", filename="stems.zip",
                            background=BackgroundTask(temporary.cleanup))
    except BaseException:
        temporary.cleanup()
        raise
