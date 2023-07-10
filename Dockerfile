FROM ghcr.io/opennmt/ctranslate2:latest-ubuntu20.04-cuda11.2

ENV PYTHON_VERSION=3.10

RUN apt update

RUN apt install -y software-properties-common

RUN add-apt-repository ppa:deadsnakes/ppa

RUN apt-get update && apt-get install -y \
     #build-essential \
     #gcc \
     #git \
     curl \
     ffmpeg

RUN export DEBIAN_FRONTEND=noninteractive \
    && apt-get -qq update \
    && apt-get -qq install --no-install-recommends \
    git \
    python${PYTHON_VERSION} \
    python${PYTHON_VERSION}-venv \
    python3-pip \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

RUN ln -s -f /usr/bin/python${PYTHON_VERSION} /usr/bin/python3 && \
    ln -s -f /usr/bin/python${PYTHON_VERSION} /usr/bin/python && \
    ln -s -f /usr/bin/pip3 /usr/bin/pip

RUN curl -sS https://bootstrap.pypa.io/get-pip.py | python3.10

RUN pip install --upgrade pip

RUN pip install torch==2.0.0+cu117 torchvision==0.15.1+cu117 torchaudio==2.0.1+cu117 --extra-index-url https://download.pytorch.org/whl/cu117

RUN pip install git+https://github.com/m-bain/whisperx.git




