"""HTTP API: upload any audio file, download a 16 kHz WAV."""

from __future__ import annotations

import re
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import Response

from app.convert import ConversionError, convert_to_wav16k

MAX_UPLOAD_BYTES = 50 * 1024 * 1024
_SAFE_SUFFIX = re.compile(r"^\.[A-Za-z0-9]{1,8}$")
_SAFE_NAME = re.compile(r"[^A-Za-z0-9._-]+")

app = FastAPI(
    title="wowtoWAV",
    description="Upload any audio file and get back a 16 kHz mono WAV.",
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/convert")
async def convert(file: UploadFile = File(...)) -> Response:
    """Accept one audio file and return 16 kHz, mono, 16-bit PCM WAV."""
    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="empty file")
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="file exceeds 50 MB")

    suffix = Path(file.filename or "").suffix.lower()
    if not _SAFE_SUFFIX.fullmatch(suffix):
        suffix = ".bin"

    try:
        wav = convert_to_wav16k(data, suffix)
    except ConversionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    stem = Path(file.filename or "audio").stem
    filename = _SAFE_NAME.sub("_", stem).strip("._") or "audio"
    return Response(
        content=wav,
        media_type="audio/wav",
        headers={"Content-Disposition": f'attachment; filename="{filename}.wav"'},
    )
