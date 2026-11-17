/* Tela de distritos: lê o export da camada Ouro (web/dados/ouro.json). */
"use strict";

(() => {
  const { el, api, avisar } = PL;
  const corpo = document.getElementById("corpo");
  const ordenar = document.getElementById("ordenar");
  let dados = null;
  let rotulos = {};

  function pendentes(d) { return d.total_ocorrencias - d.resolvidas; }

  function desenhar() {
    const campo = ordenar.value;
    const valor = (d) => (campo === "pendentes" ? pendentes(d) : d[campo]);
    const linhas = [...dados.distritos].sort((a, b) => valor(b) - valor(a));
    const maximo = Math.max(...linhas.map((d) => d.total_ocorrencias), 1);
    corpo.replaceChildren(...linhas.map((d) => {
      const barra = el("div", { class: "barra", role: "presentation" });
      barra.style.width = `${Math.round((100 * d.total_ocorrencias) / maximo)}%`;
      const pct = d.total_ocorrencias ? Math.round((100 * d.resolvidas) / d.total_ocorrencias) : 0;
      return el("tr", {},
        el("th", { scope: "row" }, d.distrito, el("br"), el("span", { class: "meta" }, d.subprefeitura)),
        el("td", {}, d.total_ocorrencias),
        el("td", { class: "coluna-barra" }, barra),
        el("td", {}, `${d.resolvidas} (${pct}%)`),
        el("td", {}, d.tempo_medio_resolucao_dias),
        el("td", {}, d.pontos_onibus_afetados),
        el("td", {}, rotulos[d.tipo_mais_comum] || d.tipo_mais_comum));
    }));
  }

  async function iniciar() {
    try {
      const [ouro, tipos] = await Promise.all([api("/dados/ouro.json"), api("/api/tipos").catch(() => [])]);
      dados = ouro;
      rotulos = Object.fromEntries(tipos.map((t) => [t.id, t.rotulo]));
      const m = ouro.metadados || {};
      document.getElementById("fonte").textContent =
        `Fonte: ${m.fonte || "camada Ouro"} · Tabela: ${m.tabela_origem || "-"} · Atualizado em ${m.atualizado_em || "-"}.`;
      desenhar();
    } catch (e) {
      avisar("Os indicadores por distrito ainda não estão disponíveis.", "aviso");
    }
  }

  ordenar.addEventListener("change", desenhar);
  iniciar();
})();
