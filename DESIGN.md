# DESIGN.md - Warung Modern by MK (situs statis)

Arahan desain untuk `warung modern by mk`. Dibaca bersama skill `antislop` sebagai filter.

## Dial

ENERGY 2 / RHYTHM 3 / MOTION 1

- ENERGY 2: hangat dan ramai seperti warung yang benar-benar buka, bukan halaman kampanye. Barang dan harga yang jadi bintang, bukan slogan.
- RHYTHM 3: komposisi antarbagian sengaja berbeda: hero belah dua dengan stiker miring, deret lima kartu rak yang rata dan sederajat, papan harga bergaris titik, blok nota untuk cara order, baris toko, footer cokelat penuh.
- MOTION 1: hanya hover dan transisi 120ms. Tidak ada animasi muncul saat scroll.

Design read: situs katalog untuk pembeli yang datang dari Instagram dan WhatsApp sebuah warung di Tangerang yang menjual lima rak barang berbeda, dengan bahasa visual stiker bulat milik logonya sendiri (pink, krem kertas, cokelat tinta, garis tebal).

## Kenapa arah ini

Logo klien sudah punya bahasa: stiker bulat bergaris tebal, pink di atas krem, tulisan tangan, gambar tenda dan keranjang. Situs mengikuti bahasa itu, bukan palet baru, supaya logo dan halaman terlihat satu benda. Klien meminta tema "harus mirip logo" dan meminta kategori serta informasi tambahan, bukan sekadar etalase. Karena itu halaman ini punya lima rak, papan harga harian, dan blok cara order.

Yang diambil dari logo hanya tiga hal: warna, garis tebal dua piksel, dan bayangan keras tanpa blur (efek stiker ditempel di kertas). Tidak ada ilustrasi tambahan, tidak ada pola batik buatan, tidak ada emoji.

## Palet

| Token | Nilai | Alasan |
|---|---|---|
| paper | #FFF7ED | krem kertas, dasar seluruh halaman |
| paper-2 | #F6EADB | pemisah bagian tanpa perlu garis |
| card | #FFFFFF | permukaan kartu stiker |
| ink | #5C2E1E | teks utama dan garis tepi, cokelat tinta pada logo |
| muted | #7A5544 | teks penjelas, masih lolos kontras AA di atas paper |
| pink | #EF6BA3 | isian stiker, badge, dan penanda kategori |
| pink-ink | #C22F6E | latar tombol yang memuat teks putih, versi pink yang digelapkan agar lolos AA |
| accent-ink | #A62B5C | teks aksen dan harga, pink yang digelapkan untuk teks di atas krem |
| butter | #FDE6C4 | isian ikon dan label harga |
| leaf | #5E7A3F | penanda "ready stok", hijau yang tidak menyala |
| line | #EBD8C6 | garis rambut pemisah |

Pink asli #EF6BA3 tidak pernah dipakai sebagai latar teks putih dan tidak dipakai untuk teks di atas krem, karena kontrasnya di bawah 4.5:1. Untuk itu ada `pink-ink` dan `accent-ink`. Semua pasangan warna diperiksa di `tools/audit.py`.

## Tipografi

- Judul dan angka harga: Fredoka 600. Huruf ini membulat dan sedikit lucu, sejalan dengan tulisan tangan pada logo, tetapi tetap rapi di ukuran besar.
- Teks isi: Plus Jakarta Sans 400/600. Netral dan nyaman dibaca di HP, sama dengan situs UMKM lain milik user.
- Skala: judul hero clamp(2rem, 5vw, 3.4rem), line-height 1.06. Judul bagian clamp(1.5rem, 2.8vw, 2.1rem). Teks isi 1rem, line-height 1.62. Harga 1.05rem bold.

## Motif identitas

1. Strip tenda: pita bergaris pink dan krem, dipakai sekali di bawah header dan sekali sebelum footer. Ini tenda warung pada logo.
2. Nomor rak: label "RAK 01" sampai "RAK 05" dengan garis rambut di bawahnya, dipakai di kartu rak dan judul halaman katalog per rak.
3. Label harga bergerigi: harga ditulis di kotak butter dengan sudut kanan atas terpotong seperti label harga gantung.

## Aturan yang dipegang

- Semua angka berasal dari poster dan brief klien: harga iPhone, A07, Osmanthus, tang yuan, pisang nagih, minuman 25.000 per cup, roti 16.000 sampai 21.000. Angka yang tidak ada di materi tidak ditampilkan. Tidak ada statistik, jumlah pelanggan, atau testimoni karangan.
- Jumlah follower hanya ditulis untuk akun yang angkanya diberikan klien (Hapeworld 114rb). Akun lain ditulis tanpa angka.
- Barang tanpa foto memakai kotak penanda "foto menyusul", bukan gambar pinjaman dari internet.
- Alamat, jam buka, dan nomor WhatsApp resmi belum dikonfirmasi, jadi ditulis "menyusul" apa adanya. Nomor 0812-5126-8000 dipakai karena itu nomor pengirim brief, dan dicatat di README sebagai hal yang harus dikonfirmasi.
- Tidak ada em dash, tidak ada emoji, tidak ada ikon dekoratif. Ikon kategori digambar sendiri, bentuknya barang yang dijual (HP, lipstik, telur, roti, mangkuk dessert), bukan ikon set bergaya pustaka.
- Tombol berbentuk kotak bersudut 12px dengan garis tinta dua piksel dan bayangan keras, bukan pil. Hanya chip filter yang berbentuk pil karena memang deretan label yang bisa digulir.
- Setiap tautan punya tujuan nyata. Tidak ada tautan ke halaman yang belum dibuat.
- Satu-satunya elemen dengan bayangan lembut adalah tombol WhatsApp melayang di mobile, karena harus terangkat di atas konten yang bergulir.
- Foto produk memakai `loading="lazy"` kecuali logo di hero, yang memakai `fetchpriority="high"`.

## Keadaan yang disiapkan

- Katalog kosong: satu pesan jelas dengan tautan WhatsApp, bukan halaman putih.
- Pencarian tanpa hasil: pesan yang sama, muncul di tempat grid.
- 404: halaman sendiri di `dist/404.html` dengan tautan ke beranda dan katalog.
- Tidak ada keadaan loading karena data ikut di dalam halaman, tanpa permintaan jaringan.
