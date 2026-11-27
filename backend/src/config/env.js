const bool = (v, d = false) => (v === undefined ? d : String(v).toLowerCase() === 'true');

export const env = {
  nodeEnv: process.env.NODE_ENV ?? 'development',
  port: Number(process.env.PORT ?? 4000),
  corsOrigins: (process.env.CORS_ORIGINS ?? 'http://localhost:5173')
    .split(',')
    .map((s) => s.trim())
    .filter(Boolean),
  databaseUrl: process.env.DATABASE_URL ?? '',
  databaseSsl: bool(process.env.DATABASE_SSL, true),
  useMockData: bool(process.env.USE_MOCK_DATA, true),
  aiServiceUrl: process.env.AI_SERVICE_URL ?? 'http://localhost:8000',
  aiTimeoutMs: Number(process.env.AI_SERVICE_TIMEOUT_MS ?? 15000),
};
