# Warung Modern by MK, situs statis

Situs katalog untuk klien Warung Modern by MK (lima rak: HP, kosmetik, sembako, roti, dessert). Statis, tanpa basis data dan tanpa keranjang. Semua pesanan lewat WhatsApp dengan pesan yang sudah terisi.

Arahan desain ada di `DESIGN.md`. Aturan bangunnya mengikuti skill `antislop` (mode `during`).

## Struktur

```
build.py              generator situs, jalankan dengan python build.py
requirements.txt      Pillow untuk mengubah jpg menjadi webp
DESIGN.md             arah visual, palet, dial, aturan isi
DEPLOY.md             langkah unggah ke Cloudflare Pages
data/site.json        identitas toko, WhatsApp, cara bayar, daftar toko
data/katalog.json     lima rak dan semua barang
assets/css/style.css  seluruh gaya, disalin apa adanya ke dist
assets/js/site.js     menu mobile
assets/js/katalog.js  pencarian di halaman katalog
assets-src/           foto dan poster asli dari klien (tidak ikut ke dist)
tools/audit.py        pemeriksaan hasil build
dist/                 hasil build, ini yang diunggah (tidak di-commit)
```

## Build

```bash
pip install -r requirements.txt
python build.py
python tools/audit.py
```

`build.py` menghapus `dist/` lalu menulis ulang 8 halaman: beranda, katalog, lima halaman rak, dan 404. Foto jpg diubah menjadi webp maksimal 760 piksel, jadi `dist/assets/img` sekitar 1,6 MB untuk 26 gambar.

`tools/audit.py` memeriksa satu h1 per halaman, lang, title, meta description, em dash, tautan mati, aset hilang, alt dan ukuran gambar, tautan kosong, serta 18 pasangan warna teks terhadap ambang kontras WCAG AA 4.5:1. Harus berakhir `masalah: 0`.

## Mengubah isi

- Harga atau barang: ubah `data/katalog.json`, lalu build ulang. Harga kosong (`null`) berarti tampil "Tanya harga" dan tombol langsung membuka chat.
- Nomor WhatsApp, cara bayar, daftar toko: ubah `data/site.json`.
- Warna dan jarak: `assets/css/style.css`. Token warna ada di blok `:root`, dan pasangan barunya perlu ditambahkan ke `PASANGAN` di `tools/audit.py` supaya ikut diperiksa.
- Foto baru: taruh jpg di `assets-src/`, sebut namanya di kolom `gambar` pada `data/katalog.json`.

## Yang sudah pasti dan yang belum

Sudah pasti, berasal dari poster dan brief klien:

- Lima rak, nama brand, dan akun Instagram atau TikTok masing-masing.
- Harga dessert dan minuman: Osmanthus QQ Bowl Rp35.000, Tang Yuan Rp25.000, pisang nagih Rp27.000 per box, minuman Rp25.000 per cup.
- Roti Fuwari Rp16.000 sampai Rp21.000, beef floss Rp16.000.
- Harga dari foto yang dikirim 15 Nov 2026: telur Rp26.000 per kg, Cleo 12.8 liter Rp22.000 per botol, Cleo Smart 220 ml 24 pcs Rp22.000 per pack, camilan Ho Ciek Rp60.000 per pack 100 g.
- Promo Samsung Galaxy A07 4/64 Rp2.099.000 dari Rp2.199.000, vivo V80, nubia A37e, iPhone 18 Pro, Solohour.
- Klaim Hapeworld: original, garansi resmi, cicilan 0% 12 bulan, kirim seluruh Indonesia.

Belum dikonfirmasi, ditulis "menyusul" di halaman:

- Alamat toko dan jam buka.
- Nomor WhatsApp resmi untuk order. Halaman memakai 0812-5126-8000 karena itu nomor pengirim brief.
- Harga gula dan minyak, serta foto bolu dan cookies.
- Harga enam roti baru (pistachio kunafa, chocolate crumble, truffle mushroom, chocolate sous, smoke beef cheese, garlic butter), jadi keenamnya tampil "Tanya harga".
- Metode kirim dan cara hitung ongkir.
- Nama produk makanan pada poster dessert yang harganya Rp29.000 dan Rp30.000.

Jangan menambah testimoni, jumlah pelanggan, atau statistik yang tidak diberikan klien.
