-- ============================================================================
-- Skrip Seeding PostgreSQL (Urutan Patuh Foreign Key: 01 -> 05)
-- Jalankan terlebih dahulu: schema_postgresql_reference.sql
-- Kemudian jalankan dari folder `database/` menggunakan psql:
--   psql "<DATABASE_URL>" -f seed_postgresql.sql
-- ============================================================================

\copy locations (location_id, location_name, area, zone_type, latitude, longitude, source_status, notes) FROM 'db_seed/01_locations.csv' WITH (FORMAT csv, HEADER true);
\copy carts (cart_id, cart_name, unit_type, default_mode, staff_alias, home_location_id, cup_capacity, source_status) FROM 'db_seed/02_carts.csv' WITH (FORMAT csv, HEADER true);
\copy menu (menu_id, category, menu_name, unit_type, price, hpp_asumsi, image_filename, image_gdrive_url, is_available, price_source, hpp_source) FROM 'db_seed/03_menu.csv' WITH (FORMAT csv, HEADER true);
\copy shifts (shift_id, shift_date, cart_id, location_id, mode_operasi, start_time, end_time, weather, cup_dibawa, cup_sisa, setoran_tunai_fisik, mutasi_qris_aktual, status) FROM 'db_seed/04_shifts.csv' WITH (FORMAT csv, HEADER true, NULL '');
\copy transactions (transaction_id, shift_id, transaction_timestamp, cart_id, location_id, menu_id, menu_name, category, unit_type, qty, unit_price, total_price, hpp_asumsi_total, payment_method, order_type) FROM 'db_seed/05_transactions.csv' WITH (FORMAT csv, HEADER true);

-- Sanity Check setelah seeding:
SELECT
    (SELECT COUNT(*) FROM locations)    AS locations_cnt,
    (SELECT COUNT(*) FROM carts)        AS carts_cnt,
    (SELECT COUNT(*) FROM menu)         AS menu_cnt,
    (SELECT COUNT(*) FROM shifts)       AS shifts_cnt,
    (SELECT COUNT(*) FROM transactions) AS transactions_cnt,
    (SELECT SUM(total_price) FROM transactions) AS total_revenue_idr;
-- Hasil wajib: 6 | 5 | 14 | 602 | 19886 | 537951000
