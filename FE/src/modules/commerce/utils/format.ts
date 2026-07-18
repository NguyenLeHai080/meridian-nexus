export function formatMoney(value: number): string {
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(value)
}

export function formatDate(value: string | null): string {
  if (!value) return 'Unpublished'

  return new Intl.DateTimeFormat('en', { dateStyle: 'medium' }).format(new Date(value))
}
