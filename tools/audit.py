"""Pemeriksaan hasil build: tautan, judul, alt, em dash, kontras, ukuran aset.

Jalankan setelah build: python tools/audit.py
"""

import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST = os.path.join(ROOT, "dist")

masalah = []

# Pasangan warna dari assets/css/style.css yang dipakai untuk teks.
PASANGAN = [
    ("ink di paper", "#5C2E1E", "#FFF7ED"),
    ("ink di kartu", "#5C2E1E", "#FFFFFF"),
    ("muted di paper", "#7A5544", "#FFF7ED"),
    ("muted di kartu", "#7A5544", "#FFFFFF"),
    ("muted di paper-2", "#7A5544", "#F6EADB"),
    ("accent-ink di paper", "#A62B5C", "#FFF7ED"),
    ("accent-ink di kartu", "#A62B5C", "#FFFFFF"),
    ("accent-ink di paper-2", "#A62B5C", "#F6EADB"),
    ("putih di pink-ink", "#FFFFFF", "#C22F6E"),
    ("putih di tombol kedua? tidak, ink di kartu", "#5C2E1E", "#FFFFFF"),
    ("ink di butter", "#5C2E1E", "#FDE6C4"),
    ("putih di leaf", "#FFFFFF", "#5E7A3F"),
    ("putih di accent-ink", "#FFFFFF", "#A62B5C"),
    ("teks footer di ink", "#F3E2D5", "#5C2E1E"),
    ("tautan footer di ink", "#E7CFC0", "#5C2E1E"),
    ("catatan footer di ink", "#CFB2A2", "#5C2E1E"),
    ("placeholder input di kartu", "#7A5544", "#FFFFFF"),
    ("harga coret di kartu", "#7A5544", "#FFFFFF"),
]


def kanal(c):
    c = c / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def luminans(hex_warna):
    h = hex_warna.lstrip("#")
    r, g, b = (int(h[i : i + 2], 16) for i in (0, 2, 4))
    return 0.2126 * kanal(r) + 0.7152 * kanal(g) + 0.0722 * kanal(b)


def kontras(a, b):
    la, lb = luminans(a), luminans(b)
    terang, gelap = max(la, lb), min(la, lb)
    return (terang + 0.05) / (gelap + 0.05)


for nama, depan, belakang in PASANGAN:
    rasio = kontras(depan, belakang)
    if rasio < 4.5:
        masalah.append("kontras %s: %.2f:1 (minimal 4.5:1)" % (nama, rasio))

halaman = []
for akar, _dirs, berkas in os.walk(DIST):
    for b in berkas:
        if b.endswith(".html"):
            halaman.append(os.path.join(akar, b))


def rel(p):
    return os.path.relpath(p, DIST).replace("\\", "/")


for p in sorted(halaman):
    html = open(p, encoding="utf-8").read()
    nama = rel(p)

    if len(re.findall(r"<h1[ >]", html)) != 1:
        masalah.append("%s: jumlah h1 = %d" % (nama, len(re.findall(r"<h1[ >]", html))))
    if 'lang="id"' not in html:
        masalah.append("%s: tidak ada lang=id" % nama)
    if "<title>" not in html or re.search(r"<title>\s*</title>", html):
        masalah.append("%s: title kosong" % nama)
    if 'name="description"' not in html or 'content=""' in html:
        masalah.append("%s: meta description kosong" % nama)
    if "\u2014" in html:
        masalah.append("%s: ada em dash" % nama)
    if "user-scalable=no" in html or "maximum-scale=1" in html:
        masalah.append("%s: viewport memblokir zoom" % nama)
    for wajib in ("<header", "<nav", "<main", "<footer"):
        if wajib not in html:
            masalah.append("%s: landmark %s tidak ada" % (nama, wajib))

    for href in re.findall(r'href="(/[^"#?]*)"', html):
        target = os.path.join(DIST, href.lstrip("/"))
        if href.endswith("/"):
            target = os.path.join(target, "index.html")
        if not os.path.exists(target):
            masalah.append("%s: tautan mati %s" % (nama, href))

    for aset in re.findall(r'(?:href|src)="(/assets/[^"]+)"', html):
        if not os.path.exists(os.path.join(DIST, aset.lstrip("/"))):
            masalah.append("%s: aset hilang %s" % (nama, aset))

    for tag in re.findall(r"<img [^>]*>", html):
        if 'alt="' not in tag:
            masalah.append("%s: img tanpa alt" % nama)
        if "width=" not in tag or "height=" not in tag:
            masalah.append("%s: img tanpa width/height" % nama)
        if "fetchpriority" not in tag and "loading=" not in tag:
            masalah.append("%s: img tanpa strategi muat" % nama)

    for tag in re.findall(r"<a [^>]*>", html):
        if 'href="#"' in tag or "href=''" in tag:
            masalah.append("%s: tautan kosong" % nama)

    if "<h1" in html and "<h1" in html.split("</h1>")[1]:
        pass
    if html.count("<main") != 1:
        masalah.append("%s: jumlah main = %d" % (nama, html.count("<main")))

teks_sumber = []
for akar, _dirs, berkas in os.walk(DIST):
    for b in berkas:
        if b.endswith((".css", ".js")):
            teks_sumber.append(os.path.join(akar, b))

for p in teks_sumber:
    isi = open(p, encoding="utf-8").read()
    if "\u2014" in isi:
        masalah.append("%s: ada em dash" % rel(p))

ukuran = Counter()
for akar, _dirs, berkas in os.walk(DIST):
    for b in berkas:
        ext = os.path.splitext(b)[1].lower() or "(tanpa ekstensi)"
        ukuran[ext] += os.path.getsize(os.path.join(akar, b))

print("halaman diperiksa:", len(halaman))
for ext, total in ukuran.most_common():
    print("  %-8s %7.1f KB" % (ext, total / 1024))
print("masalah:", len(masalah))
for m in masalah:
    print("  -", m)
sys.exit(1 if masalah else 0)
