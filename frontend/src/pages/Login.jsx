import { useState } from 'react';
import { Navigate, useNavigate } from 'react-router-dom';
import Logo from '../components/Logo.jsx';
import { useAuth } from '../lib/auth.jsx';

export default function Login() {
  const { user, login } = useAuth();
  const nav = useNavigate();
  const [role, setRole] = useState('staff');
  const [id, setId] = useState('');
  const [pw, setPw] = useState('');
  const [show, setShow] = useState(false);
  const [error, setError] = useState('');

  if (user) return <Navigate to={user.role === 'admin' ? '/admin' : '/staf'} replace />;

  const submit = (e) => {
    e.preventDefault();
    if (!id.trim() || !pw) return setError('ID Gerobak atau kata sandi salah.');
    setError('');
    login({ name: id.trim(), role });
    nav(role === 'admin' ? '/admin' : '/staf');
  };

  return (
    <main className="flex min-h-screen flex-col px-5 py-6 sm:px-10">
      <header>
        <p className="text-sm font-bold tracking-wide">KOPI SEWU</p>
        <p className="text-[11px] text-muted">OPERASIONAL GEROBAK • BATAM</p>
      </header>

      <div className="flex flex-1 items-center justify-center py-8">
        <form onSubmit={submit} className="w-full max-w-[450px] rounded-[28px] bg-white p-6 shadow-[0_20px_60px_-20px_rgba(62,39,35,.25)] sm:p-9">
          <div className="flex flex-col items-center text-center">
            <Logo />
            <h1 className="mt-3 text-4xl text-espresso">Kopi Sewu</h1>
            <p className="mt-2 text-sm text-muted">Sistem Operasional &amp;<br />Pemantauan Gerobak</p>
          </div>

          <div role="tablist" className="mt-6 grid grid-cols-2 rounded-2xl bg-sand p-1 text-sm font-semibold">
            {[['staff', 'Staf Gerobak'], ['admin', 'Admin']].map(([k, label]) => (
              <button key={k} type="button" role="tab" aria-selected={role === k} onClick={() => setRole(k)}
                className={`rounded-xl py-2.5 transition ${role === k ? 'bg-white text-dark shadow-sm' : 'text-muted'}`}>
                {label}
              </button>
            ))}
          </div>

          <label className="mt-5 block text-sm font-semibold" htmlFor="uid">ID Gerobak / Email</label>
          <input id="uid" value={id} onChange={(e) => setId(e.target.value)} placeholder="Contoh: G01 atau email"
            className="mt-2 w-full rounded-xl border border-black/10 px-4 py-3 text-sm outline-none focus:border-amber" />

          <label className="mt-4 block text-sm font-semibold" htmlFor="pw">Kata Sandi</label>
          <div className={`mt-2 flex items-center rounded-xl border bg-white px-4 ${error ? 'border-red' : 'border-black/10 focus-within:border-amber'}`}>
            <input id="pw" type={show ? 'text' : 'password'} value={pw} onChange={(e) => setPw(e.target.value)}
              className="w-full bg-transparent py-3 text-sm outline-none" />
            <button type="button" onClick={() => setShow(!show)} className="text-xs font-semibold text-muted" aria-label="Tampilkan kata sandi">
              {show ? 'Sembunyi' : 'Lihat'}
            </button>
          </div>

          {error && <p role="alert" className="mt-3 rounded-xl bg-red-soft px-4 py-3 text-xs text-red">{error}</p>}

          <button type="submit" className="mt-5 flex w-full items-center justify-between rounded-xl bg-amber px-5 py-3.5 text-sm font-bold text-white transition hover:brightness-95">
            <span className="flex-1 text-center">Masuk Sekarang</span><span aria-hidden>→</span>
          </button>
          <p className="mt-4 text-center text-xs text-muted">Butuh akses? Hubungi admin Kopi Sewu.</p>
        </form>
      </div>

      <footer className="text-xs text-muted">© 2026 Kopi Sewu • Batam, Kepulauan Riau</footer>
    </main>
  );
}
