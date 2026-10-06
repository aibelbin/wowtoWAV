"""Turn an uploaded audio file into 16 kHz mono PCM WAV."""

from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

import imageio_ffmpeg

SAMPLE_RATE = 16000
CHANNELS = 1


class ConversionError(Exception):
    """The input could not be decoded or written as WAV."""


def convert_to_wav16k(data: bytes, suffix: str = ".bin") -> bytes:
    """Decode any ffmpeg-supported audio and return 16 kHz mono 16-bit WAV bytes."""
    if not data:
        raise ConversionError("empty audio")

    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    with tempfile.TemporaryDirectory() as tmp:
        source = Path(tmp) / f"input{suffix}"
        target = Path(tmp) / "output.wav"
        source.write_bytes(data)

        result = subprocess.run(
            [
                ffmpeg,
                "-hide_banner",
                "-loglevel",
                "error",
                "-y",
                "-i",
                str(source),
                "-vn",
                "-ar",
                str(SAMPLE_RATE),
                "-ac",
                str(CHANNELS),
                "-c:a",
                "pcm_s16le",
                str(target),
            ],
            capture_output=True,
            check=False,
        )
        if result.returncode != 0 or not target.is_file() or target.stat().st_size == 0:
            detail = result.stderr.decode("utf-8", errors="replace").strip()
            raise ConversionError(detail or "could not convert audio to WAV")

        return target.read_bytes()
