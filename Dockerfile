FROM python:3.11.9-slim

# Choose the type of installation (default - just the base package)
ARG INSTALL_TYPE=normal

WORKDIR /home/abcd-graph

RUN python -m pip install --upgrade pip

COPY pyproject.toml poetry.lock README.md ./

COPY src src/

# Install the project
RUN if [ "$INSTALL_TYPE" = "normal" ]; then \
        pip install --no-cache-dir -e . ; \
    elif [ "$INSTALL_TYPE" = "igraph" ]; then \
        pip install --no-cache-dir -e .[igraph] ; \
    elif [ "$INSTALL_TYPE" = "networkx" ]; then \
        pip install --no-cache-dir -e .[networkx] ; \
    elif [ "$INSTALL_TYPE" = "extended" ]; then \
        pip install --no-cache-dir -e .[extended] ; \
    else \
        echo "Invalid INSTALL_TYPE value: $INSTALL_TYPE" && exit 1 ; \
    fi
