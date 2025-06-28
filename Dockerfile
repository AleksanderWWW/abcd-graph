FROM python:3.11.9-slim AS build

# Security updates
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install --only-upgrade -y \
        libexpat1 \
        liblzma5 \
        libsqlite3-0 \
        perl-base && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade setuptools

# Choose the type of installation (default - just the base package)
ARG INSTALL_TYPE=normal

WORKDIR /build

RUN pip install uv

COPY pyproject.toml README.md ./

# Install dependencies into a virtual environment in a temporary location
RUN if [ "$INSTALL_TYPE" = "normal" ]; then \
        uv venv /venv && \
        . /venv/bin/activate && \
        uv pip install --no-cache-dir -r pyproject.toml ; \
    else \
        uv venv /venv && \
        . /venv/bin/activate && \
        uv pip install --no-cache-dir -r pyproject.toml --extra $INSTALL_TYPE ; \
    fi

COPY src src

# Install the actual package into the virtual environment
RUN . /venv/bin/activate && uv pip install --no-cache-dir .

FROM python:3.11.9-slim AS runtime

WORKDIR /home/abcd-graph

# Copy the installed virtual environment from the build stage
COPY --from=build /venv /venv

# Activate venv by default for all shells
ENV PATH="/venv/bin:$PATH"
