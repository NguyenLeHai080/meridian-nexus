export interface SupportedLocale {
  value: 'en' | 'vi' | 'ja' | 'ko'
  shortLabel: string
  nativeLabel: string
}

export const supportedLocales: SupportedLocale[] = [
  { value: 'en', shortLabel: 'EN', nativeLabel: 'English' },
  { value: 'vi', shortLabel: 'VN', nativeLabel: 'Tiếng Việt' },
  { value: 'ja', shortLabel: 'JP', nativeLabel: '日本語' },
  { value: 'ko', shortLabel: 'KR', nativeLabel: '한국어' },
]

export function getLocaleShortLabel(language: string): string {
  for (const locale of supportedLocales) {
    if (locale.value === language) {
      return locale.shortLabel
    }
  }

  return language.toUpperCase()
}
