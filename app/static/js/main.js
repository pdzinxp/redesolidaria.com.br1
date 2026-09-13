/**
 * Rede Solidária — JavaScript principal.
 *
 * Por enquanto, este arquivo cuida apenas do menu de navegação em telas
 * pequenas (abrir/fechar o menu mobile). Novas funcionalidades que
 * dependam de JavaScript (mapa, upload de imagens, filtros) serão
 * adicionadas em arquivos próprios nas próximas etapas, para manter
 * este arquivo organizado.
 */

document.addEventListener("DOMContentLoaded", function () {
  const navToggle = document.querySelector("[data-nav-toggle]");
  const navLinks = document.querySelector("[data-nav-links]");

  if (!navToggle || !navLinks) {
    return;
  }

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
});
