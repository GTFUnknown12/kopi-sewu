import { Router } from 'express';
import { env } from '../config/env.js';
import { query } from '../db/pool.js';

const router = Router();

router.get('/', async (req, res) => {
  const out = { status: 'ok', service: 'karsa-backend', mockData: env.useMockData, database: 'skipped' };
  if (env.databaseUrl) {
    try {
      await query('SELECT 1');
      out.database = 'up';
    } catch {
      out.database = 'down';
      out.status = 'degraded';
    }
  }
  res.json(out);
});

export default router;
