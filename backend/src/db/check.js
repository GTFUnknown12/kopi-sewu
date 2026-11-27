// Sanity check seeding. Hasil wajib: 6 | 5 | 14 | 602 | 19886 | 537951000
import { query, getPool } from './pool.js';

const { rows } = await query(`
  SELECT
    (SELECT COUNT(*) FROM locations)    AS locations,
    (SELECT COUNT(*) FROM carts)        AS carts,
    (SELECT COUNT(*) FROM menu)         AS menu,
    (SELECT COUNT(*) FROM shifts)       AS shifts,
    (SELECT COUNT(*) FROM transactions) AS transactions,
    (SELECT SUM(total_price) FROM transactions) AS total_revenue_idr`);
console.table(rows);
await getPool().end();
