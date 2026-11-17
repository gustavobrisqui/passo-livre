/* Passo Livre — utilidades comuns. Nunca usa innerHTML com dados vindos da API (evita XSS). */
"use strict";

const PL = (() => {
  const STATUS = {
    novo: "Novo",
    em_analise: "Em análise",
    encaminhado: "Encaminhado à prefeitura",
    resolvido: "Resolvido",
    duplicado: "Duplicado",
  };
  const COR_STATUS = {
    novo: "#b42318",
    em_analise: "#b54708",
    encaminhado: "#1d4ed8",
    resolvido: "#067647",
    duplicado: "#667085",
  };
  const CHAVE_PENDENTES = "passolivre:pendentes";
  const CENTRO_SP = [-23.5505, -46.6333];

  function el(tag, attrs = {}, ...filhos) {
    const n = document.createElement(tag);
    for (const [k, v] of Object.entries(attrs)) {
      if (v === null || v === undefined || v === false) continue;
      if (k === "class") n.className = v;
      else if (k.startsWith("on")) n.addEventListener(k.slice(2), v);
      else n.setAttribute(k, v === true ? "" : v);
    }
    for (const f of filhos.flat()) {
      if (f === null || f === undefined) continue;
      n.append(f instanceof Node ? f : document.createTextNode(String(f)));
    }
    return n;
  }

  async function api(caminho, opcoes = {}) {
    const resp = await fetch(caminho, {
      headers: { "Content-Type": "application/json", Accept: "application/json" },
      ...opcoes,
    });
    let corpo = null;
    try { corpo = await resp.json(); } catch (_) { /* resposta sem JSON */ }
    if (!resp.ok) {
      const msg = corpo && typeof corpo.detail === "string" ? corpo.detail : `Erro ${resp.status}`;
      const erro = new Error(msg);
      erro.status = resp.status;
      throw erro;
    }
    return corpo;
  }

  function dataCurta(iso) {
    try {
      return new Date(iso).toLocaleDateString("pt-BR", { day: "2-digit", month: "short", year: "numeric" });
    } catch (_) { return iso; }
  }

  function selo(status) {
    return el("span", { class: `selo ${status}` }, STATUS[status] || status);
  }

  /* -------- relatos guardados offline (rede ruim): enviados quando a conexão voltar -------- */
  function lerPendentes() {
    try { return JSON.parse(localStorage.getItem(CHAVE_PENDENTES) || "[]"); } catch (_) { return []; }
  }
  function gravarPendentes(lista) {
    try { localStorage.setItem(CHAVE_PENDENTES, JSON.stringify(lista)); } catch (_) { /* sem storage */ }
  }
  function guardarPendente(relato) {
    const lista = lerPendentes();
    lista.push(relato);
    gravarPendentes(lista);
  }
  async function enviarPendentes() {
    const lista = lerPendentes();
    if (!lista.length || !navigator.onLine) return 0;
    const restantes = [];
    let enviados = 0;
    for (const r of lista) {
      try {
        await api("/api/relatos", { method: "POST", body: JSON.stringify(r) });
        enviados++;
      } catch (e) {
        if (!e.status || e.status >= 500 || e.status === 429) restantes.push(r); // tenta de novo depois
      }
    }
    gravarPendentes(restantes);
    if (enviados) avisar(`${enviados} relato(s) guardado(s) sem conexão foram enviados.`, "ok");
    return enviados;
  }

  function avisar(texto, tipo = "ok") {
    const alvo = document.getElementById("avisos");
    if (!alvo) return;
    alvo.replaceChildren(el("div", { class: `mensagem ${tipo}` }, texto));
  }

  function marcarNavegacao() {
    const atual = location.pathname.replace(/\/$/, "/index.html").split("/").pop() || "index.html";
    document.querySelectorAll("nav a").forEach((a) => {
      if (a.getAttribute("href").replace("/", "") === atual || (atual === "index.html" && a.getAttribute("href") === "/")) {
        a.setAttribute("aria-current", "page");
      }
    });
  }

  function novoMapa(id, opcoes = {}) {
    const mapa = L.map(id, { zoomControl: true, keyboard: true, ...opcoes }).setView(CENTRO_SP, 12);
    L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom: 19,
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
    }).addTo(mapa);
    return mapa;
  }

  window.addEventListener("online", enviarPendentes);
  document.addEventListener("DOMContentLoaded", () => {
    marcarNavegacao();
    enviarPendentes();
  });

  return { STATUS, COR_STATUS, el, api, dataCurta, selo, guardarPendente, enviarPendentes, avisar, novoMapa, CENTRO_SP };
})();
