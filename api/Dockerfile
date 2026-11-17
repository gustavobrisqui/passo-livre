# Imagem "api": FastAPI do Passo Livre. Multi-stage, usuário não-root, sem segredo.
FROM python:3.12.16-slim-trixie AS build
ENV PIP_NO_CACHE_DIR=1 PIP_DISABLE_PIP_VERSION_CHECK=1
RUN python -m venv /opt/venv
COPY requirements.txt /tmp/requirements.txt
RUN /opt/venv/bin/pip install --upgrade pip \
 && /opt/venv/bin/pip install -r /tmp/requirements.txt \
 && /opt/venv/bin/pip uninstall -y pip

FROM python:3.12.16-slim-trixie
ARG APP_VERSION=local
LABEL org.opencontainers.image.title="passo-livre-api" \
      org.opencontainers.image.source="https://github.com/gustavobrisqui/passo-livre" \
      org.opencontainers.image.version="${APP_VERSION}"

# Aplica correções de segurança do Debian (ex.: zlib) e remove o pip da imagem final
# (não é necessário em execução e reduz a superfície de ataque).
RUN apt-get update \
 && apt-get upgrade -y --no-install-recommends \
 && rm -rf /var/lib/apt/lists/* \
 && (pip uninstall -y pip setuptools wheel 2>/dev/null || true) \
 && groupadd --gid 10001 app \
 && useradd --uid 10001 --gid 10001 --no-create-home --shell /usr/sbin/nologin app \
 && mkdir -p /data \
 && chown app:app /data

COPY --from=build /opt/venv /opt/venv
WORKDIR /srv
COPY --chown=root:root app/ app/

USER 10001:10001
ENV PATH=/opt/venv/bin:$PATH \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DB_PATH=/data/passolivre.db \
    APP_VERSION=${APP_VERSION}
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
  CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/healthz', timeout=2)"]

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--no-access-log", "--no-server-header"]
