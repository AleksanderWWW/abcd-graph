FROM python:3.9.19
WORKDIR /home/abcd-graph

RUN apt-get update && apt-get -y upgrade
RUN apt-get install -y build-essential

RUN python -m pip install --upgrade pip
COPY . .
RUN pip install -e .
RUN git config --global --add safe.directory /home/abcd-graph
CMD ["/bin/bash"]
