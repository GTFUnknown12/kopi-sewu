# Dasbor Interaktif Kopi Sewu Batam (Streamlit — Side Quest DS #1)

**Proyek:** Capstone Project Asah 2026 — Tim A26-CS267 (Karsa)  
**Divisi:** Data Science Specialist (Dwiyan Achmad Assidiqie & Noval Berauh)  
**Aplikasi Utama:** [app.py](app.py)

---

## 1. Fitur Utama Dasbor
1. **Ringkasan Eksekutif & Tren (Tab 1):** 6 kartu KPI dinamis, grafik *line chart* omzet harian + MA7 + marker hari hujan, grafik dampak cuaca (Outlet vs Gerobak), serta tombol **Unduh Rekap Harian (CSV)**.
2. **Peta Lokasi, Armada & Jam Ramai (Tab 2):** Peta interaktif OpenStreetMap 6 titik koridor Tiban–Sekupang–Batam Centre, kontras omzet/jam *weekday vs weekend*, *heatmap peak hours* interaktif, serta tabel deteksi shift *blind spot* (`< Rp 50.000/jam`).
3. **Performa 14 Menu Primer (Tab 3):** Ranking interaktif 14 menu asli Kopi Sewu (urut omzet/qty/margin), komposisi kategori per lokasi, dan ringkasan *valid bulk order*.
4. **Rekonsiliasi Setoran & Pembayaran (Tab 4):** Distribusi status rekonsiliasi per armada, adopsi QRIS vs Tunai per lokasi, tabel detail shift yang dapat difilter, serta tombol **Unduh Laporan Rekonsiliasi (CSV)**.
5. **Simulator Prediksi Stok Cup ML (Tab 5):** Integrasi langsung model terlatih [cup_demand_forecaster.joblib](../models/cup_demand_forecaster.joblib) dengan peringatan *blind spot* otomatis, cek kapasitas muatan gerobak, dan proyeksi 7 hari ke depan.
6. **Pembaruan Data Mandiri (Sidebar):** Mendukung unggahan file `transactions_clean.csv` dan/atau `shifts_clean.csv` baru dengan validasi kolom otomatis.

---

## 2. Cara Menjalankan Lokal
Dari folder root repositori (`DS-CAPSTONE-ASAH`), jalankan menggunakan `.venv`:

```powershell
.\.venv\Scripts\streamlit.exe run data-science\dashboard\app.py
```

---

## 3. Opsi Integrasi ke Aplikasi Web Tim Full-Stack (FS)
Tim FS memiliki dua opsi integrasi yang keduanya sudah didukung penuh oleh Divisi DS:
1. **Integrasi Native React (Direkomendasikan untuk MVP Utama):** Tim FS merender grafik dasbor di React menggunakan 6 berkas JSON siap pakai pada `data-science/data/handoff_fs/` (kontrak endpoint `/api/v1/dashboard/...`).
2. **Embed / Tautan Langsung Streamlit Community Cloud (Free Tier):** Deploy `data-science/dashboard/app.py` ke [Streamlit Community Cloud](https://streamlit.io/cloud) lalu sematkan melalui `<iframe>` dengan parameter `?embed=true` atau tombol *"Buka Dasbor Analitik Lanjutan"* pada halaman Dasbor Pemilik.
