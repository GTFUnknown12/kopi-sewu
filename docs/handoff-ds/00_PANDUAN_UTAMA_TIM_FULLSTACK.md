# 00. Panduan Utama Integrasi — Divisi Data Science → Tim Full-Stack (FS)

**Proyek:** Capstone Project Asah 2026 — Tim A26-CS267 (**Karsa**)  
**Mitra UMKM:** Kopi Sewu *(Kopi dan Burger Sewu)* — Tiban, Sekupang, Kota Batam  
**Penerima:** Grivin William Revel & Adlan Hanif Abdillah (*AI Full-Stack Developer*)  
**Pengirim:** Dwiyan Achmad Assidiqie & Noval Berauh (*Data Science Specialist*)

---

## 1. Isi Lengkap Paket ZIP Ini

| Folder / File | Kegunaan bagi Tim Full-Stack |
|---|---|
| `00_PANDUAN_UTAMA_TIM_FULLSTACK.md` | **Baca dokumen ini terlebih dahulu** — ringkasan alur integrasi, aturan bisnis wajib, & angka validasi. |
| `database/schema_postgresql_reference.sql` | Skema lengkap tabel PostgreSQL (`locations`, `carts`, `menu`, `shifts`, `transactions`, `ai_chat_logs`) + constraint + index untuk Supabase/Neon. |
| `database/seed_postgresql.sql` | Perintah `\copy` siap pakai sesuai urutan Foreign Key (`01` → `05`). |
| `database/db_seed/01_locations.csv` s.d. `05_transactions.csv` | 5 file CSV bersih yang kolomnya sudah disesuaikan **1:1** untuk import PostgreSQL (6 lokasi, 5 armada, 14 menu primer Kopi Sewu + link foto Drive, 602 shift, 19.886 transaksi). |
| `api_dashboard_json/*.json` | **6 file JSON tervalidasi ketat (bebas `NaN`)** siap dipakai sebagai *mock payload* Frontend atau referensi format respon endpoint Express (`/api/v1/dashboard/...`). |
| `api_dashboard_json/handoff_manifest.json` | Angka acuan resmi hasil *cross-check* DS untuk memverifikasi ketepatan tampilan dasbor. |
| `docs/` | Dokumen lengkap pertanyaan bisnis, ERD & Kamus Data (`02_kamus_data.md`), kontrak API & validasi (`04_kontrak_data_dan_handoff_fs_ae.md`), dan panduan dasbor Streamlit. |
| `reference_streamlit_dashboard/` | Referensi visual 5 tab (`app.py`) dan palet warna Kopi Sewu (`config.toml`: `#6F4E37`, `#F7F3EE`, `#1F1A17`). |

---

## 2. Langkah Cepat Integrasi (Urutan Kerja 1 → 4)

### Langkah 1 — Setup & Seeding Database PostgreSQL (Supabase / Neon)
1. Jalankan `database/schema_postgresql_reference.sql` pada instance PostgreSQL.
2. Impor 5 file CSV di `database/db_seed/` **secara berurutan** (`01_locations` → `02_carts` → `03_menu` → `04_shifts` → `05_transactions`) menggunakan `database/seed_postgresql.sql` atau fitur CSV Import Supabase.
3. **Catatan Penting Import CSV:**
   - Pada `03_menu.csv`, kolom `estimated_margin` **sengaja tidak disertakan** karena di PostgreSQL didefinisikan sebagai `GENERATED ALWAYS AS (price - hpp_asumsi) STORED` (otomatis terisi oleh DB).
   - Pada `04_shifts.csv`, terdapat **15 baris dengan `cup_sisa` kosong (`""`)** — pastikan import memetakan string kosong menjadi SQL `NULL` (jangan diubah jadi `0`!).
   - Pada tabel `carts`, 3 kolom *live-tracking* (`is_active`, `current_location_id`, `last_updated_at`) memakai nilai default dan dikelola dinamis oleh Backend Express saat staf mengaktifkan/menonaktifkan status mangkal.

### Langkah 2 — Bangun Endpoint REST API Express.js (`/api/v1/...`) & Validasi Joi/Zod
Gunakan format respon yang persis sama dengan 6 file di `api_dashboard_json/`:

| Endpoint Backend Express | File Referensi JSON di Paket Ini | Fungsi Frontend |
|---|---|---|
| `GET /api/v1/dashboard/summary` | `dashboard_summary.json` | 6 KPI Cards, Line Chart Tren Harian (+ MA7 & hari hujan), Bar Bulanan |
| `GET /api/v1/dashboard/locations-and-carts` | `locations_and_carts.json` | Peta Leaflet.js 6 titik, Ranking Lokasi (*Weekday vs Weekend*), Perbandingan 5 Armada |
| `GET /api/v1/dashboard/peak-hours` | `peak_hours.json` | Heatmap Jam Ramai (`Lokasi × Jam 07:00–21:00`) & Top-3 Peak Hours |
| `GET /api/v1/dashboard/top-menus` | `top_menus.json` | Ranking 14 Menu Asli (termasuk foto Google Drive), Ringkasan Kategori, Mix per Lokasi |
| `GET /api/v1/dashboard/reconciliation` | `reconciliation.json` | Ringkasan Status Rekonsiliasi, Adopsi QRIS per Lokasi, Tabel Detail 602 Shift |
| `GET /api/v1/dashboard/forecast` | `demand_forecast.json` | *(Nilai Tambah)* Proyeksi Stok Cup 7 Hari & 66 Skenario Lookup dari Model ML DS |

