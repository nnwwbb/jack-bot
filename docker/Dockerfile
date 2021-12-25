FROM python:3.9
RUN useradd -ms /bin/bash jack
RUN mkdir /workspace
USER jack
ENV PATH=$PATH:/home/jack/.local/bin
WORKDIR /workspace
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY . .
