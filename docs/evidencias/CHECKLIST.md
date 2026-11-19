# Checklist de evidências (prints para o PDF de DevOps)

Salve os prints nesta pasta. Pode usar o nome indicado ou deixar o nome padrão (`Screenshot …png`):
o Claude identifica cada imagem e renomeia. Os prints marcados com ⭐ são os que mais pesam na rubrica.

Links usados abaixo:
- Repositório: https://github.com/gustavobrisqui/passo-livre
- Run **barrada** (vermelha): https://github.com/gustavobrisqui/passo-livre/actions/runs/44087710974
- Run **corrigida** (verde, com deploy): https://github.com/gustavobrisqui/passo-livre/actions/runs/44089185128
- MVP: https://passolivre-gs.eastus2.cloudapp.azure.com

---

## Parte A: no Mac da empresa (VPN). GitHub, portal Azure e terminal funcionam; só o site é bloqueado.

Preparação, no Terminal:
```bash
cd ~/Desktop/Project
export PATH=~/.local/passolivre-tools/bin:$PATH
```
Print de área no Mac: **Cmd+Shift+4** e arraste (vai para a Mesa). Depois mova para `docs/evidencias/`.

### 1. Container e IaC (5,0)
- [ ] `01-dockerfile-nao-root.png`: abra `Dockerfile` e `api/Dockerfile` (VS Code ou GitHub) mostrando `USER 10001:10001`. Dois prints são aceitos (`01a`, `01b`).
- [ ] ⭐ `02-compose-up.png`: abra o **Docker Desktop**, espere ele ficar verde e rode
      `docker compose up -d --build && docker compose ps`. O print deve mostrar `web` e `api` como **(healthy)**. O primeiro build demora alguns minutos.
- [ ] ⭐ `03-terraform-plan.png`: `cd infra/terraform && terraform plan` → *"No changes. Your infrastructure matches the configuration."*
- [ ] `04-terraform-state.png`: na mesma pasta, `terraform state list` (lista dos recursos criados).
- [ ] ⭐ `05-nsg-portas.png`: portal.azure.com → **rg-passolivre** → **nsg-passolivre** → *Regras de segurança de entrada*. Devem aparecer 80/443 *Permitir* e 22/3389 *Negar*.
- [ ] `06-state-remoto.png`: portal → **rg-passolivre-tfstate** → conta de armazenamento `passolivretf…` → *Contêineres* → `tfstate` (o arquivo de state aparece lá).
- [ ] `07-gitignore.png`: arquivo `.gitignore` mostrando `*.tfstate`, `*.tfvars` e `.env`.

### 2. Pipeline DevSecOps (4,0)
- [ ] ⭐ `08-pipeline-barrada.png`: abra a run **barrada** (link acima) e tire print da página de resumo (vermelha).
- [ ] ⭐ `09-trivy-cve.png`: nessa run → job **Build + Trivy (imagens) (web)** → abra o passo do Trivy → linha `CVE-2026-78661 … HIGH`.
- [ ] ⭐ `10-pipeline-corrigida.png`: abra a run **corrigida** (link acima), com todos os jobs verdes.
- [ ] `11-secrets.png`: repositório → *Settings* → *Secrets and variables* → *Actions* (só aparecem os nomes).
- [ ] `12-oidc.png`: portal → *Microsoft Entra ID* → *Registros de aplicativo* → aba *Todos os aplicativos* → **github-passolivre-deploy** → *Certificados e segredos* → aba *Credenciais federadas*.
- [ ] `13-deploy-smoke.png`: run corrigida → job **Deploy na Azure** → passo *Smoke test* → linha `Versão … no ar.`
- [ ] `14-semgrep-gitleaks.png`: run corrigida → job **Segredos (Gitleaks)** aberto (*no leaks found*). Opcional: outro print do **SAST (Semgrep)**.

### 4. Documentação (2,0)
- [ ] `19-arquitetura.png`: https://github.com/gustavobrisqui/passo-livre/blob/main/docs/arquitetura.md (diagrama renderizado).
- [ ] `20-budget.png`: portal → *Gerenciamento de Custos* → *Orçamentos* → **budget-passolivre-20usd**.
- [ ] `21-trava-runbook.png`: portal → busque **aa-passolivre-finops** → *Trabalhos* (Jobs) → job *Concluído* de 17/11.

