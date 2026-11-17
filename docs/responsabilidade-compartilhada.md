# Modelo de responsabilidade compartilhada (IaaS na Azure)

O Passo Livre roda numa **máquina virtual (IaaS)**. Nesse modelo, a Microsoft protege a nuvem, e a equipe protege o que roda **na** nuvem.

| Camada | Microsoft Azure | Equipe Passo Livre | Como a equipe cumpre |
|---|:---:|:---:|---|
| Datacenter, energia, rede física | ✅ | | — |
| Hardware e hipervisor | ✅ | | — |
| Rede virtual (VNet) e firewall (NSG) | plataforma | **configuração** | Terraform: NSG só 80/443, nega 22/3389 |
| Sistema operacional da VM | imagem oficial | **atualização e endurecimento** | Ubuntu 24.04 LTS; `package_upgrade` no cloud-init; `unattended-upgrades` |
| Runtime de containers | | ✅ | Docker do Ubuntu; containers `read_only`, `cap_drop: ALL`, `no-new-privileges`, limites de memória/CPU |
| Imagens e dependências | | ✅ | Imagens base fixadas, Trivy barra HIGH/CRITICAL, pip removido da imagem final |
| Código da aplicação | | ✅ | Semgrep (SAST), pytest, SQL parametrizado, validação de entrada |
| Segredos | Key Vault/Entra disponíveis | **gestão** | Gerados pelo Terraform; `.env` chmod 600; GitHub Secrets; Gitleaks no histórico |
| Identidade e acesso | Entra ID | **políticas e papéis** | OIDC sem senha, papéis no escopo da VM (mínimo privilégio) |
| Dados e LGPD | criptografia de disco da plataforma | **classificação e minimização** | Sem dado pessoal; logs sem IP (ver `lgpd.md`) |
| Disponibilidade da aplicação | SLA da VM | **monitoramento e resposta** | Prometheus, Grafana, alertas, `restart: unless-stopped`, healthchecks |
| Custos | medição e Cost Management | **orçamento e ação** | Budget US$ 20 + runbook que desaloca a VM |

**Se migrar para PaaS** (Container Apps + PostgreSQL gerenciado), o sistema operacional, o runtime e os patches do banco passam a ser responsabilidade da Microsoft. A equipe continua responsável por código, imagens, identidade, dados e custos.
