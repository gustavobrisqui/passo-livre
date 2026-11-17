# Deploy Blindado — Passo Livre
**Secure DevOps Tools & Cloud Computing · Global Solution FIAP 2026.2 · 4ES**

| | |
|---|---|
| **MVP (URL pública)** | https://passolivre-gs.eastus2.cloudapp.azure.com |
| **Repositório** | https://github.com/gustavobrisqui/passo-livre |
| **Pipeline** | https://github.com/gustavobrisqui/passo-livre/actions |
| **Integrantes** | _nome completo — RM (preencher)_ |

---

## Ficha Técnica do MVP
Ver tabela completa no [README](https://github.com/gustavobrisqui/passo-livre#ficha-técnica-do-mvp).
Resumo: mapa colaborativo e acessível de obstáculos em calçadas e pontos de ônibus de São Paulo para PcD e idosos.
Relato sem cadastro em menos de 1 minuto, acompanhamento público até a solução e indicadores por distrito. ODS 10, 11, 3 e 9.

## 1. Arquitetura
Diagrama e decisões: [docs/arquitetura.md](arquitetura.md).
VM Ubuntu B1s na Azure (East US 2), criada por Terraform, rodando `docker compose` com dois containers:
**web** (Caddy, HTTPS automático) e **api** (FastAPI + SQLite). Deploy pelo GitHub Actions via OIDC.
Observabilidade local (Prometheus, Alertmanager, Grafana) coletando a URL pública.

## 2. Container e IaC (5,0)

### 2.1 Docker (2,0)
- **Dockerfile enxuto:** `api` multi-stage `python:3.12-slim` com pip removido da imagem final; `web` recompila o Caddy só com o necessário. `.dockerignore` restritivo (só `app/` e `requirements.txt`; só `web/` e `Caddyfile`).
- **Usuário não-root:** `USER 10001:10001` nas duas imagens. O Caddy escuta em portas altas (8080/8443), então o container roda com `cap_drop: ALL`, `read_only: true` e `no-new-privileges`.
- **Sem segredo na imagem:** tokens e hash de senha entram por variável de ambiente do `.env` (fora do Git). O Trivy procura segredos dentro das imagens (`--scanners vuln,secret`).
- **Stack com docker compose:** `docker compose up -d --build` sobe web e api com healthchecks, limites de CPU/memória e rotação de logs. É o mesmo arquivo local e na nuvem.

> 📷 Prints 01 e 02

### 2.2 Terraform (3,0)
- **24 recursos:** RG, VNet/subnet, NSG, IP público com DNS, NIC, VM com cloud-init e identidade gerenciada, app registration + 2 federated credentials (OIDC) + role assignment, Automation Account + runbook + webhook, Action Group, Budget.
- **State fora do repositório:** backend `azurerm` em Storage Account própria (`rg-passolivre-tfstate`, TLS 1.2, sem acesso público, versionamento). `backend.hcl`, `*.tfstate`, `*.tfvars` e `*.tfplan` estão no `.gitignore`; existe só o `terraform.tfvars.example`.
- **Porta admin nunca aberta para 0.0.0.0/0:** o NSG permite apenas 80/443 vindo da Internet e tem regra explícita `nega-admin` para **22 e 3389**. Não existe SSH: administração e deploy usam `az vm run-command` (Entra ID + Activity Log).

> 📷 Prints 03 a 07

## 3. Pipeline DevSecOps (4,0)
Arquivo: `.github/workflows/ci-cd.yml`. Executa **a cada push**:

| Etapa | Ferramenta | Barra o pipeline quando |
|---|---|---|
| Segredos | **Gitleaks** v8.30.1 (histórico completo) | encontra qualquer segredo |
| SAST | **Semgrep** 1.185.0 (`p/ci`, `p/python`, `p/dockerfile`, `p/javascript`, `p/secrets`) | qualquer achado bloqueante |
| Testes | **pytest** (14 testes da API) | algum teste falha |
| IaC | **Trivy config** + `terraform fmt/validate` | misconfiguração HIGH/CRITICAL |
| Imagens | **build** + **Trivy image** (vuln + secret) | CVE HIGH/CRITICAL com correção disponível |
| Publicação | GHCR (tag = SHA curto + `latest`) | — (só na `main`) |
| Deploy | `azure/login` via **OIDC** + `az vm run-command` | — (só na `main`) |
| Smoke test | `curl /version` = SHA do commit + `/healthz` | a nova versão não responde |

- **Segredos em GitHub Secrets:** `AZURE_CLIENT_ID`, `AZURE_TENANT_ID` e `AZURE_SUBSCRIPTION_ID`. **Não há senha da Azure**: o OIDC troca o token do workflow por um token de curta duração, com permissão só na VM.
- **Actions fixadas por SHA:** o próprio Semgrep apontou o risco de supply chain de tags mutáveis, que foi corrigido.

### Execução barrada e corrigida
| Commit | O que aconteceu |
|---|---|
| `faaba7d` | ❌ **Barrada:** o Trivy encontrou **CVE-2026-78661 (HIGH)** em `golang.org/x/net v0.60.0`, embutido no binário oficial do Caddy 2.11.9. O job *Build + Trivy (web)* falhou e o **deploy não foi executado**. |
| `7bdcaf0` | ✅ Correção do CVE: o Caddy passou a ser recompilado com `xcaddy` e `golang.org/x/net v0.62.0`, e todos os scans e builds ficaram verdes. ❌ O deploy falhou no login OIDC (`AADSTS700213`): o GitHub agora emite o *subject* com IDs imutáveis (`repo:owner@id/repo@id`). |
| `b0bd0d8` | ✅ **Corrigida:** credenciais federadas ajustadas no Terraform. **Pipeline 100% verde**, com deploy e smoke test (`Versão b0bd0d8 no ar`). |
| `00fe151` | ✅ Endurecimento LGPD: o logger padrão do Caddy deixou de registrar IP de bots com host desconhecido. |

> 📷 Prints 08 a 14

## 4. Observabilidade (3,0)
Detalhes: [docs/observabilidade.md](observabilidade.md).
- **Dashboard das 4 golden signals** (Grafana, provisionado por código): latência p50/p95/p99, tráfego por código HTTP, % de erros 4xx/5xx e saturação (requisições em andamento, CPU e memória da API), além de disponibilidade e relatos em 24 h.
- **Alertas** (Prometheus → Alertmanager → Discord): `MVPIndisponivel`, `TaxaDeErros5xxAlta`, `LatenciaP95Alta`, `SaturacaoMemoriaAPI`.
- **Alerta disparado:** a API foi parada na VM via run-command, o alerta ficou FIRING, a API foi religada e o alerta passou a RESOLVED.

> 📷 Prints 15 a 18

## 5. Documentação (2,0)
- **Diagrama da arquitetura:** [docs/arquitetura.md](arquitetura.md)
- **Responsabilidade compartilhada:** [docs/responsabilidade-compartilhada.md](responsabilidade-compartilhada.md)
- **Onde ficam os dados pessoais (LGPD):** [docs/lgpd.md](lgpd.md). O MVP não coleta dado pessoal, os logs saem sem IP e os segredos ficam só no `.env` (chmod 600) e no state privado.
- **Estimativa de custo:** [docs/custos-finops.md](custos-finops.md). **≈ US$ 13,64/mês** (≈ US$ 4,50 no período da GS), com **trava automática de US$ 20** (budget → runbook que desaloca a VM).
  **Teste da trava (17/11):** o webhook foi chamado, o job do runbook foi criado e a VM passou de `running` para `deallocated` em cerca de 1 min. Ao religar (`az vm start`), o site voltou sozinho (healthz 200).
- **README reproduzível:** passo a passo local, Terraform, pipeline e observabilidade.

> 📷 Prints 19 a 23

## Conclusão
O Passo Livre está no ar numa infraestrutura criada só por código, sem porta administrativa exposta, com deploy sem senha
armazenada e com segurança verificada a cada commit. O pipeline provou seu valor ao barrar uma vulnerabilidade real
antes de ela chegar ao cidadão. O custo cabe no crédito estudantil e tem uma trava automática contra surpresas.
