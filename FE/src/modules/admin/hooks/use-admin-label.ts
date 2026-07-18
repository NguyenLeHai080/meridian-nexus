import { useTranslation } from 'react-i18next'

export function useAdminLabel() {
  const { t } = useTranslation('admin')

  return (group: 'status' | 'role', value: string, fallback?: string): string => {
    let defaultValue = value
    if (fallback !== undefined) {
      defaultValue = fallback
    }

    return t(`${group}.${value}`, { defaultValue })
  }
}
