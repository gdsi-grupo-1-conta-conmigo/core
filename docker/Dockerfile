FROM python:3.12-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /core

# Copy project files
COPY ./app /core/app
COPY uv.lock pyproject.toml /core

# Install dependencies (locked for reproducibility)
RUN uv sync --frozen --no-cache

# Expose default FastAPI port
EXPOSE 80

# Default command (can be overridden by docker-compose or docker run)
CMD ["uv", "run", "fastapi", "run", "app/main.py", "--port", "80", "--host", "0.0.0.0"]