### Langkah 3 — Hubungkan Modul Staf, Peta Publik, & Chat AI (Via Backend!)
- **Peta Publik Pelanggan (Tanpa Login):** Endpoint publik `GET /api/v1/carts/active` menampilkan armada yang berstatus `is_active = TRUE` menggunakan koordinat `locations` (pusat peta Batam: lat `1.118`, lon `104.005`, zoom `11–12`; Outlet Utama Kopi Sewu di Vitka Futsal Tiban: `1.111124, 103.978107`). Jika semua gerobak nonaktif, tampilkan informasi *"Saat ini belum ada gerobak aktif beroperasi"* dengan rapi.
- **Form POS & Lokasi Staf (Mobile-Responsive):** Buat tombol *quick-click preset* untuk 14 menu (bisa tampilkan foto dari `image_gdrive_url`), tombol toggle **Mulai Jualan / Selesai Shift**, serta loading/success/error state yang jelas.
- **Integrasi Chat AI (Side Quest FS Wajib Via Backend):** Frontend memanggil `POST /api/v1/ai/chat` pada Express → Express meneruskan ke layanan FastAPI Tim AE (`POST /chat`) → Express menyimpan log percakapan ke tabel `ai_chat_logs` (termasuk `predicted_intent`, `intent_confidence`, `is_out_of_context`, `fallback_used`). **Dilarang** memanggil API AI/Gemini langsung dari Frontend!

### Langkah 4 — Verifikasi Angka Dasbor (*Sanity Check* Wajib)
Begitu database ter-seed dan dasbor pemilik aktif untuk periode penuh **1 Agustus – 31 Oktober 2026**, pastikan angka yang tampil di UI **cocok 100%** dengan acuan berikut:
- **Total Omzet:** `Rp 537.951.000` | **Estimasi Margin Kotor:** `Rp 290.507.900 (54,0%)`
- **Total Volume:** `29.443 cup` + `744 botol` | **Total Transaksi:** `19.886` | **AOV:** `Rp 27.052`
- **Proporsi Pembayaran (diketahui):** `QRIS 57,1%` vs `Tunai 42,9%` *(198 transaksi historis berlabel `Tidak Diketahui`)*
- **Total Shift:** `602 shift` → Status Rekonsiliasi: **418 Cocok**, **94 Perlu Cek**, **75 Selisih Tinggi**, **15 Data Tidak Lengkap** (`cup_sisa` kosong); total akumulasi selisih cup **183 cup**.

---

## 3. Aturan Bisnis & Validasi Ketat (Agar Tidak Melenceng dari DS!)

1. **ATURAN REKONSILIASI `cup` vs `botol` (SANGAT PENTING!):**  
   Katalog Kopi Sewu memiliki 12 menu bersatuan `cup` (`Kopi`, `Non Kopi`) dan 2 menu bersatuan `botol` (`Botolan 1 Liter`, `Botolan 250 ml`). Saat menghitung `cup_tercatat_sistem` untuk dicocokkan dengan `cup_dibawa - cup_sisa`, **WAJIB filter `WHERE unit_type = 'cup'`**. Penjualan `botol` tetap masuk omzet & setoran tunai/QRIS, tetapi **tidak mengurangi stok cup**!
2. **ATURAN `cup_sisa IS NULL`:**  
   Jika `cup_sisa` belum diisi / `NULL`, tampilkan status `data_tidak_lengkap` — **JANGAN** diubah jadi `0` karena akan memunculkan selisih cup palsu.
3. **ATURAN VALIDASI INPUT JOI/ZOD PADA FORM STAF:**
   - `menu_id` dipilih dari tabel `menu`; **`unit_price`, `category`, `unit_type`, `total_price`, dan `hpp_asumsi_total` WAJIB dihitung di Backend Express**, bukan diketik manual dari Frontend!
   - `qty`: integer wajib `>= 1` dan `<= 100` (otomatis set `order_type = 'bulk_order'` jika `qty >= 15`).
   - `payment_method`: enum ketat wajib `'Tunai'` atau `'QRIS'` (**tidak boleh kosong/null** — hasil EDA DS membuktikan 198 transaksi tanpa metode bayar memicu selisih kas semu Rp 5,46 juta!).
   - `location_id`: wajib dipilih saat mengubah status gerobak menjadi `aktif`.
   - Saat tutup shift: `cup_sisa` wajib integer `0 <= cup_sisa <= cup_dibawa` dan `end_time > start_time`.
4. **ATURAN STATUS REKONSILIASI SHIFT:**
   - `data_tidak_lengkap`: jika `cup_sisa IS NULL`
   - `selisih_tinggi`: jika `ABS(selisih_cup) >= 3` atau `ABS(selisih_tunai_idr) > 30000`
   - `perlu_cek`: jika `ABS(selisih_cup) BETWEEN 1 AND 2` atau `ABS(selisih_tunai_idr) BETWEEN 5001 AND 30000`
   - `cocok`: jika `selisih_cup == 0` dan `ABS(selisih_tunai_idr) <= 5000`
5. **ATURAN EDGE CASES & KEPATUHAN ASAH 2026:**
   - Filter tanggal tanpa riwayat transaksi wajib menampilkan pesan kosong yang ramah (*"Data belum tersedia untuk periode ini"*), bukan layar blank/error.
   - Jika layanan AI Tim AE lambat/timeout/kena *rate limit*, tampilkan pesan notifikasi ramah + tetap tampilkan tabel rekap statis.
   - Wajib pasang label/badge kecil `"Data Simulasi Capstone (Agt–Okt 2026)"` pada dasbor (dilarang menyajikan data dummy seolah laporan keuangan riil UMKM).
   - **Dilarang** menaruh tombol mati / halaman *"segera hadir"*, dan **dilarang** menyertakan password/API key/nomor HP pribadi di repositori publik.