---

## Parte B: no computador pessoal (fora da VPN)

### B1. Prints do site (não precisa instalar nada)
- [ ] ⭐ `22-mvp-url-publica.png`: abra o MVP no navegador; o print deve mostrar o **cadeado** e a URL completa.
- [ ] `23-mvp-celular.png`: o mesmo site no celular (Wi-Fi de casa ou 4G).

### B2. Instalar (uma vez)
- **Docker Desktop**: https://www.docker.com/products/docker-desktop/ (abra e espere ficar verde).
- **Git**: no Mac, digite `git` no Terminal e aceite instalar; no Windows, https://git-scm.com (use o **Git Bash** em todos os comandos abaixo).

### B3. Baixar o projeto e criar os segredos (fora do Git, de propósito)
Antes, **no Mac da empresa**, copie a senha das métricas de produção para um lugar seguro (gerenciador de senhas ou nota privada):
```bash
cat ~/Desktop/Project/observability/secrets/metrics_password_azure
```
No computador pessoal:
```bash
git clone https://github.com/gustavobrisqui/passo-livre.git
cd passo-livre
mkdir -p observability/secrets
printf '%s' 'COLE_A_SENHA_AQUI' > observability/secrets/metrics_password_azure
openssl rand -hex 12 > observability/secrets/grafana_admin_password
touch observability/secrets/discord_webhook
./scripts/gerar-env.sh             # cria .env e a senha das métricas locais
docker compose up -d --build       # app local, para os alvos "local" não ficarem em alerta
cd observability && docker compose up -d
```
Confira em http://localhost:9090/targets: os alvos `web` e `api` com `alvo=azure` devem estar **UP**.
Se estiverem DOWN com *401*, a senha foi colada errada: corrija o arquivo e rode `docker compose restart prometheus`.

### 3. Observabilidade (3,0)
- [ ] ⭐ `15-grafana-golden-signals.png`: http://localhost:3000. Usuário `admin`; a senha sai de `cat secrets/grafana_admin_password`. Abra o dashboard **Passo Livre — Golden Signals**, escolha **Ambiente = azure**, navegue uns minutos pelo site (e no celular) para gerar tráfego, espere ~2 min e tire o print com os 4 painéis preenchidos.
- [ ] ⭐ `16-alerta-firing.png`: **derrube a API da nuvem**. Portal Azure → **vm-passolivre** → *Operações* → *Executar comando* → **RunShellScript** → cole e execute:
      `cd /opt/passolivre && docker compose stop api`
      Espere ~2 min e tire o print de http://localhost:9090/alerts com **MVPIndisponivel** *FIRING* (`alvo="azure"`, `job="api"`). Um print do Grafana com o painel vermelho também vale.
- [ ] `17-alerta-discord.png` (opcional): só se configurou o Discord (veja abaixo).
- [ ] ⭐ `18-alerta-resolvido.png`: **religue a API** (mesmo caminho do 16): `cd /opt/passolivre && docker compose start api`.
      Espere ~2 min e tire o print de `/alerts` sem o alerta, ou de `/targets` com `api` **UP** de novo.

> **Não esqueça de religar a API** (passo 18), senão o site fica sem dados para a correção e para o pitch.

Discord (opcional, para o 17): no seu servidor → canal → ⚙️ *Editar canal* → *Integrações* → *Webhooks* → *Novo webhook* → *Copiar URL*. Depois:
```bash
printf '%s' 'COLE_A_URL' > secrets/discord_webhook && docker compose restart alertmanager
```
Faça isso **antes** do passo 16.

### B4. Mandar os prints para o Mac da empresa
Qualquer um destes caminhos funciona: e-mail para você mesmo, Google Drive, AirDrop ou WhatsApp Web (para o print do celular).
Salve tudo em `~/Desktop/Project/docs/evidencias/` e avise o Claude: "prints prontos".

### B5. Desligar no pessoal (depois dos prints)
```bash
cd passo-livre/observability && docker compose down -v
cd .. && docker compose down -v
rm -f observability/secrets/*         # apaga as senhas copiadas
```
