# 01. Analisis Masalah UMKM, Peran Data, dan Perumusan Pertanyaan Bisnis

**Proyek:** Capstone Project Asah 2026 — Tim A26-CS267 (Karsa)  
**Mitra UMKM:** Kopi Sewu (Kopi dan Burger Sewu) — Tiban, Sekupang, Kota Batam  
**PIC UMKM:** Olivia Esli (Pemilik Usaha)  
**Divisi:** Data Science Specialist (Dwiyan Achmad Assidiqie & Noval Berauh)  
**Status Dokumen:** Deliverable Minggu ke-1 (Main Quest DS #1 & #2)

---

## 1. Pemetaan Masalah Bisnis Kopi Sewu & Peran Data

Berdasarkan hasil wawancara dengan pemilik Kopi Sewu (22 Oktober 2026), operasional usaha menggabungkan **1 outlet tetap** (bersebelahan dengan Vitka Futsal Tiban) dan **armada gerobak kopi keliling** (sebagian bersifat *mangkal* dan sebagian *keliling/muter* di koridor Tiban, Sekupang, dan Batam Centre).

Ketiadaan pencatatan digital yang terintegrasi menimbulkan tiga kelompok masalah utama. Tabel berikut memetakan peran Data Science dalam menjawab masing-masing masalah tersebut:

| No | Masalah Operasional di Lapangan | Dampak Bisnis (Hasil Wawancara) | Peran Data & Analitik (Divisi DS) |
|---|---|---|---|
| **1** | **Blind spot lokasi & jam keramaian armada** — Gerobak sempat mangkal lama di titik yang sedang sepi sementara calon pembeli bingung mencari posisi gerobak aktif. | Kehilangan penjualan (*lost sales*), produktivitas jam kerja rider rendah, penempatan armada tidak berbasis bukti. | Mengukur produktivitas per titik mangkal (omzet/jam, cup/jam), memetakan distribusi *peak hours* berdasarkan tipe zona (kampus, perkantoran/ruang publik, komersial, perumahan) serta perbedaan *weekday* vs *weekend* dan efek cuaca. |
| **2** | **Rekapitulasi manual 1–2 jam per malam & rawan selisih hitung** — Nota kertas, sisa fisik cup, uang tunai, dan mutasi QRIS dicocokkan manual setiap malam. | Waktu pemilik tersita 1–2 jam/malam; sering terjadi selisih antara sisa fisik cup dan transaksi tercatat karena order tunai terlewat saat antrean ramai. | Membangun pipeline *data wrangling* & agregasi otomatis, serta modul **rekonsiliasi shift** yang membandingkan `cup_terpakai_fisik` vs `cup_tercatat_sistem` (memisahkan produk `cup` dari `botol` agar tidak bias) dan `setoran_tunai_fisik` vs `expected_tunai_sistem`. |
| **3** | **Evaluasi performa menu, stok, dan keputusan harian masih mengandalkan intuisi** — Pemilik butuh cara instan mengecek menu terlaris, margin, dan proyeksi kebutuhan cup. | Alokasi stok cup dan bahan baku kurang presisi (berisiko kehabisan di titik ramai atau berlebih di titik sepi). | Menyediakan agregasi ranking menu, estimasi margin kotor (berbasis asumsi HPP), model prediksi permintaan cup harian/per shift (*Side Quest*), serta dataset & ringkasan terstruktur untuk mendukung layanan Asisten Cerdas AI. |

---

## 2. Perumusan Pertanyaan Bisnis Terukur (Business Questions)

Seluruh analisis data di Minggu ke-2 dirancang secara spesifik untuk menjawab **7 pertanyaan bisnis terukur** berikut:

| Kode | Pertanyaan Bisnis | Metrik / KPI Utama | Relevansi ke Fitur MVP & Keputusan UMKM |
|---|---|---|---|
| **BQ-01** | Bagaimana tren omzet, jumlah cup/botol terjual, dan estimasi margin kotor Kopi Sewu secara harian, mingguan, dan bulanan (Agustus–Oktober 2026), serta bagaimana pengaruh *weekday/weekend*, tanggal gajian, dan cuaca hujan? | Total omzet (Rp), total cup, total botol, estimasi margin kotor (Rp & %), *Average Order Value* (AOV), rasio omzet hujan vs cerah. | Menjadi KPI utama dan grafik tren di **Dasbor Pemilik** serta dasar jawaban intent `tanya_omzet_penjualan`. |
| **BQ-02** | Titik lokasi mana di koridor Tiban–Sekupang–Batam Centre yang paling produktif dan titik mana yang paling tidak efisien berdasarkan omzet per jam dan cup per jam? | Omzet per shift, omzet per jam aktif (Rp/jam), cup per jam, total transaksi per lokasi (6 titik). | Dasar rekomendasi alokasi lokasi armada dan visualisasi ranking lokasi di **Dasbor Pemilik**. |
| **BQ-03** | Kapan jam puncak keramaian (*peak hours*) di masing-masing tipe zona lokasi, dan apakah pola tersebut berubah antara hari kerja (*weekday*) dan akhir pekan (*weekend*)? | Distribusi transaksi & cup per jam (07:00–22:00) × tipe zona × *weekday/weekend* (*heatmap*). | Membantu pemilik menentukan jadwal buka-tutup shift dan waktu perpindahan gerobak keliling (*muter*). |
| **BQ-04** | Bagaimana perbandingan performa antar-unit (Outlet Utama vs 4 Gerobak Keliling; mode *mangkal* vs *keliling*), dan apakah teridentifikasi pola *blind spot* (gerobak mangkal di titik sepi)? | Total omzet, rata-rata omzet/jam, jumlah shift efisien vs shift performa rendah per `cart_id`. | Dasar evaluasi kinerja armada dan relokasi gerobak yang terjebak di titik sepi (mis. area kampus saat akhir pekan). |
| **BQ-05** | Menu dan kategori produk apa (Kopi, Non Kopi, Botolan) yang paling laris dan menyumbang omzet serta estimasi margin tertinggi, dan apakah preferensi menu berbeda antar-zona lokasi? | Kuantitas terjual, kontribusi omzet (%), estimasi margin per menu, proporsi kategori per zona lokasi, frekuensi *bulk order*. | Panduan persiapan stok bahan baku per titik mangkal (mis. lebih banyak Non Kopi di kampus, Americano di perkantoran, Botolan di outlet). |
| **BQ-06** | Seberapa sering dan seberapa besar selisih rekonsiliasi antara sisa fisik cup vs transaksi tercatat serta setoran tunai fisik vs catatan sistem, dan faktor apa yang paling memicunya? | Persentase shift berselisih, total cup tak tercatat (`cup_diff`), total selisih kas tunai (`cash_diff`), rasio pembayaran QRIS vs Tunai per zona, korelasi kepadatan jam sibuk dengan selisih. | Memvalidasi manfaat utama digitalisasi pencatatan transaksi (POS cepat) dan mendorong adopsi QRIS di titik dominan tunai. |
| **BQ-07** | *(Side Quest Prediktif)* Dapatkah kita memprediksi kebutuhan jumlah cup harian per unit/lokasi berdasarkan hari, lokasi, mode operasi, cuaca, dan histori penjualan untuk membantu persiapan stok rider? | MAE (*Mean Absolute Error*), RMSE, dan MAPE pada *chronological test split* dibanding baseline rata-rata. | Integrasi rekomendasi target bawaan cup harian ke **Dasbor Pemilik** dan **Asisten AI**. |

---

## 3. Batasan & Kepatuhan Etika Data

1. **Klasifikasi Sumber Data:** Katalog 14 menu, harga jual per satuan, aset gambar produk, dan koordinat Outlet Utama Kopi Sewu (Vitka Futsal Tiban) bersumber dari **data primer UMKM**. Seluruh catatan transaksi historis, jadwal shift, estimasi HPP, 5 titik mangkal sekitar, dan dataset kueri intent merupakan **DATA SINTETIS (DUMMY)** yang dibuat oleh Tim DS karena riwayat transaksi digital UMKM belum tersedia dan laporan laba-rugi asli bersifat rahasia.
2. **Larangan Klaim Palsu:** Seluruh hasil analisis pada tahap capstone disajikan secara transparan sebagai *hasil pengujian prototipe berbasis data sintetis*, bukan laporan keuangan atau klaim kinerja riil Kopi Sewu.
3. **Privasi:** Dataset tidak mengandung nama asli pelanggan, nomor telepon, rekening bank, maupun data kredensial pihak mana pun. Nama staf gerobak menggunakan alias (`Staf Outlet`, `Rider A`–`Rider D`).
