# Contratos de integração

Documentação interativa (OpenAPI): `https://passolivre-gs.eastus2.cloudapp.azure.com/api/docs`

Base URL de produção: `https://passolivre-gs.eastus2.cloudapp.azure.com`
Local: `http://localhost:8080`

> Os tokens (`RPA_TOKEN`, `ROBO_TOKEN`) são gerados pelo Terraform e passados aos responsáveis **por canal privado**.
> Nunca os coloque no repositório: o Gitleaks barra o pipeline.

## Valores aceitos

- **tipo**: `buraco`, `carro_na_calcada`, `entulho`, `degrau_sem_rampa`, `ponto_onibus_inacessivel`,
  `calcada_estreita`, `arvore_raiz`, `iluminacao`, `outro` (lista atualizada em `GET /api/tipos`)
- **status**: `novo`, `em_analise`, `encaminhado`, `resolvido`, `duplicado`
- **prioridade**: `baixa`, `media`, `alta`
- **lat/lon**: dentro do município de São Paulo (lat −24,01 a −23,35; lon −46,83 a −46,36)

## Relatos

### `GET /api/relatos` (público)
Parâmetros opcionais: `status`, `tipo`, `desde` (ISO 8601, filtra por `atualizado_em`), `limite` (1–1000).

```json
[{
  "id": 21, "tipo": "degrau_sem_rampa", "tipo_rotulo": "Degrau sem rampa",
  "descricao": "Degrau na esquina", "lat": -23.5614, "lon": -46.6559,
  "status": "novo", "prioridade": null, "protocolo": null, "origem": "app",
  "confirmacoes": 0, "simulado": false,
  "criado_em": "2026-11-17T12:36:25+00:00", "atualizado_em": "2026-11-17T12:36:25+00:00"
}]
```

### `GET /api/relatos/{id}` (público)
O mesmo objeto, mais `historico: [{status, nota, autor, em}]`.

### `POST /api/relatos` (cidadão: público com rate limit; robô: token)
```json
{ "tipo": "entulho", "descricao": "texto opcional (até 280)", "lat": -23.55, "lon": -46.63, "origem": "app" }
```
- Cidadão: `origem` = `app` (padrão). Limite de 10 envios por minuto por cliente → `429`.
- **Robô (Maker Lab):** `origem` = `robo` e cabeçalho `X-Api-Key: <ROBO_TOKEN>`; sem token → `401`.
- Resposta `201` com o relato criado. Entrada inválida → `422`.

### `POST /api/relatos/{id}/confirmar` (público com rate limit)
Soma 1 em `confirmacoes` ("Também vi isso").

## Integração RPA

### `PATCH /api/relatos/{id}` — cabeçalho `Authorization: Bearer <RPA_TOKEN>`
```json
{ "status": "em_analise", "prioridade": "alta", "protocolo": "PL-2026-0042", "nota": "Perto de ponto de ônibus" }
```
- `prioridade`, `protocolo` e `nota` são opcionais (se omitidos, mantêm o valor anterior).
- Sem token ou token errado → `401`; relato inexistente → `404`.
- Resposta `200` com o relato e o histórico (autor `rpa`).

Fluxo sugerido do bot:
1. `GET /api/relatos?status=novo`
2. Para cada relato: duplicado (mesmo tipo a menos de 30 m de outro aberto)? → `status: duplicado`
3. Senão, regra de prioridade (ex.: `ponto_onibus_inacessivel` ou `degrau_sem_rampa` → `alta`)
4. Gera o protocolo do chamado e envia o `PATCH` com `status: em_analise` ou `encaminhado`.

Exemplo em Python:
```python
import os, requests
BASE = os.environ["PASSOLIVRE_URL"]
H = {"Authorization": f"Bearer {os.environ['RPA_TOKEN']}"}
for r in requests.get(f"{BASE}/api/relatos", params={"status": "novo"}, timeout=10).json():
    prioridade = "alta" if r["tipo"] in ("ponto_onibus_inacessivel", "degrau_sem_rampa") else "media"
    requests.patch(f"{BASE}/api/relatos/{r['id']}", headers=H, timeout=10,
                   json={"status": "em_analise", "prioridade": prioridade,
                         "protocolo": f"PL-2026-{r['id']:04d}"}).raise_for_status()
```

## Big Data → `web/dados/ouro.json` <a id="ouro-json"></a>

O componente de dados exporta a agregação da camada Ouro (fato de ocorrências × dimensão distrito) e abre um
PR substituindo `web/dados/ouro.json`. O pipeline valida, publica e a tela **Distritos** passa a exibir os dados.

```json
{
  "metadados": {
    "tabela_origem": "workspace.gs.ouro_fato_ocorrencias",
    "fonte": "texto exibido na tela",
    "atualizado_em": "AAAA-MM-DD",
    "dados_pessoais": "nenhum"
  },
  "distritos": [{
    "distrito": "Sé", "subprefeitura": "Sé",
    "total_ocorrencias": 142, "resolvidas": 51, "tempo_medio_resolucao_dias": 38,
    "tipo_mais_comum": "calcada_estreita", "pontos_onibus_afetados": 17
  }]
}
```
Regras: apenas agregados, **sem dado pessoal** (LGPD); `tipo_mais_comum` usa os valores de `tipo` acima.

## Operacionais
| Rota | Uso |
|---|---|
| `GET /healthz` | saúde da API e do banco (smoke test) |
| `GET /version` | SHA curto do commit em produção |
| `GET /metrics/caddy`, `GET /metrics/api` | Prometheus (basic auth) |
