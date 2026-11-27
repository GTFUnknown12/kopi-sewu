export const rupiah = (n) => 'Rp ' + Math.round(Number(n)).toLocaleString('id-ID');
export const num = (n) => Number(n).toLocaleString('id-ID');
/** 134.000 -> "134rb", 1.250.000 -> "1,25jt" */
export const ringkas = (n) =>
  n >= 1_000_000 ? `${(n / 1_000_000).toFixed(n % 1_000_000 ? 1 : 0).replace('.', ',')}jt` : `${Math.round(n / 1000)}rb`;
