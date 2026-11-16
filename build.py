"""Build situs statis Warung Modern by MK.

Sumber data:
  data/site.json      identitas toko, nomor WA, cara bayar, daftar toko
  data/katalog.json   lima rak dan barang yang dijual
  assets-src/*.jpg    logo dan poster produk dari klien

Hasil: dist/ siap diunggah ke Cloudflare Pages.

Jalankan: python build.py
"""

import json
import os
import shutil
from datetime import date
from html import escape
from urllib.parse import quote

from PIL import Image

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "assets-src")
DIST = os.path.join(ROOT, "dist")
IMG = os.path.join(DIST, "assets", "img")
CSS = os.path.join(ROOT, "assets", "css")
JS = os.path.join(ROOT, "assets", "js")

SITE = json.load(open(os.path.join(ROOT, "data", "site.json"), encoding="utf-8"))
DATA = json.load(open(os.path.join(ROOT, "data", "katalog.json"), encoding="utf-8"))

KATEGORI = DATA["kategori"]
PRODUK = DATA["produk"]

FONT = (
    "https://fonts.googleapis.com/css2?"
    "family=Fredoka:wght@500;600;700&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap"
)

IKON = {
    "hp": '<rect x="7" y="2.5" width="10" height="19" rx="2.2"/><path d="M10.5 5.5h3"/>',
    "lipstik": '<rect x="7" y="9" width="10" height="12" rx="1.6"/><path d="M9.5 9V4.5h5V9"/><path d="M9.5 15h5"/>',
    "telur": '<path d="M12 3c3.2 3.6 5 7 5 9.6A5 5 0 0 1 7 12.6C7 10 8.8 6.6 12 3Z"/>',
    "roti": '<path d="M3.6 13c1.5-4.4 4-6.8 8.4-6.8S19 8.6 20.4 13"/><path d="M3.6 13h16.8a1.6 1.6 0 0 1 0 3.2H21v2.3H6.2A2.6 2.6 0 0 1 3.6 15V13Z"/>',
    "mangkuk": '<path d="M4.5 11.5h15a7.5 7.5 0 0 1-7.5 7 7.5 7.5 0 0 1-7.5-7Z"/><path d="M9 8.2c0-1.6 1.2-2.9 3-2.9"/><path d="M14.6 4.6a1.3 1.3 0 1 1 2.2 1.2"/>',
    "botol": '<path d="M9.4 7V4.2h5.2V7"/><path d="M7.4 7h9.2l1 12.6H6.4L7.4 7Z"/><path d="M8.6 13.4h6.8"/>',
    "karung": '<path d="M9 4.2h6l2 3.8-2 2.1V20H9v-9.9L7 8z"/><path d="M9 12.2h6"/>',
}


def ikon(nama, kelas="ikon"):
    isi = IKON.get(nama, IKON["roti"])
    return (
        '<svg class="%s" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" '
        'aria-hidden="true" focusable="false">%s</svg>' % (kelas, isi)
    )


def rupiah(n):
    return "Rp%s" % format(n, ",").replace(",", ".")


def wa(pesan=None):
    teks = pesan or SITE["wa_pesan"]
    return "https://wa.me/%s?text=%s" % (SITE["wa"], quote(teks))


def tulis(path, isi):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(isi)


# ---------------------------------------------------------------- gambar

def simpan_webp(sumber, tujuan, lebar, mutu=82):
    im = Image.open(sumber).convert("RGB")
    if im.width > lebar:
        tinggi = round(im.height * lebar / im.width)
        im = im.resize((lebar, tinggi), Image.LANCZOS)
    im.save(tujuan, "WEBP", quality=mutu, method=6)
    return im.width, im.height


