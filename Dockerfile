FROM debian:bookworm-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

# Core utilities and build essentials
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    wget \
    git \
    ca-certificates \
    gnupg \
    build-essential \
    sudo \
    zsh \
    && rm -rf /var/lib/apt/lists/*

# Python 3 + pip
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Node.js LTS (v22) + TypeScript
RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && rm -rf /var/lib/apt/lists/* \
    && npm install -g typescript

# Non-root user with sudo access and zsh as default shell
RUN useradd -m -s /bin/zsh dev \
    && echo "dev ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

USER dev
WORKDIR /home/dev

# Oh My Zsh
RUN sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended

# Claude Code
RUN curl -fsSL https://claude.ai/install.sh | bash

# Ensure Claude Code is on PATH for zsh (installer only updates .bashrc)
RUN echo 'export PATH="${HOME}/.local/bin:${PATH}"' >> "${HOME}/.zshrc"

# Project files
COPY --chown=dev:dev CLAUDE.md /home/dev/CLAUDE.md
COPY --chown=dev:dev format_log.py /home/dev/format_log.py
COPY --chown=dev:dev entrypoint.sh /home/dev/entrypoint.sh

# Skip Claude Code onboarding
RUN echo '{"hasCompletedOnboarding": true}' > "${HOME}/.claude.json"

CMD ["./entrypoint.sh"]
