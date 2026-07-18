import type { ReactNode } from 'react'
import { useEffect, useRef, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { getLocaleShortLabel, supportedLocales } from '@/core/i18n/supported-locales'
import { loadLocaleFonts } from '@/core/i18n/locale-fonts'

function GlobeIcon() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <circle cx="12" cy="12" r="9" />
      <path d="M3 12h18M12 3c3 3.2 3 14.8 0 18M12 3c-3 3.2-3 14.8 0 18" />
    </svg>
  )
}

export function LanguageSwitcher() {
  const { i18n, t } = useTranslation('common')
  const [open, setOpen] = useState(false)
  const containerRef = useRef<HTMLDivElement>(null)
  const currentLanguage = i18n.resolvedLanguage || i18n.language || 'en'
  const buttons: ReactNode[] = []
  let menu: ReactNode = null

  useEffect(() => {
    function closeOnOutsideClick(event: MouseEvent) {
      if (containerRef.current !== null && !containerRef.current.contains(event.target as Node)) {
        setOpen(false)
      }
    }

    function closeOnEscape(event: KeyboardEvent) {
      if (event.key === 'Escape') {
        setOpen(false)
      }
    }

    document.addEventListener('mousedown', closeOnOutsideClick)
    document.addEventListener('keydown', closeOnEscape)

    return () => {
      document.removeEventListener('mousedown', closeOnOutsideClick)
      document.removeEventListener('keydown', closeOnEscape)
    }
  }, [])

  for (const locale of supportedLocales) {
    let className = 'language-option'
    if (currentLanguage === locale.value) {
      className += ' active'
    }

    buttons.push(
      <button
        key={locale.value}
        type="button"
        className={className}
        onPointerEnter={() => loadLocaleFonts(locale.value)}
        onFocus={() => loadLocaleFonts(locale.value)}
        onClick={() => {
          loadLocaleFonts(locale.value)
          void i18n.changeLanguage(locale.value)
          setOpen(false)
        }}
      >
        <span>{locale.shortLabel}</span>
        <strong>{locale.nativeLabel}</strong>
      </button>,
    )
  }

  if (open) {
    menu = (
      <div className="language-menu" role="menu">
        {buttons}
      </div>
    )
  }

  return (
    <div className="language-switcher" ref={containerRef}>
      <button
        type="button"
        className="language-trigger"
        aria-label={t('language')}
        aria-expanded={open}
        onClick={() => setOpen(!open)}
      >
        <GlobeIcon />
        <span>{getLocaleShortLabel(currentLanguage)}</span>
      </button>
      {menu}
    </div>
  )
}
