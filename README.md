# ♿ Passo Livre

**Mapa colaborativo de obstáculos em calçadas e pontos de ônibus para pessoas com deficiência e idosos em São Paulo.**

🌐 **MVP no ar:** https://passolivre-gs.eastus2.cloudapp.azure.com
📄 **API (OpenAPI):** https://passolivre-gs.eastus2.cloudapp.azure.com/api/docs

> Global Solution FIAP 2026.2 — CitizenTech · Engenharia de Software 4º ano (4ES)

---

## Ficha Técnica do MVP

| Campo | Resposta |
|---|---|
| **Nome do produto** | Passo Livre |
| **Cidadão e território** | Pessoas com deficiência, idosos e quem anda a pé ou depende de ônibus na cidade de São Paulo (metrópole). |
| **Problema, em uma frase** | Calçadas e pontos de ônibus com buracos, degraus sem rampa, carros e entulho tiram a autonomia de quem tem mobilidade reduzida, e não há um canal simples para registrar, priorizar e acompanhar a solução. |
| **Proposta de valor** | Relatar um obstáculo em menos de 1 minuto, sem cadastro, e acompanhar publicamente até a solução; para a prefeitura, um mapa priorizado de onde agir primeiro. |
| **Arquitetura: componentes** | Web acessível (HTML/JS + Leaflet) · API FastAPI + SQLite · Caddy (HTTPS, headers, métricas) · VM Azure via Terraform · GitHub Actions DevSecOps (Gitleaks, Semgrep, Trivy) · Prometheus/Grafana/Alertmanager · integração RPA e robô via API · indicadores da camada Ouro (Big Data). Ver [docs/arquitetura.md](docs/arquitetura.md). |
| **Fontes de dados** | Relatos de cidadãos e do robô (API); camada Ouro do pipeline de Big Data (SPTrans Olho Vivo, Open-Meteo, IBGE, SP156) exportada para `web/dados/ouro.json`; dados de demonstração simulados e documentados ([docs/dados-simulados.md](docs/dados-simulados.md)). |
| **Modelos de IA utilizados** | Visão computacional (YOLO) e assistente RAG local — componentes das disciplinas de Visão e GenAI, desenvolvidos por outros integrantes. O MVP publicado não executa modelos de IA. |
| **URL do MVP e repositório** | https://passolivre-gs.eastus2.cloudapp.azure.com · https://github.com/gustavobrisqui/passo-livre |
| **Indicadores de impacto** | Nº de obstáculos relatados · % resolvidos · tempo médio até a solução · confirmações de vizinhos · pontos de ônibus afetados por distrito. |
| **ODS conectados** | **ODS 10** (redução das desigualdades), **ODS 11** (metas 11.2 transporte acessível e 11.7 espaços públicos acessíveis), **ODS 3** (prevenção de quedas e acidentes), **ODS 9** (infraestrutura). |

## Integrantes

| Nome completo | RM |
|---|---|
| _a preencher_ | _a preencher_ |

---

## Como rodar localmente

Pré-requisito: Docker.

```bash
./scripts/gerar-env.sh          # cria .env com segredos aleatórios (fora do Git)
docker compose up -d --build    # sobe web (Caddy) + api (FastAPI)
open http://localhost:8080
```

Monitoramento local (Prometheus + Alertmanager + Grafana com o dashboard das 4 golden signals):

```bash
cd observability
openssl rand -hex 12 > secrets/grafana_admin_password
docker compose up -d
open http://localhost:3000      # usuário admin, senha em secrets/grafana_admin_password
```

Testes da API:

```bash
cd api && python -m venv .venv && .venv/bin/pip install -r requirements-dev.txt && .venv/bin/python -m pytest -q
```

## Infraestrutura (Terraform na Azure)

```bash
az login
./infra/bootstrap-state.sh                       # state remoto em Azure Storage (uma vez)
cd infra/terraform
cp terraform.tfvars.example terraform.tfvars     # ajuste subscription_id (arquivo fora do Git)
terraform init -backend-config=backend.hcl
terraform plan -out=passolivre.tfplan && terraform apply passolivre.tfplan
```

Cria: resource group, VNet, NSG (só 80/443; 22 e 3389 negadas), IP com DNS, VM Ubuntu B1s com cloud-init,
identidade OIDC para o GitHub Actions (permissão só na VM) e a **trava de gasto de US$ 20**
(budget → action group → runbook que desaloca a VM). Detalhes em [docs/custos-finops.md](docs/custos-finops.md).

## Pipeline (GitHub Actions)

`push` em qualquer branch → **Gitleaks** · **Semgrep** · **pytest** · **Trivy config + terraform validate** (paralelos) →
**build + Trivy image** (barra HIGH/CRITICAL) → na `main`: **GHCR** → **deploy via OIDC + `az vm run-command`** → **smoke test**.

## Documentação

- [Arquitetura](docs/arquitetura.md) · [Contratos de integração](docs/contratos.md) · [LGPD](docs/lgpd.md)
- [Responsabilidade compartilhada](docs/responsabilidade-compartilhada.md) · [Custos e FinOps](docs/custos-finops.md)
- [Observabilidade](docs/observabilidade.md) · [Relatório DevOps](docs/relatorio-devops.md) · [Pitch](pitch/roteiro.md)
