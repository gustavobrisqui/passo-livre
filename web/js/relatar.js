/* Formulário de relato: tipo, local (toque, GPS ou centro do mapa) e descrição opcional. */
"use strict";

(() => {
  const { el, api, avisar, guardarPendente } = PL;
  const form = document.getElementById("form-relato");
  const txtLocal = document.getElementById("local-escolhido");
  const desc = document.getElementById("descricao");
  const btnEnviar = document.getElementById("btn-enviar");
  const mapa = PL.novoMapa("mapa");
  let marcador = null;
  let ponto = null;

  const LIMITES = { lat: [-24.01, -23.35], lon: [-46.83, -46.36] };
  const dentroDeSP = (lat, lon) =>
    lat >= LIMITES.lat[0] && lat <= LIMITES.lat[1] && lon >= LIMITES.lon[0] && lon <= LIMITES.lon[1];

  function escolher(lat, lon, origem) {
    if (!dentroDeSP(lat, lon)) {
      avisar("Esse ponto fica fora do município de São Paulo. Escolha um local dentro da cidade.", "erro");
      return;
    }
    ponto = { lat: Number(lat.toFixed(6)), lon: Number(lon.toFixed(6)) };
    if (marcador) marcador.setLatLng([lat, lon]);
    else marcador = L.marker([lat, lon], { keyboard: false, title: "Local do obstáculo" }).addTo(mapa);
    txtLocal.textContent = `Local escolhido (${origem}): ${ponto.lat}, ${ponto.lon}.`;
  }

  async function carregarTipos() {
    const tipos = await api("/api/tipos");
    const alvo = document.getElementById("opcoes-tipo");
    alvo.replaceChildren(...tipos.map((t, i) =>
      el("label", { class: "opcao" },
        el("input", { type: "radio", name: "tipo", value: t.id, required: i === 0 }),
        t.rotulo)));
  }

  mapa.on("click", (e) => escolher(e.latlng.lat, e.latlng.lng, "toque no mapa"));

  document.getElementById("btn-centro").addEventListener("click", () => {
    const c = mapa.getCenter();
    escolher(c.lat, c.lng, "centro do mapa");
  });

  document.getElementById("btn-gps").addEventListener("click", () => {
    if (!navigator.geolocation) {
      avisar("Seu navegador não permite localização. Toque no mapa para escolher o local.", "aviso");
      return;
    }
    txtLocal.textContent = "Buscando sua localização…";
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        mapa.setView([pos.coords.latitude, pos.coords.longitude], 18);
        escolher(pos.coords.latitude, pos.coords.longitude, "sua localização");
      },
      () => {
        txtLocal.textContent = "Não conseguimos sua localização. Toque no mapa para escolher o local.";
      },
      { enableHighAccuracy: true, timeout: 10000 },
    );
  });

  desc.addEventListener("input", () => {
    document.getElementById("contador").textContent = desc.value.length;
  });

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const tipo = form.querySelector("input[name=tipo]:checked");
    if (!tipo) {
      avisar("Escolha o tipo de obstáculo (passo 1).", "erro");
      form.querySelector("input[name=tipo]").focus();
      return;
    }
    if (!ponto) {
      avisar("Escolha o local do obstáculo no mapa (passo 2).", "erro");
      document.getElementById("btn-gps").focus();
      return;
    }
    const relato = { tipo: tipo.value, descricao: desc.value.trim(), lat: ponto.lat, lon: ponto.lon };
    btnEnviar.disabled = true;
    try {
      const criado = await api("/api/relatos", { method: "POST", body: JSON.stringify(relato) });
      const alvo = document.getElementById("avisos");
      alvo.replaceChildren(el("div", { class: "mensagem ok" },
        "Relato enviado. Obrigado! ",
        el("a", { href: `/#relato-${criado.id}` }, "Ver no mapa")));
      form.reset();
      document.getElementById("contador").textContent = "0";
      ponto = null;
      if (marcador) { mapa.removeLayer(marcador); marcador = null; }
      txtLocal.textContent = "Nenhum local escolhido ainda.";
    } catch (erro) {
      if (!erro.status || erro.status >= 500) {
        guardarPendente(relato);
        avisar("Sem conexão com o servidor. Guardamos seu relato neste aparelho e vamos enviá-lo quando a internet voltar.", "aviso");
      } else {
        avisar(erro.message, "erro");
      }
    } finally {
      btnEnviar.disabled = false;
    }
  });

  carregarTipos().catch(() => avisar("Não foi possível carregar os tipos de obstáculo. Recarregue a página.", "erro"));
})();
