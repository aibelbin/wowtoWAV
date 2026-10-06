import io
import math
import struct
import wave

from fastapi.testclient import TestClient

from app.convert import convert_to_wav16k
from app.main import app

client = TestClient(app)


def _tone_wav(rate: int = 44100, channels: int = 2, seconds: float = 0.25) -> bytes:
    frames = int(rate * seconds)
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wav:
        wav.setnchannels(channels)
        wav.setsampwidth(2)
        wav.setframerate(rate)
        samples = bytearray()
        for i in range(frames):
            value = int(16000 * math.sin(2 * math.pi * 440 * i / rate))
            packed = struct.pack("<h", value)
            samples.extend(packed * channels)
        wav.writeframes(samples)
    return buffer.getvalue()


def _assert_wav16k(data: bytes) -> None:
    with wave.open(io.BytesIO(data), "rb") as wav:
        assert wav.getframerate() == 16000
        assert wav.getnchannels() == 1
        assert wav.getsampwidth() == 2
        assert wav.getnframes() > 0


def test_convert_stereo_wav_to_16k_mono():
    result = convert_to_wav16k(_tone_wav(), ".wav")
    _assert_wav16k(result)


def test_endpoint_returns_wav():
    response = client.post(
        "/convert",
        files={"file": ("clip.wav", _tone_wav(), "audio/wav")},
    )
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("audio/wav")
    assert 'filename="clip.wav"' in response.headers["content-disposition"]
    _assert_wav16k(response.content)


def test_endpoint_rejects_empty_file():
    response = client.post("/convert", files={"file": ("empty.wav", b"", "audio/wav")})
    assert response.status_code == 400


def test_endpoint_rejects_non_audio():
    response = client.post(
        "/convert",
        files={"file": ("notes.txt", b"this is not audio", "text/plain")},
    )
    assert response.status_code == 400
