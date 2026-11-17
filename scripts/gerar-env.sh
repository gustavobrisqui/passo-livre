#!/usr/bin/env bash
# Gera um .env local com segredos aleatórios (não sobrescreve um .env existente).
# Também grava a senha do Prometheus em observability/secrets/metrics_password (fora do Git).
set -euo pipefail
cd "$(dirname "$0")/.."

if [[ -f .env ]]; then
  echo ".env já existe — nada a fazer (apague-o para gerar de novo)."
  exit 0
fi

senha_metricas="$(openssl rand -hex 16)"
hash_metricas="$(docker run --rm caddy:2.11.9-alpine caddy hash-password --bcrypt-cost 10 --plaintext "$senha_metricas")"

mkdir -p observability/secrets
umask 077
printf '%s' "$senha_metricas" > observability/secrets/metrics_password

cat > .env <<EOF
SITE_ADDRESS=:8080
HTTP_PORT=8080
HTTPS_PORT=8443
IMAGE_TAG=local
RPA_TOKEN=$(openssl rand -hex 24)
ROBO_TOKEN=$(openssl rand -hex 24)
METRICS_USER=prometheus
METRICS_HASH='${hash_metricas}'
SEED_DEMO=true
RATE_LIMIT_POR_MINUTO=10
EOF
chmod 600 .env
echo "OK: .env e observability/secrets/metrics_password criados (ambos ignorados pelo Git)."
