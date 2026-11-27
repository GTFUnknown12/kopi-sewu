// Peta skematis (bukan tile map) — posisi titik dihitung dari lat/lon master lokasi.
// Peta Leaflet interaktif untuk pelanggan dibuat terpisah (/carts/active).
export default function CartMap({ locations }) {
  const lats = locations.map((l) => l.latitude);
  const lons = locations.map((l) => l.longitude);
  const [minLa, maxLa, minLo, maxLo] = [Math.min(...lats), Math.max(...lats), Math.min(...lons), Math.max(...lons)];
  const pos = (l) => ({
    left: `${8 + ((l.longitude - minLo) / (maxLo - minLo || 1)) * 80}%`,
    top: `${10 + (1 - (l.latitude - minLa) / (maxLa - minLa || 1)) * 70}%`,
  });
  return (
    <div className="relative h-56 overflow-hidden rounded-2xl bg-[#EFEBDD]" role="img" aria-label="Peta skematis titik operasional di Batam">
      <div className="absolute inset-x-0 bottom-0 h-10 bg-[#E3ECEA]" />
      {locations.map((l) => (
        <div key={l.location_id} style={pos(l)} className="absolute -translate-x-1/2 -translate-y-1/2">
          <span className="flex items-center gap-1 rounded-full bg-espresso px-2 py-1 text-[10px] font-semibold text-cream shadow">
            ☕ {l.location_id.replace('LOC-', 'L')}
          </span>
        </div>
      ))}
      <span className="absolute bottom-2 left-3 rounded-full bg-white px-3 py-1 text-[11px] text-muted">Peta area operasional • skematis</span>
    </div>
  );
}
