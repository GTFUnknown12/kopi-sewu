kopi sewu/
├── package.json ← perintah pintasan (npm run dev:be, dev:fe, dst.)
├── README.md
├── .gitignore ← mencegah .env & node_modules ikut ke GitHub
│
├── frontend/ ← TAMPILAN (React + Vite + Tailwind) :5173
│ ├── index.html ← pintu masuk + pemuat font Google
│ ├── vite.config.js ← plugin React/Tailwind + proxy /api → backend
│ ├── .env.example
│ └── src/
│ ├── main.jsx ← menyalakan React
│ ├── App.jsx ← daftar halaman (rute): / , /admin, /staf
│ ├── index.css ← warna & font dari Figma (design tokens)
│ ├── pages/
│ │ ├── Login.jsx
│ │ ├── StaffPlaceholder.jsx ← sementara
│ │ └── admin/Dashboard.jsx ← dasbor ringkasan
│ ├── layouts/
│ │ └── AdminLayout.jsx ← sidebar + bingkai halaman admin
│ ├── components/ ← potongan UI yang dipakai ulang
│ │ ├── Card.jsx, Logo.jsx, CartMap.jsx, AiPanel.jsx
│ └── lib/ ← fungsi bantu
│ ├── api.js ← satu-satunya jalur ke backend (fetch)
│ ├── useApi.js ← hook: ambil data + loading + error
│ ├── auth.jsx ← status login (sementara demo)
│ └── format.js ← format Rupiah & angka
│
├── backend/ ← DAPUR (Express.js) :4000
│ ├── .env.example
│ └── src/
│ ├── index.js ← menyalakan server
│ ├── app.js ← pasang CORS, Helmet, JSON, rute
│ ├── config/env.js ← baca pengaturan dari .env
│ ├── routes/
│ │ ├── index.js ← pintu semua rute /api/v1
│ │ ├── health.js ← cek server/DB hidup
│ │ └── dashboard.js← 6 endpoint dasbor (sementara baca JSON mock)
│ ├── middleware/error.js ← 404 & penanganan error seragam
│ ├── db/
│ │ ├── pool.js ← koneksi PostgreSQL
│ │ └── check.js ← cek hasil seed
│ └── mock/ ← 6 JSON dari DS
│
├── database/ ← GUDANG (milik teman Anda)
│ ├── schema_postgresql_reference.sql
│ ├── seed_postgresql.sql
│ └── db_seed/ 01…05 .csv
│
├── docs/handoff-ds/ ← dokumen dari tim DS
└── reference/ ← referensi dasbor Streamlit
