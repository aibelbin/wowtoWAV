import io
import math
import struct
import wave
from pathlib import Path

from streamlit.testing.v1 import AppTest

APP_PATH = Path(__file__).resolve().parents[1] / "streamlit_app.py"


def _tone_wav() -> bytes:
    rate = 44100
    frames = rate // 4
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wav:
        wav.setnchannels(2)
        wav.setsampwidth(2)
        wav.setframerate(rate)
        samples = bytearray()
        for i in range(frames):
            value = int(8000 * math.sin(2 * math.pi * 440 * i / rate))
            packed = struct.pack("<h", value)
            samples.extend(packed * 2)
        wav.writeframes(samples)
    return buffer.getvalue()


def test_drop_file_shows_download():
    app = AppTest.from_file(APP_PATH, default_timeout=30)
    app.run()
    assert not app.exception
    assert len(app.download_button) == 0

    app.file_uploader[0].upload("clip.wav", _tone_wav()).run()
    assert not app.exception
    assert len(app.error) == 0
    assert app.download_button[0].label == "Download WAV"
