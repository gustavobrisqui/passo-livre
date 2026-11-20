# Observabilidade

Prometheus, Alertmanager e Grafana rodam **na máquina da equipe** (o enunciado permite), coletando o MVP publicado por
HTTPS com basic auth. Isso dá custo zero na nuvem, e a coleta passa pelo mesmo caminho que o usuário: internet → NSG → Caddy.

```
Prometheus (local) ──HTTPS + basic auth──> https://passolivre-gs.eastus2.cloudapp.azure.com/metrics/caddy
                                         └> https://passolivre-gs.eastus2.cloudapp.azure.com/metrics/api
        │ regras de alerta
        ▼
Alertmanager ──> Discord (webhook em secrets/discord_webhook)
Grafana ──> dashboard "Passo Livre — Golden Signals" (variável Ambiente: azure | local)
```

## As 4 golden signals

| Sinal | Métrica (PromQL) | Painel | Alerta |
|---|---|---|---|
| **Latência** | `histogram_quantile(0.95, sum by (le) (rate(caddy_http_request_duration_seconds_bucket{handler="subroute",server!="srv0"}[5m])))` + p95 da API (`passolivre_http_request_duration_seconds`) | 3. Latência p50/p95/p99 | `LatenciaP95Alta` (> 1 s por 5 min) |
| **Tráfego** | `sum by (code) (rate(caddy_http_request_duration_seconds_count{handler="subroute",server!="srv0"}[1m]))` | 1. Tráfego por código | — |
| **Erros** | razão de respostas `5xx` (e `4xx`) sobre o total | 2. Erros % | `TaxaDeErros5xxAlta` (> 5% por 1 min) |
| **Saturação** | `caddy_http_requests_in_flight`, `rate(process_cpu_seconds_total[1m])`, `process_resident_memory_bytes / 256 MB` | 4. Saturação | `SaturacaoMemoriaAPI` (> 200 MB por 5 min) |
| Disponibilidade | `up` | Alvos coletados | `MVPIndisponivel` (`up == 0` por 1 min) |

Indicador de negócio no topo do dashboard: **relatos criados nas últimas 24 h**.

## Como subir

```bash
cd observability
openssl rand -hex 12 > secrets/grafana_admin_password
terraform -chdir=../infra/terraform output -raw metrics_password > secrets/metrics_password_azure
# opcional: URL de webhook do Discord em secrets/discord_webhook
docker compose up -d
```
- Grafana: http://localhost:3000 (usuário `admin`)
- Prometheus: http://localhost:9090/alerts
- Alertmanager: http://localhost:9093

## Como disparar o alerta (demonstração)

```bash
# 1. derruba a aplicação na VM (sem SSH: via run-command)
az vm run-command invoke -g rg-passolivre -n vm-passolivre --command-id RunShellScript \
  --scripts "cd /opt/passolivre && docker compose stop api"
# 2. ~1-2 min depois: MVPIndisponivel e TaxaDeErros5xxAlta ficam FIRING (Prometheus, Grafana, Discord)
# 3. restaura
az vm run-command invoke -g rg-passolivre -n vm-passolivre --command-id RunShellScript \
  --scripts "cd /opt/passolivre && docker compose start api"
# 4. alerta volta a RESOLVED
```
