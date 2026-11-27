import { useMemo } from 'react';
import { Bar, BarChart, CartesianGrid, Cell, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import Card from '../../components/Card.jsx';
import CartMap from '../../components/CartMap.jsx';
import AiPanel from '../../components/AiPanel.jsx';
import { useApi } from '../../lib/useApi.js';
import { num, ringkas, rupiah } from '../../lib/format.js';

const AMBER = '#E67E22';
const STATUS = {
  cocok: ['Cocok', 'bg-emerald-soft text-emerald'],
  perlu_cek: ['Perlu cek', 'bg-amber-soft text-amber'],
  selisih_tinggi: ['Selisih tinggi', 'bg-red-soft text-red'],
  data_tidak_lengkap: ['Data tidak lengkap', 'bg-sand text-muted'],
};

function Kpi({ label, value, hint }) {
  return (
    <div className="rounded-[20px] bg-white p-4">
      <p className="text-xs text-muted">{label}</p>
      <p className="mt-2 whitespace-nowrap font-display text-xl text-espresso sm:text-2xl">{value}</p>
      <p className="mt-1 text-[11px] text-emerald">{hint}</p>
    </div>
  );
}

export default function Dashboard() {
  const sum = useApi('/dashboard/summary');
  const loc = useApi('/dashboard/locations-and-carts');
  const peak = useApi('/dashboard/peak-hours');
  const rec = useApi('/dashboard/reconciliation');

  const hourly = useMemo(() => {
    if (!peak.data) return [];
    const acc = {};
    for (const r of peak.data.heatmap) {
      (acc[r.hour] ??= []).push(r.avg_cups_per_shift_hour);
    }
    return Object.entries(acc).map(([h, v]) => ({ hour: `${String(h).padStart(2, '0')}`, cups: +(v.reduce((a, b) => a + b, 0) / v.length).toFixed(2) }));
  }, [peak.data]);

  const loading = sum.loading || loc.loading || peak.loading || rec.loading;
  const error = sum.error || loc.error || peak.error || rec.error;

  if (loading) return <p className="p-6 text-sm text-muted">Memuat data…</p>;
  if (error) return <p role="alert" className="m-4 rounded-xl bg-red-soft p-4 text-sm text-red">Gagal memuat data: {error}. Pastikan backend berjalan.</p>;

  const { kpi, meta } = sum.data;
  const carts = loc.data.cart_comparison;
  const top = hourly.reduce((a, b) => (b.cups > a.cups ? b : a), hourly[0]);
  const bestCart = carts.reduce((a, b) => (b.total_revenue_idr > a.total_revenue_idr ? b : a));
  const r = rec.data.summary;
  const latest = rec.data.shift_details.slice(-6).reverse();

  return (
    <div className="grid gap-6 xl:grid-cols-[minmax(0,1fr)_320px]">
      <div className="min-w-0">
        <p className="text-[11px] tracking-widest text-muted">OPERASIONAL / RINGKASAN</p>
        <div className="mt-1 flex flex-wrap items-start justify-between gap-3">
          <div>
            <h1 className="text-3xl text-espresso sm:text-4xl">Pantau hari, racik strategi.</h1>
            <p className="mt-1 text-sm text-muted">Periode {meta.start_date} s.d. {meta.end_date} • Semua gerobak di Batam</p>
          </div>
          <span className="rounded-full bg-amber-soft px-3 py-1.5 text-xs font-semibold text-amber">Data Simulasi Capstone (Agt–Okt 2026)</span>
        </div>

        <div className="mt-5 grid grid-cols-2 gap-3 lg:grid-cols-4">
          <Kpi label="Omzet" value={rupiah(kpi.total_revenue_idr)} hint={`Margin kotor ${String(kpi.gross_margin_pct).replace('.', ',')}%`} />
          <Kpi label="Cup terjual" value={`${num(kpi.total_cups_sold)} Cup`} hint={`+ ${num(kpi.total_bottles_sold)} botol`} />
          <Kpi label="Unit operasional" value={`${carts.length} Unit`} hint={`Terbaik: ${bestCart.cart_name}`} />
          <Kpi label="Jam ramai" value={`${top.hour}:00`} hint={`rata-rata ${top.cups} cup/jam`} />
        </div>

        <div className="mt-4 grid gap-4 lg:grid-cols-2">
          <Card title="Omzet per gerobak" subtitle="Perbandingan total omzet periode">
            <div className="h-56">
              <ResponsiveContainer>
                <BarChart data={carts.map((c) => ({ name: c.cart_id.replace('CRT-', 'G'), v: c.total_revenue_idr }))}>
                  <CartesianGrid vertical={false} stroke="#0000000d" />
                  <XAxis dataKey="name" tickLine={false} axisLine={false} fontSize={12} />
                  <YAxis tickFormatter={(v) => ringkas(v)} tickLine={false} axisLine={false} fontSize={11} width={44} />
                  <Tooltip formatter={(v) => rupiah(v)} cursor={{ fill: '#0000000a' }} />
                  <Bar dataKey="v" radius={[6, 6, 0, 0]}>
                    {carts.map((c) => <Cell key={c.cart_id} fill={c.cart_id === bestCart.cart_id ? AMBER : '#F2B880'} />)}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </Card>

          <Card title="Ritme penjualan" subtitle="Rata-rata cup per jam operasional">
            <div className="h-56">
              <ResponsiveContainer>
                <LineChart data={hourly}>
                  <CartesianGrid vertical={false} stroke="#0000000d" />
                  <XAxis dataKey="hour" tickLine={false} axisLine={false} fontSize={12} />
                  <YAxis tickLine={false} axisLine={false} fontSize={11} width={32} />
                  <Tooltip formatter={(v) => `${v} cup/jam`} labelFormatter={(h) => `Pukul ${h}:00`} />
                  <Line type="monotone" dataKey="cups" stroke={AMBER} strokeWidth={2.5} dot={{ r: 3 }} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </Card>
        </div>

        <div className="mt-4 grid gap-4 lg:grid-cols-2">
          <Card title="Titik operasional di Batam" action={<span className="text-xs font-semibold text-emerald">{loc.data.location_ranking.length} titik</span>}>
            <CartMap locations={loc.data.location_ranking} />
          </Card>

          <Card title="Status rekonsiliasi" subtitle={`${num(r.total_shifts)} shift • selisih ${num(r.total_cup_diff)} cup`}>
            <ul className="space-y-3 text-sm">
              {[['cocok', r.matched_shifts], ['perlu_cek', r.perlu_cek_shifts], ['selisih_tinggi', r.high_discrepancy_shifts], ['data_tidak_lengkap', r.incomplete_shifts]].map(([k, v]) => (
                <li key={k} className="flex items-center justify-between">
                  <span className={`rounded-full px-3 py-1 text-xs font-semibold ${STATUS[k][1]}`}>{STATUS[k][0]}</span>
                  <span className="font-bold">{num(v)} shift</span>
                </li>
              ))}
            </ul>
          </Card>
        </div>

        <Card title="Shift terbaru" subtitle="Rekonsiliasi shift terakhir pada periode data" className="mt-4">
          <div className="overflow-x-auto">
            <table className="w-full min-w-[560px] text-sm">
              <thead><tr className="bg-cream text-left text-[11px] tracking-wider text-muted">
                {['TANGGAL', 'GEROBAK', 'CUP TERPAKAI', 'SELISIH CUP', 'STATUS'].map((h) => <th key={h} className="px-3 py-2">{h}</th>)}
              </tr></thead>
              <tbody>{latest.map((s) => (
                <tr key={s.shift_id} className="border-t border-black/5">
                  <td className="px-3 py-3">{s.shift_date}</td>
                  <td className="px-3 py-3">{s.cart_name}</td>
                  <td className="px-3 py-3">{s.cup_sisa == null ? '—' : num(s.cup_terpakai_fisik)}</td>
                  <td className="px-3 py-3">{s.cup_sisa == null ? '—' : s.selisih_cup}</td>
                  <td className="px-3 py-3"><span className={`rounded-full px-3 py-1 text-xs font-semibold ${STATUS[s.reconciliation_status][1]}`}>{STATUS[s.reconciliation_status][0]}</span></td>
                </tr>
              ))}</tbody>
            </table>
          </div>
        </Card>
      </div>

      <AiPanel carts={carts} />
    </div>
  );
}
