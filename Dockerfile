FROM python:3.11.9-slim

# Choose the type of installation (default - just the base package)
ARG INSTALL_TYPE=normal

WORKDIR /home/abcd-graph

RUN pip install uv

COPY pyproject.toml README.md ./

# Install the project dependencies
RUN if [ "$INSTALL_TYPE" = "normal" ]; then \
        uv pip install --no-cache-dir --system -r pyproject.toml ; \
    else \
        uv pip install --no-cache-dir --system -r pyproject.toml --extra $INSTALL_TYPE ; \
    fi

COPY src src

# Install the project source code
RUN uv pip install --no-cache-dir --system .
