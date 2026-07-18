import type { SelectOption } from '../types/admin.types'
import { useAdminLabel } from '../hooks/use-admin-label'

interface AdminStatusSelectProps<T extends string> {
  options: SelectOption<T>[]
  value: T
  disabled?: boolean
  onChange: (value: T) => void
}

export function AdminStatusSelect<T extends string>({
  options,
  value,
  disabled,
  onChange,
}: AdminStatusSelectProps<T>) {
  const label = useAdminLabel()

  return (
    <select
      value={value}
      disabled={disabled}
      onChange={(event) => onChange(event.target.value as T)}
    >
      {options.map((option) => (
        <option key={option.value} value={option.value}>
          {label('status', option.value, option.label)}
        </option>
      ))}
    </select>
  )
}
