# LGPD — onde ficam os dados e como são protegidos

## Princípio: minimização (art. 6º, III)
O Passo Livre **não precisa saber quem é o cidadão** para registrar um buraco na calçada. Por isso não há cadastro.

## Inventário de dados

| Dado | Coletado? | Onde fica | Observação |
|---|---|---|---|
| Nome, e-mail, telefone, CPF | ❌ Não | — | Não existe cadastro nem login para o cidadão |
| Endereço IP | ❌ Não gravado | Só em memória por até 1 min | Usado como **hash diário com sal aleatório** para rate limit; descartado ao reiniciar ou no dia seguinte |
| Logs de acesso | ✅ Sem IP | stdout dos containers (rotação 3×10 MB) | O Caddy remove IP, porta, cabeçalhos e user-agent; a API registra só método, rota, status e tempo |
| Tipo, local e descrição do obstáculo | ✅ | SQLite na VM (`/var/lib/docker/volumes/passolivre_api-data`) | Dado público por natureza; o formulário orienta a **não escrever nomes, placas ou telefones** |
| Fotos | ❌ Não armazenadas | — | O MVP não recebe imagens |
| Geolocalização do aparelho | Só com consentimento | Não é enviada sozinha | O navegador pede permissão; só a coordenada escolhida para o relato é enviada |
| Indicadores por distrito (Ouro) | ✅ Agregados | `web/dados/ouro.json` | Sem dado pessoal; a máscara/hash é feita na camada Ouro do Big Data |
| Tokens (RPA, robô), senha de métricas | Segredos técnicos | `.env` na VM (chmod 600) e state do Terraform (Azure Storage privado) | Nunca no Git; o Gitleaks barra o pipeline |

## Medidas técnicas
- **Em trânsito:** HTTPS obrigatório (Let's Encrypt, HSTS), e o HTTP só redireciona para HTTPS.
- **Em repouso:** disco gerenciado com criptografia da plataforma (SSE padrão da Azure). Storage do state com TLS 1.2+, sem acesso público e com versionamento.
- **Acesso:** sem SSH (porta 22 negada); administração via `az vm run-command` com Entra ID e Activity Log. O deploy usa identidade OIDC restrita à VM.
- **Aplicação:** SQL parametrizado, validação de entrada (tipos fechados, coordenadas só de SP, 280 caracteres), CSP restritiva, sem cookies nem rastreadores de terceiros.
- **Transparência:** a página `/privacidade.html` explica em linguagem simples o que é e o que não é coletado.

## Direitos do titular
Como não há identificação do autor, não há dado pessoal vinculado a um titular. Se uma descrição contiver dado pessoal de terceiros (ex.: placa), a equipe edita ou remove o relato mediante solicitação.

## Retenção
Relatos resolvidos podem ser anonimizados (descrição apagada) após 12 meses, mantendo só tipo, local aproximado e datas para os indicadores.
