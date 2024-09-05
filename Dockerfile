FROM python:3.11.9-slim

WORKDIR /home/abcd-graph

RUN python -m pip install --upgrade pip

COPY pyproject.toml poetry.lock README.md ./

COPY src src/

RUN pip install --no-cache-dir -e .

CMD ["/bin/bash"]
