# Deploy Warung Modern by MK

Pola sama dengan `djamoe-damar-web` dan `perfect-flowers-web`: repo dulu, Cloudflare Pages belakangan. Proyek Pages yang dibuat lewat Upload assets tidak bisa dihubungkan ke GitHub setelahnya.

## Sebelum deploy

1. Konfirmasi ke klien atau PIC: alamat toko, jam buka, nomor WhatsApp resmi, harga sembako, dan foto produk yang masih kosong. Daftarnya ada di README bagian "Yang sudah pasti dan yang belum".
2. Ganti `wa` dan `wa_tampil` di `data/site.json` kalau nomor resminya berbeda dari 0812-5126-8000.
3. Build bersih:

```bash
pip install -r requirements.txt
python build.py
python tools/audit.py
```

`tools/audit.py` harus berakhir `masalah: 0` dan `dist/` berisi 8 halaman HTML.

## Repo

1. Repo sudah ada: `https://github.com/alifvir/warungmodern-bymk` (publik, satu klien satu repo).
2. Push seluruh isi proyek, termasuk `assets-src/` dan `data/`. Jangan push `dist/`, karena sudah ada di `.gitignore` dan dibangun ulang oleh Cloudflare. `mockup/`, `kirim/`, `baru/`, dan media mentah WhatsApp juga diabaikan.

## Cloudflare Pages

1. Cloudflare Dashboard, Workers and Pages, Create, Pages, Connect to Git, pilih repo tersebut.
2. Setelan build:
   - Framework preset: None
   - Build command: `pip install -r requirements.txt && python build.py`
   - Build output directory: `dist`
   - Root directory: kosong
3. Deploy. Nama proyek menentukan subdomain, jadi putuskan sebelum klik pertama. Usulan: `warungmodern-bymk` sehingga alamatnya `https://warungmodern-bymk.pages.dev`.

## Setelah live

1. Isi `url` di `data/site.json` dengan alamat live tanpa garis miring di akhir.
2. Build ulang, commit, push. Dengan `url` terisi, `sitemap.xml` ikut dibuat, `robots.txt` memuat baris Sitemap, dan canonical plus JSON-LD toko muncul di beranda.
3. Uji alamat produksi:

```bash
for p in / /katalog/ /katalog/hp/ /katalog/dessert/ /404.html /assets/css/style.css /assets/img/logo.webp /robots.txt /sitemap.xml; do
  printf "%s " "$p"; curl -s -o /dev/null -w "%{http_code}\n" "https://umkm-warung-modern.pages.dev$p"
done
curl -s -o /dev/null -w "%{http_code}\n" "https://umkm-warung-modern.pages.dev/halaman-ngawur"
```

Semua harus 200, kecuali path ngawur yang harus 404 dengan halaman sendiri.

4. Cek di HP: tombol WhatsApp membuka aplikasi dengan pesan yang sudah terisi, menu mobile bisa dibuka dan ditutup, dan tidak ada halaman yang bisa digeser ke samping.

## Update harga atau barang

1. Ubah `data/katalog.json` atau `data/site.json`.
2. `python build.py`
3. `git add -A && git commit -m "Update harga" && git push`
4. Cloudflare membangun ulang otomatis.

Harga tidak berubah sendiri di halaman terbit: harus lewat build dan push.

## Domain sendiri

Tambah domain di Cloudflare Pages, Custom domains. Setelah aktif, ganti `url` di `data/site.json`, build ulang, push. Canonical, sitemap, dan JSON-LD ikut menyesuaikan.

## Catatan file `_headers`

`dist/_headers` mengatur cache aset 7 hari dan HTML 1 jam. Kalau nanti gambar diganti dengan nama file yang sama, naikkan versi dengan mengubah nama berkas supaya cache lama tidak dipakai.
