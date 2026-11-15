// Pencarian di halaman katalog. Kartu sudah ada di HTML, jadi halaman tetap
// terbaca tanpa JavaScript. Skrip ini hanya menyaring kartu yang sudah ada.
(function () {
  var grid = document.querySelector("[data-grid]");
  var input = document.querySelector("[data-cari]");
  if (!grid || !input) return;

  var kartu = [].slice.call(grid.querySelectorAll("[data-kartu]"));
  var hitung = document.querySelector("[data-hitung]");
  var kosong = document.querySelector("[data-kosong]");
  var tombolHapus = document.querySelector("[data-hapus-cari]");

  function normal(teks) {
    return teks.toLowerCase().replace(/\s+/g, " ").trim();
  }

  function jalankan() {
    var q = normal(input.value);
    var tampil = 0;

    kartu.forEach(function (k) {
      var cocok = !q || normal(k.getAttribute("data-cari-teks") || "").indexOf(q) > -1;
      k.hidden = !cocok;
      if (cocok) tampil += 1;
    });

    if (hitung) {
      hitung.textContent = q
        ? tampil + " barang cocok dengan \u201c" + input.value.trim() + "\u201d"
        : kartu.length + " barang di rak ini";
    }
    if (kosong) kosong.hidden = tampil !== 0;
    grid.hidden = tampil === 0;
  }

  input.addEventListener("input", jalankan);
  if (tombolHapus) {
    tombolHapus.addEventListener("click", function () {
      input.value = "";
      jalankan();
      input.focus();
    });
  }
  jalankan();
})();