def siapkan_gambar():
    os.makedirs(IMG, exist_ok=True)
    ukuran = {}

    lw, lh = simpan_webp(os.path.join(SRC, "logo.jpg"), os.path.join(IMG, "logo.webp"), 360, 88)
    ukuran["logo.webp"] = (lw, lh)
    simpan_webp(os.path.join(SRC, "logo.jpg"), os.path.join(IMG, "logo-88.webp"), 88, 88)

    fav = Image.open(os.path.join(SRC, "logo.jpg")).convert("RGB")
    fav.thumbnail((64, 64), Image.LANCZOS)
    fav.save(os.path.join(DIST, "assets", "favicon.png"), "PNG", optimize=True)

    # Gambar pratinjau tautan. WhatsApp lebih konsisten menampilkan JPEG daripada WebP.
    og = Image.new("RGB", (1200, 630), (255, 247, 237))
    tanda = Image.open(os.path.join(SRC, "logo.jpg")).convert("RGB")
    tanda.thumbnail((470, 470), Image.LANCZOS)
    og.paste(tanda, ((1200 - tanda.width) // 2, (630 - tanda.height) // 2))
    og.save(os.path.join(IMG, "og.jpg"), "JPEG", quality=86, optimize=True, progressive=True)

    for p in PRODUK:
        if not p.get("gambar"):
            continue
        if p["gambar"] in ukuran:
            continue
        berkas = os.path.splitext(p["gambar"])[0] + ".webp"
        ukuran[p["gambar"]] = simpan_webp(
            os.path.join(SRC, p["gambar"]), os.path.join(IMG, berkas), 760, 82
        )
    return ukuran


# ---------------------------------------------------------------- potongan HTML

def kepala(judul, deskripsi, aktif, kanonikal="", skrip_katalog=False):
    url = SITE["url"].rstrip("/")
    kanon = '<link rel="canonical" href="%s%s">' % (url, kanonikal) if url else ""
    nomor_terstruktur = ""
    if url and aktif == "beranda":
        nomor_terstruktur = (
            '<script type="application/ld+json">'
            '{"@context":"https://schema.org","@type":"Store",'
            '"name":"%s %s","url":"%s","telephone":"+%s",'
            '"address":{"@type":"PostalAddress","addressLocality":"%s","addressCountry":"ID"},'
            '"description":"%s"}'
            "</script>"
            % (
                SITE["brand"],
                SITE["brand_akhir"],
                url,
                SITE["wa"],
                SITE["kota"],
                escape(SITE["deskripsi"]),
            )
        )
    skrip = (
        '<script src="/assets/js/katalog.js" defer></script>' if skrip_katalog else ""
    )

    situs = "%s %s" % (SITE["brand"], SITE["brand_akhir"])
    sosial = [
        '<meta property="og:type" content="website">',
        '<meta property="og:site_name" content="%s">' % escape(situs),
        '<meta property="og:locale" content="id_ID">',
        '<meta property="og:title" content="%s">' % escape(judul),
        '<meta property="og:description" content="%s">' % escape(deskripsi),
    ]
    if url:
        sosial.append('<meta property="og:url" content="%s%s">' % (url, kanonikal))
        sosial.append('<meta property="og:image" content="%s/assets/img/og.jpg">' % url)
        sosial.append('<meta property="og:image:width" content="1200">')
        sosial.append('<meta property="og:image:height" content="630">')
        sosial.append(
            '<meta property="og:image:alt" content="Stiker logo %s">' % escape(situs)
        )
        sosial.append('<meta name="twitter:card" content="summary_large_image">')
        sosial.append('<meta name="twitter:title" content="%s">' % escape(judul))
        sosial.append(
            '<meta name="twitter:description" content="%s">' % escape(deskripsi)
        )
        sosial.append('<meta name="twitter:image" content="%s/assets/img/og.jpg">' % url)

    return """<!doctype html>
<html lang="id">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{judul}</title>
<meta name="description" content="{deskripsi}">
<meta name="theme-color" content="#FFF7ED">
<link rel="icon" href="/assets/favicon.png" sizes="64x64">
<link rel="apple-touch-icon" href="/assets/favicon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="{font}" rel="stylesheet">
<link rel="stylesheet" href="/assets/css/style.css">
{kanon}
{sosial}
{gambar_terstruktur}
{skrip}
</head>
<body>
<a class="sr" href="#utama">Lompat ke isi</a>
""".format(
        judul=escape(judul),
        deskripsi=escape(deskripsi),
        font=FONT,
        kanon=kanon,
        sosial="\n".join(sosial),
        gambar_terstruktur=nomor_terstruktur,
        skrip=skrip,
    )


def header(aktif):
    def nav(kunci, href, teks):
        cur = ' aria-current="page"' if aktif == kunci else ""
        return '<a href="%s"%s>%s</a>' % (href, cur, teks)

    menu = "\n".join(
        [
            '<li>%s</li>' % nav("beranda", "/", "Beranda"),
            '<li>%s</li>' % nav("katalog", "/katalog/", "Katalog"),
            '<li><a href="/#cara-order">Cara order</a></li>',
            '<li><a href="/#toko">Toko</a></li>',
            '<li><a href="%s" target="_blank" rel="noopener">WhatsApp %s</a></li>'
            % (wa(), SITE["wa_tampil"]),
        ]
    )

    return """<header class="topbar">
  <div class="wrap">
    <a class="brand" href="/">
      <img src="/assets/img/logo-88.webp" alt="" width="44" height="44" loading="eager">
      <span class="brand-txt"><b>{brand}</b><span>{akhir}</span></span>
    </a>
    <nav class="nav" aria-label="Navigasi utama">
      {nav}
    </nav>
    <a class="tombol" href="{wa}" target="_blank" rel="noopener">Order via WhatsApp</a>
    <button class="menu-btn" type="button" data-menu-tombol aria-expanded="false" aria-controls="menu-mobile">
      <span aria-hidden="true"></span>
      <span class="sr">Buka menu</span>
    </button>
  </div>
  <div class="menu-panel" id="menu-mobile" data-menu-panel>
    <ul>{menu}</ul>
  </div>
</header>
<div class="tenda" aria-hidden="true"></div>
<main id="utama">
""".format(
        brand=escape(SITE["brand"]),
        akhir=escape(SITE["brand_akhir"]),
        nav="\n      ".join(
            [
                nav("beranda", "/", "Beranda"),
                nav("katalog", "/katalog/", "Katalog"),
                '<a href="/#cara-order">Cara order</a>',
                '<a href="/#toko">Toko</a>',
            ]
        ),
        wa=wa(),
        menu=menu,
    )


def ajakan():
    return """<section class="ajakan">
  <div class="wrap">
    <div>
      <h2>Bingung stok atau harga hari ini?</h2>
      <p>Chat saja. Sebut barangnya, kami balas stok, harga, dan cara kirimnya. Tidak perlu bikin akun.</p>
    </div>
    <div class="aksi">
      <a class="tombol" href="{wa}" target="_blank" rel="noopener">Chat WhatsApp</a>
      <a class="tombol kedua" href="/katalog/">Buka katalog</a>
    </div>
  </div>
</section>
""".format(wa=wa())


def footer():
    toko = "\n      ".join(
        '<a href="%s" target="_blank" rel="noopener">%s</a>'
        % (t["tautan"], escape(t["nama"]))
        for t in SITE["toko"]
    )
    kategori = "\n      ".join(
        '<a href="/katalog/%s/">%s</a>' % (k["id"], escape(k["nama"])) for k in KATEGORI
    )
    return """</main>
<div class="tenda bawah" aria-hidden="true"></div>
<footer>
  <div class="wrap">
    <div class="kolom">
      <div>
        <div class="footer-brand">
          <img src="/assets/img/logo-88.webp" alt="" width="40" height="40" loading="lazy">
          <b>{brand} {akhir}</b>
        </div>
        <p>{ringkas}</p>
        <p>WhatsApp {wa_tampil}</p>
      </div>
      <div>
        <h4>Rak</h4>
      {kategori}
      </div>
      <div>
        <h4>Toko di dalamnya</h4>
      {toko}
      </div>
    </div>
    <p class="footer-catatan">Alamat dan jam buka {status}. Harga yang tidak tercantum di halaman ini dikonfirmasi lewat WhatsApp.</p>
  </div>
</footer>
<div class="pita-wa">
  <a href="{wa}" target="_blank" rel="noopener">Chat WhatsApp {wa_tampil}</a>
</div>
<script src="/assets/js/site.js" defer></script>
</body>
</html>
""".format(
        brand=escape(SITE["brand"]),
        akhir=escape(SITE["brand_akhir"]),
        ringkas=escape(
            "Sembako, HP dan aksesoris, kosmetik, roti, dessert dan minuman. Satu nomor untuk semua pesanan."
        ),
        wa_tampil=escape(SITE["wa_tampil"]),
        wa=wa(),
        kategori=kategori,
        toko=toko,
        status=escape(SITE["alamat"].lower()),
    )


def kartu_produk(p, ukuran):
    if p.get("gambar"):
        lebar, tinggi = ukuran.get(p["gambar"], (760, 950))
        badan_foto = (
            '<img src="/assets/img/%s" alt="%s" width="%d" height="%d" loading="lazy" decoding="async">'
            % (os.path.splitext(p["gambar"])[0] + ".webp", escape(p.get("alt", p["nama"])), lebar, tinggi)
        )
    else:
        badan_foto = '<div class="kosong">%s<span>foto menyusul</span></div>' % ikon(
            p.get("ikon", "roti")
        )

    if p.get("badge_teks"):
        label = '<span class="label %s">%s</span>' % (
            p.get("badge", ""),
            escape(p["badge_teks"]),
        )
    else:
        label = ""

    if p.get("harga"):
        satuan = ""
        if p.get("satuan") == "mulai":
            harga = (
                '<span class="angka">Mulai %s</span>' % rupiah(p["harga"])
            )
        else:
            harga = '<span class="angka">%s</span>' % rupiah(p["harga"])
            if p.get("satuan"):
                satuan = '<span class="satuan">%s</span>' % escape(p["satuan"])
        harga = harga + satuan
        if p.get("coret"):
            harga += "<del>%s</del>" % rupiah(p["coret"])
    else:
        harga = '<span class="tanya">%s</span>' % escape(p.get("tanya", "Tanya harga"))

    cari = " ".join(
        [p["nama"], p["brand"], p.get("meta", ""), p.get("kategori_nama", "")]
    ).lower()

    return """<article class="kartu" data-kartu data-cari-teks="{cari}">
  <div class="foto">{label}{foto}</div>
  <div class="isi">
    <div class="asal">{brand}</div>
    <h3>{nama}</h3>
    <div class="meta">{meta}</div>
    <div class="harga">{harga}</div>
    <a class="pesan" href="{tautan}" target="_blank" rel="noopener">{cta}</a>
  </div>
</article>""".format(
        cari=escape(cari),
        label=label,
        foto=badan_foto,
        brand=escape(p["brand"]),
        nama=escape(p["nama"]),
        meta=escape(p.get("meta", "")),
        harga=harga,
        tautan=wa(p["wa"]),
        cta=escape(p.get("cta", "Pesan")),
    )


# ---------------------------------------------------------------- halaman

def halaman_beranda(ukuran):
    rak = "\n".join(
        """    <a class="rak" href="/katalog/{id}/">
      <div class="nomor">{rak}</div>
      {ikon}
      <h3>{nama}</h3>
      <p>{ringkas}</p>
      <div class="rak-brand">{brand}</div>
    </a>""".format(
            id=k["id"],
            rak=k["rak"],
            ikon=ikon(k["ikon"]),
            nama=escape(k["nama"]),
            ringkas=escape(k["ringkas"]),
            brand=escape(k["brand"]),
        )
        for k in KATEGORI
    )

    pilihan = ["osmanthus-qq-bowl", "roti-truffle", "pisang-nagih", "minuman-mangga",
               "iphone-18-pro", "samsung-a07", "implora-lip-cream", "telur-ayam"]
    kartu = "\n".join(
        kartu_produk(next(p for p in PRODUK if p["id"] == pid), ukuran) for pid in pilihan
    )

    bayar = "".join("<span>%s</span>" % escape(b) for b in SITE["bayar"])

    toko = "\n".join(
        """    <a class="toko-item" href="{tautan}" target="_blank" rel="noopener">
      <span class="av" aria-hidden="true">{huruf}</span>
      <span>
        <b>{nama}</b>
        <small>{bidang}</small>
        <em>{label}</em>
      </span>
    </a>""".format(
            tautan=t["tautan"],
            huruf=escape(t["nama"][0]),
            nama=escape(t["nama"]),
            bidang=escape(t["bidang"]),
            label=escape(t["label"]),
        )
        for t in SITE["toko"]
    )

    isi = (
        kepala(
            "%s %s: lima rak dalam satu nomor WhatsApp" % (SITE["brand"], SITE["brand_akhir"]),
            SITE["deskripsi"],
            "beranda",
            "/",
        )
        + header("beranda")
        + """
<section class="hero">
  <div class="wrap">
    <div>
      <p class="kicker">Tangerang, buka tiap hari</p>
      <h1>Lima rak warung, <mark>satu nomor WhatsApp.</mark></h1>
      <p class="lead">Sembako, HP bergaransi, kosmetik, roti, dessert dan minuman. Pilih barangnya di sini, lalu selesaikan pesanan lewat chat. Bisa COD, transfer, debit, sampai cicilan.</p>
      <div class="hero-aksi">
        <a class="tombol" href="{wa}" target="_blank" rel="noopener">Chat WhatsApp</a>
        <a class="tombol kedua" href="/katalog/">Lihat katalog</a>
      </div>
      <div class="catatan-kecil">
        <span>Order lewat WhatsApp</span>
        <span>Cicilan 0% untuk HP</span>
        <span>Kirim seluruh Indonesia</span>
      </div>
    </div>
    <div class="stiker">
      <img src="/assets/img/logo.webp" alt="Stiker logo Warung Modern by MK" width="{lw}" height="{lh}" fetchpriority="high">
      <span class="tempel satu">5 rak</span>
      <span class="tempel dua">Ready stok</span>
    </div>
  </div>
</section>

<section id="rak">
  <div class="wrap">
    <div class="bagian-kepala">
      <h2>Lima rak yang buka hari ini</h2>
      <p>Tiap rak punya toko sendiri yang sudah jalan. Semuanya bisa dipesan dari satu nomor.</p>
    </div>
    <div class="rak-grid">
{rak}
    </div>
  </div>
</section>

<section style="padding-top:8px">
  <div class="wrap">
    <div class="bagian-kepala">
      <h2>Yang paling sering ditanya</h2>
      <p>Contoh isi rak pekan ini. Tekan katalog untuk melihat semuanya.</p>
      <a class="tautan" href="/katalog/">Lihat semua barang</a>
    </div>
    <div class="grid">
{kartu}
    </div>
  </div>
</section>

<section id="cara-order" class="ajakan">
  <div class="wrap">
    <div>
      <h2>Cara order, tanpa bikin akun</h2>
      <p>Semua pesanan lewat WhatsApp. Kami cek stok dulu, baru kirim total dan pilihan bayar.</p>
    </div>
    <div class="aksi">
      <a class="tombol" href="{wa}" target="_blank" rel="noopener">Mulai chat</a>
    </div>
  </div>
</section>

<section>
  <div class="wrap">
    <div class="info-dua">
      <div class="nota">
        <div class="nota-kepala"><b>Alur pesanan</b><span>3 LANGKAH</span></div>
        <ol class="langkah">
          <li><div><b>Sebut barang dan jumlah</b><span>Boleh tanya stok dulu, tidak harus langsung pesan.</span></div></li>
          <li><div><b>Kami kirim total dan pilihan bayar</b><span>Termasuk ongkir kalau dikirim, atau jam ambil kalau diambil sendiri.</span></div></li>
          <li><div><b>Bayar, lalu barang disiapkan</b><span>Dessert dan roti dibuat setelah pesanan masuk supaya masih segar.</span></div></li>
        </ol>
      </div>
      <div>
        <h3>Bayar dan kirim</h3>
        <div class="bayar">{bayar}</div>
        <dl class="daftar-info">
          <div><dt>Cicilan</dt><dd>{cicilan}</dd></div>
          <div><dt>Pengiriman</dt><dd>{kirim}</dd></div>
          <div><dt>Ambil sendiri</dt><dd>Bisa, alamat {alamat}</dd></div>
          <div><dt>Jam buka</dt><dd>{jam}</dd></div>
        </dl>
      </div>
    </div>
  </div>
</section>

<section id="toko" style="padding-top:8px">
  <div class="wrap">
    <div class="bagian-kepala">
      <h2>Toko yang ada di dalamnya</h2>
      <p>Masing-masing punya akun sendiri. Pantau stok dan promo harian di sana.</p>
    </div>
    <div class="toko-list">
{toko}
    </div>
  </div>
</section>
""".format(
            wa=wa(),
            lw=ukuran["logo.webp"][0],
            lh=ukuran["logo.webp"][1],
            rak=rak,
            kartu=kartu,
            bayar=bayar,
            cicilan=escape(SITE["cicilan"]),
            kirim=escape(SITE["kirim"]),
            alamat=escape(SITE["alamat"].lower()),
            jam=escape(SITE["jam"].lower()),
            toko=toko,
        )
        + footer()
    )
    tulis(os.path.join(DIST, "index.html"), isi)


def halaman_katalog(ukuran):
    chip = "\n          ".join(
        '<a class="chip" href="/katalog/%s/">%s</a>' % (k["id"], escape(k["pendek"]))
        for k in KATEGORI
    )
    kartu = "\n".join(kartu_produk(p, ukuran) for p in PRODUK)

    isi = (
        kepala(
            "Katalog Warung Modern by MK",
            "Daftar barang di lima rak Warung Modern by MK: HP dan aksesoris, kosmetik, sembako, roti, dessert dan minuman. Ketik nama barang untuk menyaring.",
            "katalog",
            "/katalog/",
            skrip_katalog=True,
        )
        + header("katalog")
        + """
<section>
  <div class="wrap">
    <div class="kepala-halaman">
      <div class="remah"><a href="/">Beranda</a> / Katalog</div>
      <h1>Semua rak, satu daftar</h1>
      <p>Harga yang belum punya angka berarti masih dikonfirmasi ke pemasok. Tekan tombol di kartu untuk membuka chat dengan pesan yang sudah terisi.</p>
    </div>

    <div class="alat">
      <div class="chip-bar" role="group" aria-label="Pilih rak">
          <a class="chip" href="/katalog/" aria-current="page">Semua</a>
          {chip}
      </div>
      <div class="cari">
        <label class="sr" for="cari">Cari barang</label>
        <input id="cari" type="search" placeholder="Cari: iphone, telur, bolu" autocomplete="off" data-cari>
        <button type="button" data-hapus-cari aria-label="Hapus pencarian">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" aria-hidden="true"><path d="M6 6l12 12M18 6 6 18"/></svg>
        </button>
      </div>
    </div>

    <p class="hitung" data-hitung>{jumlah} barang di rak ini</p>

    <div class="grid" data-grid>
{kartu}
    </div>

    <div class="kosong-grid" data-kosong hidden>
      <b>Tidak ada barang yang cocok</b>
      Coba kata lain, atau chat WhatsApp. Barang yang belum ada di daftar sering masih bisa dipesan.
      <a href="{wa}" target="_blank" rel="noopener">Tanya lewat WhatsApp</a>
    </div>

    <div class="bantuan">
      <span><b>Tanpa akun:</b> semua pesanan lewat WhatsApp</span>
      <span>Stok berubah tiap hari</span>
    </div>
  </div>
</section>
""".format(
            chip=chip,
            kartu=kartu,
            jumlah=len(PRODUK),
            wa=wa(),
        )
        + ajakan()
        + footer()
    )
    tulis(os.path.join(DIST, "katalog", "index.html"), isi)


def halaman_rak(k, ukuran):
    barang = [p for p in PRODUK if p["kat"] == k["id"]]
    chip = "\n          ".join(
        (
            '<a class="chip" href="/katalog/%s/"%s>%s</a>'
            % (x["id"], ' aria-current="page"' if x["id"] == k["id"] else "", escape(x["pendek"]))
        )
        for x in KATEGORI
    )
    kartu = "\n".join(kartu_produk(p, ukuran) for p in barang)

    isi = (
        kepala(
            "%s, %s %s" % (k["nama"], SITE["brand"], SITE["brand_akhir"]),
            "%s %s" % (k["ringkas"], k["keterangan"]),
            "katalog",
            "/katalog/%s/" % k["id"],
            skrip_katalog=True,
        )
        + header("katalog")
        + """
<section>
  <div class="wrap">
    <div class="kepala-halaman">
      <div class="remah"><a href="/">Beranda</a> / <a href="/katalog/">Katalog</a> / {nama}</div>
      <span class="rak-label">{rak} / {brand}</span>
      <h1>{nama}</h1>
      <p>{keterangan}</p>
    </div>

    <div class="alat">
      <div class="chip-bar" role="group" aria-label="Pilih rak">
          <a class="chip" href="/katalog/">Semua</a>
          {chip}
      </div>
      <div class="cari">
        <label class="sr" for="cari">Cari barang di rak ini</label>
        <input id="cari" type="search" placeholder="Cari di rak ini" autocomplete="off" data-cari>
        <button type="button" data-hapus-cari aria-label="Hapus pencarian">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" aria-hidden="true"><path d="M6 6l12 12M18 6 6 18"/></svg>
        </button>
      </div>
    </div>

    <p class="hitung" data-hitung>{jumlah} barang di rak ini</p>

    <div class="grid" data-grid>
{kartu}
    </div>

    <div class="kosong-grid" data-kosong hidden>
      <b>Tidak ada barang yang cocok</b>
      Coba kata lain, atau chat WhatsApp untuk menanyakan barang lain di rak ini.
      <a href="{wa}" target="_blank" rel="noopener">Tanya lewat WhatsApp</a>
    </div>

    <div class="bantuan">
      <span><b>{brand}</b></span>
      <span>Pesan lewat WhatsApp {wa_tampil}</span>
    </div>
  </div>
</section>
""".format(
            nama=escape(k["nama"]),
            rak=k["rak"],
            brand=escape(k["brand"]),
            keterangan=escape(k["keterangan"]),
            chip=chip,
            kartu=kartu,
            jumlah=len(barang),
            wa=wa(),
            wa_tampil=escape(SITE["wa_tampil"]),
        )
        + ajakan()
        + footer()
    )
    tulis(os.path.join(DIST, "katalog", k["id"], "index.html"), isi)


def halaman_404():
    isi = (
        kepala(
            "Halaman tidak ditemukan, Warung Modern by MK",
            "Alamat yang dibuka tidak ada. Kembali ke beranda atau buka katalog Warung Modern by MK.",
            "",
            "/404.html",
        )
        + header("")
        + """
<section class="galat">
  <div class="wrap">
    <div class="kotak">
      <p class="kode">404</p>
      <h1>Alamat ini tidak ada di warung</h1>
      <p>Mungkin tautannya salah ketik, atau halamannya sudah dipindah. Dua tautan di bawah selalu tersedia.</p>
      <div class="aksi">
        <a class="tombol" href="/">Ke beranda</a>
        <a class="tombol kedua" href="/katalog/">Buka katalog</a>
      </div>
    </div>
  </div>
</section>
"""
        + footer()
    )
    tulis(os.path.join(DIST, "404.html"), isi)


def berkas_pendukung():
    url = SITE["url"].rstrip("/")
    halaman = [("/", "1.0"), ("/katalog/", "0.9")] + [
        ("/katalog/%s/" % k["id"], "0.8") for k in KATEGORI
    ]
    if url:
        urls = "\n".join(
            "  <url><loc>%s%s</loc><changefreq>weekly</changefreq><priority>%s</priority></url>"
            % (url, path, pri)
            for path, pri in halaman
        )
        tulis(
            os.path.join(DIST, "sitemap.xml"),
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            "%s\n</urlset>\n" % urls,
        )
        print("sitemap ditulis untuk %s" % url)
    else:
        print("sitemap dilewati: isi data/site.json bagian url setelah situs live")

    baris_sitemap = "\nSitemap: %s/sitemap.xml" % url if url else ""
    tulis(
        os.path.join(DIST, "robots.txt"),
        "User-agent: *\nAllow: /%s\n" % ("\n" + baris_sitemap if baris_sitemap else ""),
    )

    tulis(
        os.path.join(DIST, "_headers"),
        "/assets/*\n  Cache-Control: public, max-age=604800\n"
        "/*\n  Cache-Control: public, max-age=3600\n",
    )


def salin_aset():
    os.makedirs(os.path.join(DIST, "assets", "css"), exist_ok=True)
    os.makedirs(os.path.join(DIST, "assets", "js"), exist_ok=True)
    shutil.copy2(os.path.join(CSS, "style.css"), os.path.join(DIST, "assets", "css", "style.css"))
    for nama in ("site.js", "katalog.js"):
        shutil.copy2(os.path.join(JS, nama), os.path.join(DIST, "assets", "js", nama))


def main():
    if os.path.isdir(DIST):
        shutil.rmtree(DIST)
    os.makedirs(DIST, exist_ok=True)

    salin_aset()
    ukuran = siapkan_gambar()

    halaman_beranda(ukuran)
    halaman_katalog(ukuran)
    for k in KATEGORI:
        halaman_rak(k, ukuran)
    halaman_404()
    berkas_pendukung()

    halaman_total = 2 + len(KATEGORI) + 1
    print("build selesai: %d halaman, tanggal %s" % (halaman_total, date.today().isoformat()))


if __name__ == "__main__":
    main()
