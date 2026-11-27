import { Navigate, useNavigate } from 'react-router-dom';
import { useAuth } from '../lib/auth.jsx';

export default function StaffPortal() {
  const { user, logout } = useAuth();
  const nav = useNavigate();
  if (!user) return <Navigate to="/" replace />;
  return (
    <main className="mx-auto max-w-md p-6">
      <h1 className="text-3xl text-espresso">Selamat jualan, {user.name}!</h1>
      <p className="mt-2 text-sm text-muted">Portal staf (kasir cepat) sedang dikerjakan pada tahap berikutnya.</p>
      <button onClick={() => { logout(); nav('/'); }} className="mt-6 rounded-xl bg-amber px-5 py-3 text-sm font-bold text-white">Keluar</button>
    </main>
  );
}
