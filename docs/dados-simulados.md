# Dados simulados (geração justificada)

O briefing aceita "dados simulados com geração justificada e documentada". Dois conjuntos do MVP são simulados:

## 1. Relatos de demonstração (`api/app/seed.py`)
- **O que é:** 20 relatos inseridos **só quando o banco está vazio** (`SEED_DEMO=true`), para o mapa não começar em branco na primeira visita e na demonstração.
- **Como foram gerados:** escritos à mão pela equipe, com coordenadas próximas a pontos reais de São Paulo (Av. Paulista, Sé, Terminal Bandeira, Pinheiros, Itaquera, Capão Redondo etc.) e tipos inspirados nas categorias mais comuns de reclamação sobre calçadas.
- **Como identificar:** campo `simulado = true` na API e selo "simulado" na interface.
- **Como desligar:** `SEED_DEMO=false` no `.env`.

## 2. Indicadores por distrito (`web/dados/ouro.json`)
- **O que é:** exemplo do contrato de saída da camada Ouro, até o componente de Big Data publicar o export real.
- **Como foram gerados:** números plausíveis definidos pela equipe, com mais ocorrências e mais tempo de resolução nas periferias (Capão Redondo, Itaquera, Brasilândia) do que no centro expandido. Essa hipótese deve ser confirmada pelos dados reais do SP156.
- **Como identificar:** `metadados.fonte` diz "EXEMPLO SIMULADO", e a tela Distritos mostra a fonte.
- **Como substituir:** PR com o novo `ouro.json` seguindo `docs/contratos.md#ouro-json`.

Relatos feitos por pessoas reais no site publicado **não** são simulados (`simulado = false`).
