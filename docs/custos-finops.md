# Custos e FinOps

Preços de varejo (pay-as-you-go) consultados na **Azure Retail Prices API** em 17/11/2026, região **East US 2**, em US$.
Convertidos para reais com a referência **US$ 1 = R$ 5,50** (ajuste para o câmbio do dia).

## Estimativa mensal da produção

| Recurso | Configuração | Preço unitário | Mês (730 h) |
|---|---|---|---|
| VM | Standard_B1s (1 vCPU, 1 GiB), Linux | US$ 0,0104/h | **US$ 7,59** |
| Disco do SO | Standard SSD E4 (30/32 GiB) | US$ 2,40/mês | **US$ 2,40** |
| IP público | Standard IPv4 estático | US$ 0,005/h | **US$ 3,65** |
| Automation (trava) | Runbook, só executa se o budget estourar | 500 min/mês grátis, depois US$ 0,002/min | **US$ 0,00** |
| Storage do state | Blob LRS Hot, < 1 MB | US$ 0,018/GB | **< US$ 0,01** |
| Saída de dados | Primeiros 100 GB/mês | grátis | **US$ 0,00** |
| Budget, Action Group, NSG, VNet, OIDC | — | sem custo | **US$ 0,00** |
| **Total** | | | **≈ US$ 13,64/mês (≈ R$ 75)** |

- **Custo diário:** ≈ US$ 0,45.
- **Período da GS:** do deploy (17/11) até a correção (~26/11) são ≈ 10 dias, ou **≈ US$ 4,50**. O crédito do Azure for Students é de US$ 100.
- Observabilidade (Prometheus, Grafana, Alertmanager) roda na máquina da equipe: **US$ 0**.
- GitHub Actions e GHCR em repositório público: **US$ 0**.

## Trava de gasto de US$ 20

O **budget** da Azure, sozinho, só envia avisos; ele não bloqueia gastos. O projeto transforma o aviso em ação automática:

```
Budget mensal US$ 20 (rg-passolivre)
 ├─ 50% real      → e-mail para o Owner da assinatura
 ├─ 80% real      → e-mail
 ├─ 100% previsto → e-mail (aviso antecipado)
 └─ 100% real     → e-mail + Action Group → webhook → Runbook "Desalocar-VM-Passo-Livre"
                                                       └─ identidade gerenciada (permissão só na VM)
                                                          POST .../virtualMachines/vm-passolivre/deallocate
```

- **VM desalocada não cobra computação.** Disco e IP continuam (≈ US$ 0,20/dia).
- **Atraso:** os dados de custo chegam ao Cost Management com 8–24 h de atraso. Por isso existem os avisos em 50%, 80% e 100% previsto.
- **Teste:** a trava foi testada chamando o webhook manualmente (ver `docs/evidencias/CHECKLIST.md`).
- **Limite rígido:** a própria assinatura Azure for Students fica desabilitada ao zerar o crédito de US$ 100, **sem cobrar cartão**.

## Práticas FinOps adotadas

| Prática | Como |
|---|---|
| Visibilidade | Tags em todos os recursos: `projeto`, `ambiente`, `dono`, `custo`, `iac` |
| Orçamento e alerta | Budget de US$ 20 com 4 limiares e ação automática |
| Right-sizing | B1s (1 GiB) + swap de 1 GiB; limites de memória por container (128/256 MB); `vm_size` é variável do Terraform |
| Região mais barata | East US 2 em vez de Brazil South (≈ 30–50% mais cara para a mesma VM) |
| Sem recursos ociosos | Sem Load Balancer, NAT Gateway ou banco gerenciado; observabilidade fora da nuvem |
| Ciclo de vida | `terraform destroy` após a correção da GS remove tudo |

## Cenários de evolução

| Cenário | Mudança | Estimativa |
|---|---|---|
| MVP atual | B1s + SQLite | US$ 13,6/mês |
| Mais tráfego | `vm_size = "Standard_B2s"` (2 vCPU, 4 GiB) | ≈ US$ 36/mês |
| Piloto com prefeitura | Container Apps (consumo) + PostgreSQL Flexible B1ms + backup | ≈ US$ 25–40/mês |
| Hospedar IA (Visão/LLM) | VM com 16 GB+ ou GPU | US$ 100+/mês: manter fora até haver receita |

## Custo por relato (indicador de negócio)

Com 1.000 relatos/mês, o custo de infraestrutura fica em US$ 0,014 por relato. Com 10.000 relatos/mês, no mesmo servidor, cai para US$ 0,0014.
