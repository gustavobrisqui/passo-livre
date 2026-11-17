# Imagem "web": Caddy com os arquivos estáticos do Passo Livre embutidos.
# - usuário não-root (uid 10001), sem capabilities (escuta em portas altas 8080/8443)
# - nenhum segredo na imagem: senhas e domínio chegam por variável de ambiente em tempo de execução
#
# Estágio 1: recompila o Caddy 2.11.9 com golang.org/x/net corrigido.
# O binário oficial vem com x/net v0.60.0 (CVE-2026-78661, HIGH), e o Trivy barrou o pipeline por isso.
FROM caddy:2.11.9-builder-alpine AS build
RUN apk add --no-cache libcap \
 && xcaddy build v2.11.9 --output /tmp/caddy --replace golang.org/x/net=golang.org/x/net@v0.62.0 \
 && (setcap -r /tmp/caddy 2>/dev/null || true) \
 && /tmp/caddy version

FROM caddy:2.11.9-alpine

ARG APP_VERSION=local
LABEL org.opencontainers.image.title="passo-livre-web" \
      org.opencontainers.image.source="https://github.com/gustavobrisqui/passo-livre" \
      org.opencontainers.image.version="${APP_VERSION}"

# Binário recompilado (sem file capabilities: roda com cap_drop: ALL).
COPY --from=build /tmp/caddy /usr/bin/caddy

RUN addgroup -S -g 10001 app \
 && adduser -S -D -H -u 10001 -G app app \
 && mkdir -p /data /config \
 && chown -R app:app /data /config

COPY --chown=root:root Caddyfile /etc/caddy/Caddyfile
COPY --chown=root:root web/ /srv/

USER 10001:10001
ENV XDG_DATA_HOME=/data XDG_CONFIG_HOME=/config
EXPOSE 8080 8443

HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
  CMD wget -q -O /dev/null http://127.0.0.1:8081/healthz || exit 1

CMD ["caddy", "run", "--config", "/etc/caddy/Caddyfile", "--adapter", "caddyfile"]
