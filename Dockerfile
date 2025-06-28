FROM python:3.12-alpine AS build

# Install build tools + curl
RUN apk add --no-cache \
    bash \
    curl \
    libffi-dev \
    build-base \
    linux-headers

# Install uv and upgrade pip/setuptools
RUN pip install --upgrade pip setuptools && pip install uv

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

FROM python:3.12-alpine AS runtime

# Add a non-root user
RUN addgroup -S abcd && adduser -S abcd -G abcd

WORKDIR /home/abcd-graph

# Copy the installed virtual environment from the build stage
COPY --from=build /venv /venv

# Add a default shell
SHELL ["/bin/sh", "-c"]

# Set environment to use venv
ENV PATH="/venv/bin:$PATH"

# Use non-root user
USER abcd

# Default to python REPL
ENTRYPOINT ["python"]
