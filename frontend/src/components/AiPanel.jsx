import { useState } from 'react';
import { api } from '../lib/api.js';
import { rupiah } from '../lib/format.js';

const CHIPS = ['Menu terlaris periode ini', 'Bandingkan omzet gerobak', 'Kapan jam paling ramai?'];

// Frontend -> Express (/ai/chat) -> FastAPI Tim AE. Tidak pernah memanggil AI langsung.
export default function AiPanel({ carts }) {
  const [q, setQ] = useState('');
  const [msgs, setMsgs] = useState([]);
  const [busy, setBusy] = useState(false);
  const [offline, setOffline] = useState(false);
  const sessionId = useState(() => `sess-${Math.random().toString(36).slice(2, 10)}`)[0];

  const ask = async (text) => {
    const question = text.trim();
    if (!question || busy) return;
    setMsgs((m) => [...m, { from: 'me', text: question }]);
    setQ('');
    setBusy(true);
    try {
      const r = await api('/ai/chat', { method: 'POST', body: JSON.stringify({ session_id: sessionId, question }) });
      setOffline(false);
      setMsgs((m) => [...m, { from: 'ai', text: r.answer }]);
    } catch {
      setOffline(true);
      setMsgs((m) => [...m, { from: 'ai', text: 'Asisten AI sedang tidak tersedia. Rekap statis di bawah tetap bisa Anda gunakan.' }]);
    } finally { setBusy(false); }
  };

  return (
    <aside className="rounded-[24px] bg-white p-5 xl:sticky xl:top-6 xl:max-h-[calc(100vh-3rem)] xl:overflow-y-auto">
      <header className="flex items-center gap-3 border-b border-black/10 pb-4">
        <span className="grid h-10 w-10 place-items-center rounded-xl bg-amber-soft text-amber" aria-hidden>✦</span>
        <div><h2 className="text-xl text-espresso">Asisten AI</h2><p className="text-xs text-muted">Kopi Sewu</p></div>
      </header>

      {offline && (
        <div role="status" className="mt-4 rounded-xl border border-amber/40 bg-amber-soft p-3 text-xs">
          <p className="font-bold">Mode cadangan aktif</p>
          <p className="mt-1">AI sementara tidak tersedia. Menampilkan rekap statis terbaru.</p>
        </div>
      )}

      <div className="mt-4 space-y-3" aria-live="polite">
        {msgs.map((m, i) => (
          <p key={i} className={`rounded-2xl px-4 py-3 text-sm ${m.from === 'me' ? 'ml-6 bg-espresso text-cream' : 'mr-6 bg-sand'}`}>{m.text}</p>
        ))}
        {busy && <p className="text-xs text-muted">Menyusun jawaban…</p>}
      </div>

      <div className="mt-4 rounded-2xl border border-black/10 p-3">
        <h3 className="text-base text-espresso">Tabel Rekap Statis</h3>
        <table className="mt-2 w-full text-xs">
          <thead><tr className="text-left text-muted"><th className="py-1">Gerobak</th><th>Omzet</th></tr></thead>
          <tbody>{carts.map((c) => (
            <tr key={c.cart_id} className="border-t border-black/5"><td className="py-1.5 font-semibold">{c.cart_id.replace('CRT-', 'G')}</td><td>{rupiah(c.total_revenue_idr)}</td></tr>
          ))}</tbody>
        </table>
      </div>

      <p className="mt-4 text-[10px] tracking-widest text-muted">COBA TANYAKAN</p>
      <div className="mt-2 flex flex-wrap gap-2">
        {CHIPS.map((c) => (
          <button key={c} onClick={() => ask(c)} disabled={busy} className="rounded-xl bg-sand px-3 py-2 text-left text-xs font-semibold disabled:opacity-50">{c} ↗</button>
        ))}
      </div>

      <form onSubmit={(e) => { e.preventDefault(); ask(q); }} className="mt-4 flex items-end gap-2 rounded-2xl border border-black/10 p-3">
        <textarea value={q} onChange={(e) => setQ(e.target.value)} rows={2} placeholder="Tulis pertanyaan Anda…" aria-label="Pertanyaan untuk Asisten AI"
          className="w-full resize-none bg-transparent text-sm outline-none" />
        <button type="submit" disabled={busy || !q.trim()} aria-label="Kirim" className="grid h-9 w-9 shrink-0 place-items-center rounded-lg bg-amber text-white disabled:opacity-40">➤</button>
      </form>
    </aside>
  );
}
