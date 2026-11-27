import { Navigate, NavLink, Outlet, useNavigate } from 'react-router-dom';
import Logo from '../components/Logo.jsx';
import { useAuth } from '../lib/auth.jsx';

export default function AdminLayout() {
  const { user, logout } = useAuth();
  const nav = useNavigate();
  if (!user) return <Navigate to="/" replace />;
  if (user.role !== 'admin') return <Navigate to="/staf" replace />;

  return (
    <div className="min-h-screen lg:flex">
      <aside className="flex flex-col bg-dark px-4 py-5 text-cream lg:sticky lg:top-0 lg:h-screen lg:w-[183px] lg:shrink-0">
        <div className="flex items-center gap-3 lg:block">
          <Logo size={36} />
          <div className="lg:mt-3">
            <p className="font-display text-2xl leading-none">Kopi Sewu</p>
            <p className="mt-1 text-[11px] tracking-widest text-cream/60">ADMIN</p>
          </div>
        </div>
        <nav className="mt-4 lg:mt-10" aria-label="Menu utama">
          <p className="mb-2 hidden text-[10px] tracking-widest text-cream/50 lg:block">RUANG KERJA</p>
          <NavLink to="/admin" end className={({ isActive }) =>
            `block rounded-xl px-3 py-2.5 text-sm font-semibold ${isActive ? 'bg-espresso' : 'text-cream/70 hover:bg-white/5'}`}>
            Ringkasan
          </NavLink>
        </nav>
        <div className="mt-4 border-t border-white/10 pt-4 lg:mt-auto">
          <p className="text-sm font-semibold">Admin Operasional</p>
          <button onClick={() => { logout(); nav('/'); }} className="mt-2 text-sm text-cream/70 hover:text-cream">Keluar</button>
        </div>
      </aside>
      <main className="min-w-0 flex-1 p-4 sm:p-6"><Outlet /></main>
    </div>
  );
}
