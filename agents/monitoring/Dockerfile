# Use the latest Python 3.13 image with uv installed
FROM ghcr.io/astral-sh/uv:python3.13-bookworm AS base

# Stage for building the application
FROM base AS builder

# Pull latest uv image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
# Set environment variables for uv
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

WORKDIR /app

# Create a directory for the application
RUN mkdir -p agent

# Copy the application code
COPY . agent/
WORKDIR /app/agent

# Create lockfile
RUN --mount=type=cache,target=/root/.cache/uv \
    uv lock --prerelease=allow

# Install the application dependencies using uv
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev
# Stage for the final image
FROM base

# Copy the built application from the builder stage
COPY --from=builder /app /app

# Set environment variables for the final image
ENV PATH="/app/.venv/bin:$PATH"

# Set the working directory to the application directory
WORKDIR /app/agent

# Run the application using nat a2a serve
CMD ["uv", "run", "nat", "a2a", "serve", "--config_file", "configs/nemo_rng.yml"]
