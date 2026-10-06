"""One page: drop an audio file, download a 16 kHz WAV."""

from __future__ import annotations

import re
from pathlib import Path

import streamlit as st

from app.convert import ConversionError, convert_to_wav16k

_SAFE_SUFFIX = re.compile(r"^\.[A-Za-z0-9]{1,8}$")
_SAFE_NAME = re.compile(r"[^A-Za-z0-9._-]+")

st.set_page_config(page_title="wowtoWAV", page_icon="🎵")
st.title("wowtoWAV")
st.write("Drop an audio file. Download a 16 kHz mono WAV.")

uploaded = st.file_uploader("Audio file", label_visibility="collapsed")

if uploaded is not None:
    suffix = Path(uploaded.name).suffix.lower()
    if not _SAFE_SUFFIX.fullmatch(suffix):
        suffix = ".bin"
    stem = _SAFE_NAME.sub("_", Path(uploaded.name).stem).strip("._") or "audio"
    try:
        wav = convert_to_wav16k(uploaded.getvalue(), suffix)
    except ConversionError as exc:
        st.error(str(exc) or "Could not convert that file.")
    else:
        st.download_button(
            "Download WAV",
            data=wav,
            file_name=f"{stem}.wav",
            mime="audio/wav",
        )
