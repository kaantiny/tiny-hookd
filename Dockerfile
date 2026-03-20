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
    # Python
    python3 \
    python3-pip \
    python3-venv \
    # Node.js prerequisites
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
# 3. Node.js 20 LTS
# ============================================================
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# ============================================================
# 4. webhookd (latest release)
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
# 5. Python packages
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
# 6. Node.js packages (global)
# ============================================================
RUN npm install -g \
    openai \
    @anthropic-ai/sdk \
    p-retry@4 \
    async-retry \
    exponential-backoff \
    axios \
    typescript \
    ts-node \
    json

# ============================================================
# 7. Runtime config
# ============================================================
WORKDIR /var/opt/webhookd

ENV NODE_PATH=/usr/lib/node_modules
ENV PYTHONDONTWRITEBYTECODE=1

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD curl -sf http://localhost:8080/ || exit 1

ENTRYPOINT ["webhookd"]
CMD ["--scripts=/var/opt/webhookd/scripts", "--log-level=info"]
