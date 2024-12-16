FROM python:3.11.9-slim

# Choose the type of installation (default - just the base package)
ARG INSTALL_TYPE=normal

WORKDIR /home/abcd-graph

RUN python -m pip install --upgrade pip

COPY pyproject.toml README.md ./

COPY src src/

# Install the project
RUN if [ "$INSTALL_TYPE" = "normal" ]; then \
        pip install --no-cache-dir -e . ; \
    else \
        pip install --no-cache-dir -e .[$INSTALL_TYPE] ; \
    fi
