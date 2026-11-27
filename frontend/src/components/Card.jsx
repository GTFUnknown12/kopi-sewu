export default function Card({ title, subtitle, action, children, className = '' }) {
  return (
    <section className={`rounded-[20px] bg-white p-5 shadow-[0_1px_0_rgba(62,39,35,.04)] ${className}`}>
      {(title || action) && (
        <header className="mb-3 flex items-start justify-between gap-3">
          <div>
            {title && <h2 className="text-xl text-espresso">{title}</h2>}
            {subtitle && <p className="mt-0.5 text-xs text-muted">{subtitle}</p>}
          </div>
          {action}
        </header>
      )}
      {children}
    </section>
  );
}
