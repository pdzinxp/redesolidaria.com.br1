/**
 * Rede Solidária — JavaScript principal.
 *
 * Por enquanto, este arquivo cuida apenas do menu de navegação em telas
 * pequenas (abrir/fechar o menu mobile). Novas funcionalidades que
 * dependam de JavaScript (mapa, upload de imagens, filtros) serão
 * adicionadas em arquivos próprios nas próximas etapas, para manter
 * este arquivo organizado.
 */

/**
 * Rede Solidária — JavaScript principal.
 *
 * Cuida do menu de navegação em telas pequenas e das setas do carrossel
 * de instituições em destaque. A rolagem em si (arrastar com o mouse ou
 * o dedo) já funciona sem nenhum JavaScript, só com CSS
 * (scroll-snap + overflow-x) — as setas aqui são apenas um atalho a mais
 * para quem está usando mouse/teclado.
 */

document.addEventListener("DOMContentLoaded", function () {
  const navToggle = document.querySelector("[data-nav-toggle]");
  const navLinks = document.querySelector("[data-nav-links]");

  if (navToggle && navLinks) {
    navToggle.addEventListener("click", function () {
      const isOpen = navLinks.classList.toggle("is-open");
      navToggle.setAttribute("aria-expanded", isOpen ? "true" : "false");
    });

    // Fecha o menu automaticamente ao clicar em um link (útil no celular)
    navLinks.querySelectorAll("a").forEach(function (link) {
      link.addEventListener("click", function () {
        navLinks.classList.remove("is-open");
        navToggle.setAttribute("aria-expanded", "false");
      });
    });
  }

  // ---------- Carrossel de instituições em destaque ----------
  document.querySelectorAll("[data-carousel-track]").forEach(function (track) {
    const wrapper = track.closest(".carousel");
    if (!wrapper) return;

    const prevBtn = wrapper.querySelector("[data-carousel-prev]");
    const nextBtn = wrapper.querySelector("[data-carousel-next]");
    if (!prevBtn || !nextBtn) return;

    // Quanto rolar a cada clique: a largura de um card + o espaçamento
    // entre eles, para sempre parar alinhado no próximo card.
    function stepSize() {
      const card = track.querySelector(".institution-card");
      if (!card) return track.clientWidth;
      const trackStyle = window.getComputedStyle(track);
      const gap = parseFloat(trackStyle.columnGap || trackStyle.gap || "0") || 0;
      return card.getBoundingClientRect().width + gap;
    }

    // Habilita/desabilita as setas nas pontas (não tem pra onde rolar
    // mais à esquerda, ou já chegou no fim da lista à direita).
    function updateArrows() {
      const maxScroll = track.scrollWidth - track.clientWidth;
      prevBtn.disabled = track.scrollLeft <= 4;
      nextBtn.disabled = maxScroll <= 4 || track.scrollLeft >= maxScroll - 4;
    }

    prevBtn.addEventListener("click", function () {
      track.scrollBy({ left: -stepSize(), behavior: "smooth" });
    });

    nextBtn.addEventListener("click", function () {
      track.scrollBy({ left: stepSize(), behavior: "smooth" });
    });

    track.addEventListener("scroll", updateArrows);
    window.addEventListener("resize", updateArrows);
    updateArrows();
  });
});
