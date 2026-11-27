import { createApp } from './app.js';
import { env } from './config/env.js';

createApp().listen(env.port, () => {
  console.log(`[karsa-backend] http://localhost:${env.port}/api/v1/health (mock=${env.useMockData})`);
});
