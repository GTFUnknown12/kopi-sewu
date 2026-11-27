-- 1. Informasi Dasar Brand (Read-Only untuk Pelanggan, Editable oleh Admin)
CREATE TABLE IF NOT EXISTS brand_info (
    brand_id          SERIAL PRIMARY KEY,
    brand_name        VARCHAR(60) NOT NULL DEFAULT 'Kopi Sewu',
    tagline           VARCHAR(150) NOT NULL,
    description       TEXT NOT NULL,
    operating_hours   VARCHAR(80) NOT NULL,
    contact_whatsapp  VARCHAR(25),
    instagram_handle  VARCHAR(50),
    updated_at        TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- 2. Master Titik Lokasi / Zona Mangkal (Acuan Analitik DS & Peta)
CREATE TABLE IF NOT EXISTS locations (
    location_id   VARCHAR(10) PRIMARY KEY,
    location_name VARCHAR(80) NOT NULL,
    area          VARCHAR(60) NOT NULL,
    zone_type     VARCHAR(40) NOT NULL,
    latitude      DECIMAL(9, 6) NOT NULL,
    longitude     DECIMAL(9, 6) NOT NULL,
    source_status VARCHAR(30) NOT NULL DEFAULT 'asumsi_titik_sekitar_umkm',
    notes         TEXT
);

-- 3. Master Armada Gerobak & Outlet + Status Live Tracking
CREATE TABLE IF NOT EXISTS carts (
    cart_id             VARCHAR(10) PRIMARY KEY,
    cart_name           VARCHAR(50) NOT NULL,
    unit_type           VARCHAR(25) NOT NULL CHECK (unit_type IN ('outlet_tetap', 'gerobak_keliling')),
    default_mode        VARCHAR(15) NOT NULL CHECK (default_mode IN ('tetap', 'mangkal', 'keliling')),
    staff_alias         VARCHAR(30) NOT NULL,
    home_location_id    VARCHAR(10) NOT NULL REFERENCES locations(location_id),
    cup_capacity        INTEGER NOT NULL CHECK (cup_capacity > 0),
    source_status       VARCHAR(30) NOT NULL DEFAULT 'asumsi_armada_sintetis',
    
    -- Kontrol Izin & Live Location (Dikelola bersama oleh Admin & Staff)
    is_authorized       BOOLEAN NOT NULL DEFAULT TRUE,   -- Master izin dari Admin (TRUE = diizinkan tampil)
    is_active           BOOLEAN NOT NULL DEFAULT FALSE,  -- Saklar operasional oleh Staff/Admin (TRUE = sedang mangkal/buka)
    current_location_id VARCHAR(10) REFERENCES locations(location_id), -- Zona terdekat (opsional untuk analitik DS)
    current_latitude    DECIMAL(9, 6),                   -- Koordinat GPS live dari perangkat Staff
    current_longitude   DECIMAL(9, 6),                   -- Koordinat GPS live dari perangkat Staff
    last_updated_at     TIMESTAMP WITH TIME ZONE
);

-- 4. Akun Pengguna Internal (Khusus Admin & Staff; Pelanggan tanpa login)
CREATE TABLE IF NOT EXISTS users (
    user_id           VARCHAR(15) PRIMARY KEY,
    full_name         VARCHAR(80) NOT NULL,
    username          VARCHAR(40) NOT NULL UNIQUE,
    password_hash     TEXT NOT NULL,
    role              VARCHAR(15) NOT NULL CHECK (role IN ('admin', 'staff')),
    assigned_cart_id  VARCHAR(10) REFERENCES carts(cart_id) ON DELETE SET NULL,
    is_account_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at        TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- 5. Katalog Menu Kopi Sewu
CREATE TABLE IF NOT EXISTS menu (
    menu_id          VARCHAR(10) PRIMARY KEY,
    category         VARCHAR(20) NOT NULL CHECK (category IN ('Kopi', 'Non Kopi', 'Botolan')),
    menu_name        VARCHAR(60) NOT NULL UNIQUE,
    unit_type        VARCHAR(10) NOT NULL CHECK (unit_type IN ('cup', 'botol')),
    price            INTEGER NOT NULL CHECK (price > 0),
    hpp_asumsi       INTEGER NOT NULL CHECK (hpp_asumsi >= 0),
    estimated_margin INTEGER GENERATED ALWAYS AS (price - hpp_asumsi) STORED,
    image_filename   VARCHAR(100),
    image_gdrive_url TEXT,
    is_available     BOOLEAN NOT NULL DEFAULT TRUE,
    price_source     VARCHAR(20) NOT NULL DEFAULT 'primer_umkm',
    hpp_source       VARCHAR(20) NOT NULL DEFAULT 'asumsi_tim_ds'
);

-- 6. Sesi Operasional / Shift Harian Gerobak
CREATE TABLE IF NOT EXISTS shifts (
    shift_id            VARCHAR(20) PRIMARY KEY,
    shift_date          DATE NOT NULL,
    cart_id             VARCHAR(10) NOT NULL REFERENCES carts(cart_id),
    staff_user_id       VARCHAR(15) REFERENCES users(user_id), -- Nullable agar CSV sintetis DS tetap bisa masuk
    location_id         VARCHAR(10) NOT NULL REFERENCES locations(location_id),
    mode_operasi        VARCHAR(15) NOT NULL CHECK (mode_operasi IN ('tetap', 'mangkal', 'keliling')),
    start_time          TIMESTAMP NOT NULL,
    end_time            TIMESTAMP,
    weather             VARCHAR(15) CHECK (weather IN ('Cerah', 'Berawan', 'Hujan')),
    cup_dibawa          INTEGER NOT NULL CHECK (cup_dibawa >= 0),
    cup_sisa            INTEGER CHECK (cup_sisa >= 0 AND cup_sisa <= cup_dibawa),
    setoran_tunai_fisik INTEGER CHECK (setoran_tunai_fisik >= 0),
    mutasi_qris_aktual  INTEGER CHECK (mutasi_qris_aktual >= 0),
    status              VARCHAR(15) NOT NULL DEFAULT 'aktif' CHECK (status IN ('aktif', 'selesai')),
    CHECK (end_time IS NULL OR end_time > start_time)
);

-- 7. Catatan Transaksi Penjualan (Input POS Staff & Data Latih DS)
CREATE TABLE IF NOT EXISTS transactions (
    transaction_id        VARCHAR(15) PRIMARY KEY,
    shift_id              VARCHAR(20) NOT NULL REFERENCES shifts(shift_id),
    staff_user_id         VARCHAR(15) REFERENCES users(user_id), -- Pencatat transaksi POS
    transaction_timestamp TIMESTAMP NOT NULL,
    cart_id               VARCHAR(10) NOT NULL REFERENCES carts(cart_id),
    location_id           VARCHAR(10) NOT NULL REFERENCES locations(location_id),
    menu_id               VARCHAR(10) NOT NULL REFERENCES menu(menu_id),
    menu_name             VARCHAR(60) NOT NULL,
    category              VARCHAR(20) NOT NULL,
    unit_type             VARCHAR(10) NOT NULL CHECK (unit_type IN ('cup', 'botol')),
    qty                   INTEGER NOT NULL CHECK (qty >= 1),
    unit_price            INTEGER NOT NULL CHECK (unit_price > 0),
    total_price           INTEGER NOT NULL CHECK (total_price = qty * unit_price),
    hpp_asumsi_total      INTEGER NOT NULL CHECK (hpp_asumsi_total >= 0),
    payment_method        VARCHAR(20) NOT NULL CHECK (payment_method IN ('Tunai', 'QRIS', 'Tidak Diketahui')),
    order_type            VARCHAR(15) NOT NULL DEFAULT 'reguler' CHECK (order_type IN ('reguler', 'bulk_order'))
);

-- 8. Riwayat Obrolan Chatbot Asisten Admin (Gen AI + Log Inferensi)
CREATE TABLE IF NOT EXISTS ai_chat_logs (
    chat_id           SERIAL PRIMARY KEY,
    user_id           VARCHAR(15) REFERENCES users(user_id),
    session_id        VARCHAR(50) NOT NULL,
    user_question     TEXT NOT NULL,
    predicted_intent  VARCHAR(40),
    intent_confidence DECIMAL(5, 4),
    is_out_of_context BOOLEAN NOT NULL DEFAULT FALSE,
    ai_response       TEXT NOT NULL,
    fallback_used     BOOLEAN NOT NULL DEFAULT FALSE,
    created_at        TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Index Optimasi Query
CREATE INDEX IF NOT EXISTS idx_carts_live       ON carts(is_authorized, is_active);
CREATE INDEX IF NOT EXISTS idx_tx_timestamp     ON transactions(transaction_timestamp);
CREATE INDEX IF NOT EXISTS idx_tx_shift_id      ON transactions(shift_id);
CREATE INDEX IF NOT EXISTS idx_tx_cart_loc      ON transactions(cart_id, location_id);
CREATE INDEX IF NOT EXISTS idx_tx_menu_id       ON transactions(menu_id);
CREATE INDEX IF NOT EXISTS idx_shifts_date      ON shifts(shift_date, cart_id);
CREATE INDEX IF NOT EXISTS idx_chat_session     ON ai_chat_logs(session_id, created_at);