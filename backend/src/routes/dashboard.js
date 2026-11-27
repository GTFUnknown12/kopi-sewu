import { Router } from 'express';
import { readFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
import { env } from '../config/env.js';

const router = Router();
const mockDir = path.join(path.dirname(fileURLToPath(import.meta.url)), '../mock');

// Kontrak: docs/handoff-ds/04_kontrak_data_dan_handoff_fs_ae.md
const endpoints = {
  summary: 'dashboard_summary.json',
  'locations-and-carts': 'locations_and_carts.json',
  'peak-hours': 'peak_hours.json',
  'top-menus': 'top_menus.json',
  reconciliation: 'reconciliation.json',
  forecast: 'demand_forecast.json',
};

for (const [route, file] of Object.entries(endpoints)) {
  router.get(`/${route}`, async (req, res, next) => {
    try {
      if (!env.useMockData) {
        // TODO(FS): ganti dengan agregasi SQL dari PostgreSQL (cocokkan dengan handoff_manifest.json)
        return res.status(501).json({ error: 'NOT_IMPLEMENTED', message: 'Agregasi SQL belum dibuat; set USE_MOCK_DATA=true' });
      }
      res.type('json').send(await readFile(path.join(mockDir, file), 'utf8'));
    } catch (e) {
      next(e);
    }
  });
}

export default router;
