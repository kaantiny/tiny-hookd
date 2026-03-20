FROM debian:bookworm-slim

ARG TARGETARCH

# ============================================================
# 1. System packages
# ============================================================
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    wget \
    ca-certificates \
    jq \
    git \
    build-essential \
    unzip \
    gpg \
    vim-tiny \
    nano \
    python3 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

# ============================================================
# 2. GitHub CLI
# ============================================================
RUN curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg \
      | dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg \
    && chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" \
       > /etc/apt/sources.list.d/github-cli.list \
    && apt-get update && apt-get install -y gh \
    && rm -rf /var/lib/apt/lists/*

# ============================================================
# 3. webhookd (latest release)
# ============================================================
RUN ARCH=$(case "${TARGETARCH}" in \
      amd64) echo "amd64" ;; \
      arm64) echo "arm64" ;; \
      *)     echo "amd64" ;; \
    esac) \
    && LATEST=$(curl -s https://api.github.com/repos/ncarlier/webhookd/releases/latest | jq -r .tag_name) \
    && VERSION=${LATEST#v} \
    && curl -sL "https://github.com/ncarlier/webhookd/releases/download/${LATEST}/webhookd-linux-${ARCH}.tgz" \
       | tar xz -C /usr/local/bin/ \
    && chmod +x /usr/local/bin/webhookd

# ============================================================
# 4. Python packages (system-wide)
# ============================================================
RUN pip3 install --no-cache-dir --break-system-packages \
    # LLM SDKs
    openai \
    anthropic \
    google-generativeai \
    tiktoken \
    # Qodo Merge (PR-Agent) CLI
    qodo-merge \
    # HTTP & data
    requests \
    httpx \
    pydantic \
    pyyaml \
    python-dotenv \
    rich \
    # Retry / resilience
    tenacity \
    backoff \
    retry

# ============================================================
# 5. Install tiny-hookd LLM lib as a proper Python package
# ============================================================
COPY lib/ /opt/tiny-hookd-lib/
RUN pip3 install --no-cache-dir --break-system-packages /opt/tiny-hookd-lib/ \
    && rm -rf /opt/tiny-hookd-lib/

# ============================================================
# 6. Runtime config
# ============================================================
WORKDIR /var/opt/webhookd

ENV PYTHONDONTWRITEBYTECODE=1

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD curl -sf http://localhost:8080/ || exit 1

ENTRYPOINT ["webhookd"]
CMD ["--scripts=/var/opt/webhookd/scripts", "--log-level=info"]
