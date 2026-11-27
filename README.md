# Kopi Sewu — Dasbor Pemilik, POS Staf & Peta Publik
Capstone Asah 2026 · Tim **A26-CS267 (Karsa)** · Divisi Full-Stack

> Data yang dipakai adalah **Data Simulasi Capstone (Agt–Okt 2026)**, bukan laporan keuangan riil UMKM.

## Arsitektur (decoupled)
```
frontend/   React + Vite + Tailwind CSS v4   → :5173
backend/    Express.js (REST /api/v1)         → :4000   (satu-satunya yang boleh bicara ke DB & layanan AI)
database/   schema + seed PostgreSQL (Supabase/Neon)
docs/handoff-ds/   dokumen serah terima Data Science (baca 00_PANDUAN_UTAMA dulu)
reference/  referensi visual Streamlit & palet warna
```
Alur: `React → Express → PostgreSQL` dan `React → Express → FastAPI (Tim AE)`. Frontend **tidak** memanggil AI/Gemini langsung.

## Mulai cepat
Prasyarat: Node ≥ 20.6.
```bash
npm run install:all
cp backend/.env.example backend/.env      # lalu isi sesuai kebutuhan
cp frontend/.env.example frontend/.env
npm run dev:be     # terminal 1 → http://localhost:4000/api/v1/health
npm run dev:fe     # terminal 2 → http://localhost:5173
```
Secara default `USE_MOCK_DATA=true`: endpoint `/api/v1/dashboard/*` melayani JSON tervalidasi dari DS (`backend/src/mock/`), jadi frontend bisa dikembangkan sebelum database siap.

## Setup database
1. Buat project PostgreSQL (Supabase/Neon), isi `DATABASE_URL` di `backend/.env`.
2. `psql "$DATABASE_URL" -f database/schema_postgresql_reference.sql`
3. `cd database && psql "$DATABASE_URL" -f seed_postgresql.sql`
4. Verifikasi: `npm --prefix backend run db:check` → harus `6 | 5 | 14 | 602 | 19886 | 537951000`.
5. Set `USE_MOCK_DATA=false` setelah agregasi SQL dibuat.

## Endpoint
| Endpoint | Status |
|---|---|
| `GET /api/v1/health` | ✅ |
| `GET /api/v1/dashboard/{summary,locations-and-carts,peak-hours,top-menus,reconciliation,forecast}` | ✅ mock DS · ⏳ SQL |
| `GET /api/v1/carts/active` (publik), POS/shift, `POST /api/v1/ai/chat` | ⏳ |

## Aturan wajib (ringkas)
Lihat `docs/handoff-ds/00_PANDUAN_UTAMA_TIM_FULLSTACK.md`: harga/kategori/unit dihitung di server; `payment_method` hanya `Tunai|QRIS`; `qty` 1–100 (≥15 = `bulk_order`); rekonsiliasi cup hanya `unit_type='cup'`; `cup_sisa NULL` ≠ 0; angka acuan omzet **Rp 537.951.000**.

## Keamanan
Jangan commit `.env`, password, API key, atau nomor HP pribadi (repo publik).

## Frontend (mengikuti desain Figma "Capstone Project")
Halaman yang sudah ada: Login (`/`), Dasbor Admin (`/admin`, data dari `/api/v1/dashboard/*`). Token warna/font ada di `frontend/src/index.css`.
Catatan: login masih **sesi demo di sisi klien** (belum ada `/auth/login`), portal staf (`/staf`) masih placeholder, panel Asisten AI memanggil `/api/v1/ai/chat` dan menampilkan "Mode cadangan" selama endpoint itu belum ada.
