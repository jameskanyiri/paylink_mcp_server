# Stage 1: Build Stage
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS build

# Set working directory
WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Set UV link mode to copy to avoid issues with mounted volumes
ENV UV_LINK_MODE=copy

# Mount cache to speed up dependency installation
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    uv sync --frozen --no-install-project --no-dev

# Stage 2: Runtime Stage
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

# Set working directory
WORKDIR /app

# Copy application source code
COPY . .

# Install the application
RUN uv sync --locked

# Expose application port
EXPOSE 8050

# Command to run the application
CMD ["uv", "run", "paylink.py"]
