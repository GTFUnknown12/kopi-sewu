import { Router } from 'express';
import health from './health.js';
import dashboard from './dashboard.js';

const router = Router();
router.use('/health', health);
router.use('/dashboard', dashboard);
// Berikutnya: /carts/active (publik), /auth, /pos/transactions, /shifts, /ai/chat

export default router;
