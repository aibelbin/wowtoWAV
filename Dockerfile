FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY app ./app
COPY streamlit_app.py ./
COPY .streamlit ./.streamlit

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH="/app"

EXPOSE 8501

CMD ["streamlit", "run", "streamlit_app.py"]
