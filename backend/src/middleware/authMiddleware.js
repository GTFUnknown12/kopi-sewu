import jwt from 'jsonwebtoken';

const verifyToken = (req, res, next) => {
  const authHeader = req.headers.authorization;
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return res.status(401).json({ message: 'Token tidak ditemukan' });
  }

  try {
    const token = authHeader.split(' ')[1];
    req.user = jwt.verify(token, process.env.JWT_SECRET); // berisi { user_id, role, assigned_cart_id }
    next();
  } catch (err) {
    return res.status(403).json({ message: 'Token tidak valid atau kedaluwarsa' });
  }
};

const requireRole = (...allowedRoles) => (req, res, next) => {
  if (!req.user || !allowedRoles.includes(req.user.role)) {
    return res.status(403).json({ message: 'Akses ditolak untuk role ini' });
  }
  next();
};

export default { verifyToken, requireRole };