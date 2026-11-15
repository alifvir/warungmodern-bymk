// Menu mobile. Satu-satunya skrip antarmuka di halaman ini.
(function () {
  var tombol = document.querySelector("[data-menu-tombol]");
  var panel = document.querySelector("[data-menu-panel]");
  if (!tombol || !panel) return;

  function set(buka) {
    panel.setAttribute("data-terbuka", buka ? "true" : "false");
    tombol.setAttribute("aria-expanded", buka ? "true" : "false");
  }

  set(false);

  tombol.addEventListener("click", function () {
    set(panel.getAttribute("data-terbuka") !== "true");
  });

  panel.addEventListener("click", function (e) {
    if (e.target.closest("a")) set(false);
  });

  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && panel.getAttribute("data-terbuka") === "true") {
      set(false);
      tombol.focus();
    }
  });

  document.addEventListener("click", function (e) {
    if (!panel.contains(e.target) && !tombol.contains(e.target)) set(false);
  });

  window.addEventListener("resize", function () {
    if (window.innerWidth >= 920) set(false);
  });
})();
