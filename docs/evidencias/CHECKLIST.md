# Checklist de evidências (prints para o PDF de DevOps)

Salve os prints nesta pasta com o nome indicado. Cada print precisa de uma **legenda** no PDF.

## 1. Container e IaC (5,0)
- [ ] `01-dockerfile-nao-root.png`: trecho do `Dockerfile` e do `api/Dockerfile` com `USER 10001`
- [ ] `02-compose-up.png`: terminal com `docker compose up -d --build` e `docker compose ps` (healthy)
- [ ] `03-terraform-plan.png`: `terraform plan` (24 recursos)
- [ ] `04-terraform-apply.png`: `Apply complete! Resources: 24 added`
- [ ] `05-nsg-portas.png`: portal Azure → nsg-passolivre → Inbound rules (80/443 permitidas, 22/3389 negadas)
- [ ] `06-state-remoto.png`: portal → Storage `passolivretf…` → container `tfstate` (state fora do repositório)
- [ ] `07-gitignore.png`: `.gitignore` mostrando `*.tfstate`, `*.tfvars` e `.env`

## 2. Pipeline DevSecOps (4,0)
- [ ] `08-pipeline-barrada.png`: GitHub → Actions → run do commit `feat: MVP…` (vermelho)
- [ ] `09-trivy-cve.png`: log do job **Build + Trivy (web)** com `CVE-2026-78661 HIGH`
- [ ] `10-pipeline-corrigida.png`: run do commit `fix(web)…` (todos os jobs verdes, deploy ok)
- [ ] `11-secrets.png`: Settings → Secrets and variables → Actions (só nomes, valores ocultos)
- [ ] `12-oidc.png`: portal → Entra ID → App registrations → `github-passolivre-deploy` → Federated credentials
- [ ] `13-deploy-smoke.png`: log do job **Deploy** com `Versão xxxxxxx no ar.`
- [ ] `14-semgrep-gitleaks.png`: jobs Semgrep e Gitleaks verdes (opcional: log "no leaks found")

## 3. Observabilidade (3,0)
- [ ] `15-grafana-golden-signals.png`: dashboard "Passo Livre — Golden Signals" (Ambiente = azure) com dados
- [ ] `16-alerta-firing.png`: Prometheus `/alerts` ou Grafana com **MVPIndisponivel FIRING**
- [ ] `17-alerta-discord.png`: (se configurado) mensagem no Discord
- [ ] `18-alerta-resolvido.png`: alerta RESOLVED depois de religar a API

## 4. Documentação (2,0)
- [ ] `19-arquitetura.png`: diagrama de `docs/arquitetura.md` renderizado no GitHub
- [ ] `20-budget.png`: portal → Cost Management → Budgets → `budget-passolivre-20usd`
- [ ] `21-trava-runbook.png`: portal → Automation → Jobs do runbook `Desalocar-VM-Passo-Livre` (teste concluído)
- [ ] `22-mvp-url-publica.png`: site aberto na URL pública (cadeado HTTPS)
- [ ] `23-mvp-celular.png`: site no celular
