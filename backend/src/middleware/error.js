export function notFound(req, res) {
  res.status(404).json({ error: 'NOT_FOUND', message: `Rute ${req.method} ${req.originalUrl} tidak ditemukan` });
}

// eslint-disable-next-line no-unused-vars
export function errorHandler(err, req, res, next) {
  const status = err.status ?? 500;
  if (status >= 500) console.error(err);
  res.status(status).json({
    error: err.code ?? (status >= 500 ? 'INTERNAL_ERROR' : 'BAD_REQUEST'),
    message: status >= 500 ? 'Terjadi kesalahan pada server' : err.message,
  });
}
