# Pitch: Passo Livre (até 5:00)

**Formato:** vídeo no YouTube como **não listado**, com a equipe aparecendo e conduzindo a apresentação. Legendas recomendadas.
**Demonstração:** o MVP real em https://passolivre-gs.eastus2.cloudapp.azure.com (de preferência no celular, com o espelhamento de tela gravado).
**Critérios (0–10):** problema 1,5 · demo 2,5 · negócio/GTM 2,0 · indicadores 1,5 · viabilidade/pedido 1,0 · clareza 1,5.

> Antes de gravar: confira os números marcados com ⚠️ na fonte original e atualize se necessário.

---

### 0:00–0:30 · O cidadão e o problema (com dado que prove a dor)
**Fala:**
> "Dona Cida tem 72 anos e usa andador. Para pegar o ônibus até o posto de saúde, ela precisa passar por um buraco,
> um carro em cima da calçada e um degrau sem rampa. No Brasil, **18,6 milhões de pessoas têm alguma deficiência**
> ⚠️ (IBGE, PNAD Contínua 2022), e a população idosa cresce a cada censo. Em São Paulo, quem tem mobilidade reduzida
> enfrenta esses obstáculos todos os dias, e não existe um jeito simples de avisar e acompanhar a solução."

**Na tela:** pessoa da equipe falando + foto de calçada obstruída (tirada pela equipe).

### 0:30–1:00 · Solução e proposta de valor
> "O **Passo Livre** é um mapa colaborativo de obstáculos. Em menos de um minuto, **sem cadastro**, qualquer pessoa
> relata o problema. Um robô de automação prioriza e encaminha, e todo mundo acompanha até ser resolvido.
> Para a prefeitura, é um mapa priorizado de onde agir primeiro."

### 1:00–2:30 · Demonstração do MVP funcionando (URL pública)
1. Abrir a URL no celular e mostrar o **cadeado HTTPS** e o endereço.
2. **Mapa + lista:** "A lista existe porque o mapa não é acessível para leitor de tela."
3. **Relatar:** tipo "Degrau sem rampa" → **📍 Usar minha localização** → descrição → **Enviar** → mensagem de sucesso → **Ver no mapa**.
4. **Também vi isso:** confirmar um relato de outra pessoa.
5. **Status mudando:** rodar o bot de RPA do colega (ou mostrar um relato com protocolo) → status "Em análise · protocolo PL-2026-…".
6. **Distritos:** tabela da camada Ouro, ordenar por "Maior tempo de resolução" → "A periferia espera mais."
7. **Como funciona:** 5 segundos mostrando os 7 componentes (robô, visão, IA, dados).
8. (Opcional, 10 s) Grafana com as golden signals: "Monitorado 24 h, com alerta automático."

### 2:30–3:30 · Modelo de negócio e go-to-market
> "Para o cidadão, é **sempre gratuito**. Quem paga é quem precisa decidir onde investir:
> **prefeituras e subprefeituras** contratam o painel de gestão como serviço (B2G);
> **shoppings, concessionárias de transporte e empresas** contratam relatórios de acessibilidade do entorno para ESG (B2B).
> Para chegar até eles: um **piloto em uma subprefeitura**, parceria com **associações de pessoas com deficiência**
> para gerar os primeiros relatos, e programas de inovação aberta do poder público."

**Na tela:** slide simples com as duas colunas B2G / B2B e preços (ver `modelo-de-negocio.md`).

### 3:30–4:15 · Indicadores de negócio e de impacto + ODS
> "Medimos **impacto**: relatos registrados, percentual resolvido e tempo médio até a solução por distrito.
> E medimos **negócio**: contratos ativos, receita recorrente e custo de infraestrutura por relato, que hoje é de
> **centavos**. Contribuímos com os **ODS 10 e 11**, redução das desigualdades e cidades acessíveis
> (metas 11.2 e 11.7), além dos ODS 3 e 9."

**Na tela:** indicadores da página inicial e do Grafana (relatos em 24 h).

### 4:15–5:00 · Viabilidade e pedido
> "O MVP já está no ar, com deploy automático e segurança verificada a cada mudança, por **cerca de US$ 14 por mês** de nuvem.
> Nosso pedido: **um piloto de 90 dias com uma subprefeitura de São Paulo** e **R$ 150 mil** para 12 meses de operação e
> equipe, o suficiente para chegar a 5 subprefeituras pagantes. O Passo Livre devolve autonomia a quem mais precisa.
> Vamos juntos?"

**Na tela:** equipe + URL + QR code do site.

---

## Checklist de gravação
- [ ] Duração ≤ 5:00 (corte o excesso: saber cortar faz parte da nota)
- [ ] A equipe aparece; cada integrante fala em pelo menos um trecho
- [ ] Demonstração **real** na URL pública (nada de slide imitando tela)
- [ ] Legendas (YouTube automático + revisão)
- [ ] Upload como **não listado**; link testado em **aba anônima**
- [ ] Nome completo e RM de todos na mensagem de envio do Teams
- [ ] Antes de gravar: `curl https://passolivre-gs.eastus2.cloudapp.azure.com/healthz` responde `ok`
