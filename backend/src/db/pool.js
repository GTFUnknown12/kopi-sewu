import pg from 'pg';
import { env } from '../config/env.js';

let pool = null;

/** Lazy: pool baru dibuat saat pertama dipakai, sehingga mode mock jalan tanpa DB. */
export function getPool() {
  if (!env.databaseUrl) throw new Error('DATABASE_URL belum diatur');
  if (!pool) {
    pool = new pg.Pool({
      connectionString: env.databaseUrl,
      ssl: env.databaseSsl ? { rejectUnauthorized: false } : false,
      max: 10,
    });
  }
  return pool;
}

export const query = (text, params) => getPool().query(text, params);
