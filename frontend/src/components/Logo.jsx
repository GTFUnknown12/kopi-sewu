export default function Logo({ size = 56 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 56 56" role="img" aria-label="Logo Kopi Sewu">
      <rect width="56" height="56" rx="14" fill="#3E2723" />
      <path d="M17 26h20v8a8 8 0 0 1-8 8h-4a8 8 0 0 1-8-8z" fill="#FAF6F0" />
      <path d="M37 28h2a4 4 0 0 1 0 8h-2" fill="none" stroke="#FAF6F0" strokeWidth="2.5" />
      <rect x="15" y="44" width="26" height="3" rx="1.5" fill="#E67E22" />
      <rect x="20" y="29" width="12" height="2" rx="1" fill="#E67E22" />
      <path d="M22 12c-2 2 2 3 0 6M28 12c-2 2 2 3 0 6" stroke="#E67E22" strokeWidth="1.8" fill="none" strokeLinecap="round" />
    </svg>
  );
}
