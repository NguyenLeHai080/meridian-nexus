export function PageLoader({ label = 'Loading' }: { label?: string }) {
  return (
    <main className="page-loader" aria-live="polite">
      <span className="page-loader__mark">N</span>
      <span>{label}</span>
    </main>
  )
}
