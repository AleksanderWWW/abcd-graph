FROM ghcr.io/astral-sh/uv:python3.12-trixie-slim AS build

# Install build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    libffi-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Choose the type of installation (default - just the base package)
ARG INSTALL_TYPE=normal

WORKDIR /build

# Keeps Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED=1
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV UV_NO_DEV=1
ENV UV_TOOL_BIN_DIR=/usr/local/bin

COPY pyproject.toml uv.lock README.md ./

# Install the project's dependencies using the lockfile and settings
RUN --mount=type=cache,target=/root/.cache/uv \
    if [ "$INSTALL_TYPE" = "normal" ]; then \
         \
        uv sync --locked --no-install-project ; \
    else \
        uv sync --locked --no-install-project --extra $INSTALL_TYPE ; \
    fi

# Add the rest of the project source code and install it
# Installing separately from its dependencies allows layer caching
COPY abcd_graph abcd_graph
RUN --mount=type=cache,target=/root/.cache/uv \
    if [ "$INSTALL_TYPE" = "normal" ]; then \
        uv sync --frozen --no-editable ; \
    else \
        uv sync --frozen --no-editable --extra $INSTALL_TYPE ; \
    fi


FROM ghcr.io/astral-sh/uv:python3.12-trixie-slim AS runtime

# Add a non-root user (Debian syntax)
RUN useradd -m -s /bin/bash abcd

WORKDIR /home/abcd

# Copy the installed virtual environment from the build stage
COPY --from=build /build/.venv /home/abcd/.venv

# Update paths to search the virtual environment binary directories
ENV PATH="/home/abcd/.venv/bin:$PATH"
ENV PYTHONPATH="/home/abcd"

RUN chown -R abcd:abcd /home/abcd
USER abcd

ENTRYPOINT ["python"]
