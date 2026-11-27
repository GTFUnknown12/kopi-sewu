import express from 'express';
import cors from 'cors';
import db from './config/env.js';
import 'dotenv/config';

// const express = require('express');
// const cors = require('cors');
// const db = require('./src/config/database');

const app = express();
app.use(cors());
app.use(express.json());

app.get('/api/health', async (req, res) => {
  try {
    await db.query('SELECT 1');
    res.json({ status: 'OK', database: 'Connected' });
  } catch (error) {
    res.status(500).json({ status: 'Error', message: error.message });
  }
});

const PORT = process.env.PORT || 4000;
app.listen(PORT, () => {
  console.log(`Server berjalan di port ${PORT}`);
});