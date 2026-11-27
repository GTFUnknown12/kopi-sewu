// Frontend HANYA bicara ke Express. Dilarang memanggil layanan AI/Gemini langsung.
const BASE = `${import.meta.env.VITE_API_URL ?? ''}/api/v1`;

export async function api(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.message ?? `HTTP ${res.status}`);
  }
  return res.json();
}
