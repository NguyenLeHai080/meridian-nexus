const localeFontStylesheets: Record<string, string> = {
  vi: 'https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@400;500;600;700&family=Noto+Serif:wght@500;600&display=swap',
  ja: 'https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;600;700&family=Noto+Serif+JP:wght@500;600&display=swap',
  ko: 'https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;600;700&family=Noto+Serif+KR:wght@500;600&display=swap',
}

export function loadLocaleFonts(locale: string): void {
  const href = localeFontStylesheets[locale]
  if (href === undefined) {
    return
  }

  const loadedStylesheet = document.querySelector(`link[data-locale-font="${locale}"]`)
  if (loadedStylesheet !== null) {
    return
  }

  const stylesheet = document.createElement('link')
  stylesheet.rel = 'stylesheet'
  stylesheet.href = href
  stylesheet.dataset.localeFont = locale
  document.head.append(stylesheet)
}
