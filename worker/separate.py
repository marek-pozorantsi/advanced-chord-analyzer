"""Independent Demucs separation worker. Not deployed on the main Render service."""
from pathlib import Path
from tempfile import TemporaryDirectory
import io
import os
import subprocess
import sys
import zipfile

from fastapi import FastAPI, File, HTTPException, UploadFile, Header
from fastapi.responses import StreamingResponse

app = FastAPI(title="ACA separation worker", version="0.1")
MAX_UPLOAD = 40 * 1024 * 1024
TOKEN = os.environ.get("ACA_WORKER_TOKEN")
EXTENSIONS = {".mp3", ".wav", ".flac", ".ogg", ".m4a"}

@app.get("/health")
def health():
    return {"status": "ok", "model": "htdemucs"}

@app.post("/separate")
async def separate(file: UploadFile = File(...), authorization: str | None = Header(None)):
    if not TOKEN or authorization != f"Bearer {TOKEN}":
        raise HTTPException(401, "Unauthorized")
    ext = Path(file.filename or "").suffix.lower()
    if ext not in EXTENSIONS:
        raise HTTPException(415, "Unsupported format")
    with TemporaryDirectory() as folder:
        root = Path(folder)
        source = root / f"input{ext}"
        total = 0
        with source.open("wb") as out:
            while piece := await file.read(1024 * 1024):
                total += len(piece)
                if total > MAX_UPLOAD:
                    raise HTTPException(413, "Audio file too large")
                out.write(piece)
        cmd = [sys.executable, "-m", "demucs", "--two-stems", "vocals",
               "-n", "htdemucs", "-o", str(root / "output"), str(source)]
        # Note: use full four-stem separation for independent bass.
        cmd.remove("--two-stems")
        cmd.remove("vocals")
        try:
            process = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
        except subprocess.TimeoutExpired:
            raise HTTPException(504, "Separation timed out")
        if process.returncode:
            raise HTTPException(500, "Demucs failed: " + process.stderr[-500:])
        stemdir = root / "output" / "htdemucs" / "input"
        required = ["bass.wav", "drums.wav", "vocals.wav", "other.wav"]
        if not all((stemdir / name).is_file() for name in required):
            raise HTTPException(500, "Missing separated stems")
        memory = io.BytesIO()
        with zipfile.ZipFile(memory, "w", compression=zipfile.ZIP_STORED) as archive:
            for name in required:
                archive.write(stemdir / name, arcname=name)
        memory.seek(0)
        return StreamingResponse(memory, media_type="application/zip",
             headers={"Content-Disposition": 'attachment; filename="stems.zip"'})
