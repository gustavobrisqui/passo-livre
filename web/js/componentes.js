/* "Como funciona": mostra os links reais (repositório e vídeo) de cada componente da equipe.
   Os links vêm de /dados/componentes.json; campos vazios não aparecem. */
"use strict";

(() => {
  const { el, api } = PL;
  const ROTULOS = { repositorio: "Repositório no GitHub", video: "Vídeo de demonstração" };
  const ehHttps = (u) => typeof u === "string" && /^https:\/\/[^\s"'<>]+$/.test(u);

  api("/dados/componentes.json")
    .then((dados) => {
      document.querySelectorAll("[data-componente]").forEach((alvo) => {
        const links = dados[alvo.dataset.componente] || {};
        const itens = Object.entries(ROTULOS)
          .filter(([chave]) => ehHttps(links[chave]))
          .map(([chave, rotulo]) =>
            el("a", { class: "botao secundario", href: links[chave], target: "_blank", rel: "noopener noreferrer" },
              `${rotulo} ↗`));
        if (itens.length) alvo.replaceChildren(el("span", { class: "acoes" }, ...itens));
      });
    })
    .catch(() => { /* sem o arquivo, a página continua só com as descrições */ });
})();
