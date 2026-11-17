# Modelo de negócio: Passo Livre

## Lean canvas (resumo)

| Bloco | Conteúdo |
|---|---|
| **Problema** | 1) Obstáculos em calçadas e pontos de ônibus tiram a autonomia de PcD e idosos. 2) Os canais oficiais são burocráticos e não mostram o andamento. 3) O gestor público não sabe onde priorizar. |
| **Segmentos** | Usuários: PcD, idosos, pais com carrinho, pedestres. Clientes pagantes: prefeituras e subprefeituras (B2G); shoppings, concessionárias de transporte, operadoras e empresas com metas ESG (B2B). |
| **Proposta de valor** | Cidadão: relatar em menos de 1 min, sem cadastro, e acompanhar até a solução. Gestor: mapa priorizado e indicadores por distrito para decidir onde investir. |
| **Solução** | Mapa colaborativo acessível + automação que deduplica, prioriza e encaminha + painel de indicadores. |
| **Canais** | Associações de PcD, conselhos municipais, redes sociais locais, programas de inovação aberta, eventos de cidades inteligentes. |
| **Receita** | B2G: assinatura do painel por subprefeitura/município. B2B: relatório de acessibilidade do entorno + selo. |
| **Custos** | Nuvem (≈ US$ 14/mês no MVP), equipe, suporte, marketing com associações. |
| **Métricas-chave** | Relatos/mês, % resolvidos, tempo médio de resolução, contratos ativos, MRR, CAC, custo por relato. |
| **Vantagem** | Base de dados colaborativa e histórica de acessibilidade urbana, cada vez mais valiosa com o uso (efeito de rede). |

## Preços (hipóteses para validar no piloto)

| Plano | Para quem | Preço | Inclui |
|---|---|---|---|
| **Cidadão** | qualquer pessoa | **Grátis, sempre** | relatar, confirmar, acompanhar |
| **Gestão Pública** | subprefeitura ou município pequeno | **R$ 2.500/mês** | painel priorizado, exportação, integração com o sistema de chamados, SLA |
| **Entorno Acessível** | shopping, concessionária, empresa | **R$ 900/mês por unidade** | relatório mensal do entorno (raio de 1 km), selo e plano de ação |

## Projeção simples (12 meses após o piloto)
- 5 subprefeituras × R$ 2.500 = R$ 12.500/mês
- 10 unidades B2B × R$ 900 = R$ 9.000/mês
- **MRR ≈ R$ 21.500 → ≈ R$ 258 mil/ano**
- Infraestrutura: < 1% da receita (≈ R$ 75–250/mês, ver `docs/custos-finops.md`)

## Indicadores
- **Impacto:** relatos registrados; % resolvidos; tempo médio até a solução; pontos de ônibus acessíveis recuperados; usuários PcD ativos.
- **Negócio:** contratos ativos; MRR; CAC; churn; custo de infraestrutura por relato.

## Pedido
**Piloto de 90 dias** com uma subprefeitura (sugestão: Sé, maior volume de pedestres) e **R$ 150 mil** (edital de inovação ou investimento-anjo) para 12 meses de operação e equipe.
