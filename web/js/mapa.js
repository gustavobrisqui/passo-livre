/* Página inicial: mapa + lista acessível dos relatos, filtros e indicadores. */
"use strict";

(() => {
  const { el, api, dataCurta, selo, COR_STATUS, avisar } = PL;
  const mapa = PL.novoMapa("mapa");
  const camada = L.layerGroup().addTo(mapa);
  const marcadores = new Map();
  const lista = document.getElementById("lista");
  const filtros = document.getElementById("filtros");

  async function carregarTipos() {
    const tipos = await api("/api/tipos");
    const sel = document.getElementById("f-tipo");
    tipos.forEach((t) => sel.append(el("option", { value: t.id }, t.rotulo)));
  }

  async function carregarIndicadores() {
    const e = await api("/api/estatisticas");
    const s = e.por_status || {};
    document.getElementById("ind-total").textContent = e.total;
    document.getElementById("ind-abertos").textContent = (s.novo || 0) + (s.em_analise || 0) + (s.encaminhado || 0);
    document.getElementById("ind-resolvidos").textContent = `${s.resolvido || 0} (${e.percentual_resolvidos}%)`;
    document.getElementById("ind-confirmacoes").textContent = e.confirmacoes;
  }

  function conteudoPopup(r) {
    return el("div", {},
      el("strong", {}, r.tipo_rotulo), el("br"),
      selo(r.status), " ",
      r.protocolo ? el("span", { class: "meta" }, `Protocolo ${r.protocolo}`) : null,
      r.descricao ? el("p", {}, r.descricao) : null,
      el("span", { class: "meta" }, `${dataCurta(r.criado_em)} · ${r.confirmacoes} confirmação(ões)`),
    );
  }

  function itemLista(r) {
    const titulo = el("h3", { id: `relato-${r.id}` }, r.tipo_rotulo);
    const btnConfirmar = el("button", {
      type: "button", class: "secundario",
      "aria-label": `Também vi este obstáculo: ${r.tipo_rotulo}`,
      onclick: async (ev) => {
        const botao = ev.currentTarget;
        botao.disabled = true;
        try {
          const atualizado = await api(`/api/relatos/${r.id}/confirmar`, { method: "POST" });
          avisar(`Obrigado! Agora são ${atualizado.confirmacoes} confirmações.`, "ok");
          carregar();
        } catch (e) {
          avisar(e.message, "erro");
          botao.disabled = false;
        }
      },
    }, "👍 Também vi isso");
    const btnMapa = el("button", {
      type: "button", class: "secundario",
      onclick: () => {
        const m = marcadores.get(r.id);
        if (m) { mapa.setView(m.getLatLng(), 17); m.openPopup(); document.getElementById("mapa").focus(); }
      },
    }, "Ver no mapa");
    return el("li", {},
      titulo,
      el("div", {}, selo(r.status), " ",
        r.prioridade ? el("span", { class: "meta" }, `prioridade ${r.prioridade}`) : null, " ",
        r.origem === "robo" ? el("span", { class: "selo robo" }, "🤖 robô") : null, " ",
        r.simulado ? el("span", { class: "selo simulado", title: "Dado de demonstração" }, "simulado") : null),
      r.descricao ? el("p", {}, r.descricao) : null,
      el("p", { class: "meta" },
        `Relatado em ${dataCurta(r.criado_em)} · ${r.confirmacoes} confirmação(ões)`,
        r.protocolo ? ` · Protocolo ${r.protocolo}` : ""),
      el("div", { class: "acoes" }, btnConfirmar, btnMapa),
    );
  }

  async function carregar() {
    const params = new URLSearchParams();
    const dados = new FormData(filtros);
    for (const [k, v] of dados) if (v) params.set(k, v);
    try {
      const relatos = await api(`/api/relatos?${params}`);
      camada.clearLayers();
      marcadores.clear();
      relatos.forEach((r) => {
        const m = L.circleMarker([r.lat, r.lon], {
          radius: 9, weight: 2, color: "#ffffff", fillColor: COR_STATUS[r.status] || "#475467", fillOpacity: 0.95,
        }).bindPopup(conteudoPopup(r)).bindTooltip(r.tipo_rotulo);
        m.addTo(camada);
        marcadores.set(r.id, m);
      });
      lista.replaceChildren(...relatos.map(itemLista));
      if (!relatos.length) lista.append(el("li", {}, "Nenhum relato com esses filtros."));
      document.getElementById("contagem").textContent = `(${relatos.length})`;
      carregarIndicadores();
      const alvo = location.hash.match(/^#relato-(\d+)$/);
      if (alvo && marcadores.get(Number(alvo[1]))) {
        const m = marcadores.get(Number(alvo[1]));
        mapa.setView(m.getLatLng(), 17);
        m.openPopup();
      }
    } catch (e) {
      avisar(`Não foi possível carregar os relatos agora (${e.message}). Verifique sua conexão.`, "erro");
    }
  }

  filtros.addEventListener("change", carregar);
  filtros.addEventListener("submit", (e) => { e.preventDefault(); carregar(); });

  api("/version").then((v) => { document.getElementById("versao").textContent = v.versao; }).catch(() => {});
  carregarTipos().catch(() => {});
  carregar();
})();
