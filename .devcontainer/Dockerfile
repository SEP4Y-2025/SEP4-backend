FROM mcr.microsoft.com/vscode/devcontainers/base:ubuntu-22.04

ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies: Python, Node.js, build tools, Mosquitto dev libraries, Git, etc.
RUN apt-get update && apt-get install -y \
    python3 python3-pip \
    curl \
    build-essential \
    libmosquitto-dev \
    git \
    apt-transport-https \
    ca-certificates \
    gnupg \
    lsb-release

# Install Node.js (using NodeSource for Node 22)
RUN curl -sL https://deb.nodesource.com/setup_22.x | bash - && \
    apt-get install -y nodejs

# Install Docker CLI (and Docker Compose plugin)
RUN curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
        | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] \
    https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" \
        | tee /etc/apt/sources.list.d/docker.list > /dev/null && \
    apt-get update && \
    apt-get install -y docker-ce-cli docker-compose-plugin

# Upgrade pip
RUN python3 -m pip install --upgrade pip

WORKDIR /workspace
EXPOSE 8000

RUN apt-get clean && rm -rf /var/lib/apt/lists/*
