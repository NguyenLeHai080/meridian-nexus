import i18n from 'i18next'
import LanguageDetector from 'i18next-browser-languagedetector'
import resourcesToBackend from 'i18next-resources-to-backend'
import { initReactI18next } from 'react-i18next'
import { loadLocaleFonts } from './locale-fonts'

const localeModules = import.meta.glob<{ default: Record<string, unknown> }>(
  '../../locales/*/*.json',
)

function syncDocumentLanguage(language: string): void {
  const locale = language.split('-')[0]
  document.documentElement.lang = locale
  document.documentElement.dir = 'ltr'
  loadLocaleFonts(locale)
}

const initialization = i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .use(
    resourcesToBackend(async (language: string, namespace: string) => {
      const path = `../../locales/${language}/${namespace}.json`
      const loadLocale = localeModules[path]

      if (loadLocale === undefined) {
        throw new Error(`Missing locale resource: ${language}/${namespace}`)
      }

      const resource = await loadLocale()
      return resource.default
    }),
  )
  .init({
    supportedLngs: ['en', 'vi', 'ja', 'ko'],
    fallbackLng: 'en',
    defaultNS: 'common',
    ns: ['common'],
    load: 'languageOnly',
    interpolation: { escapeValue: false },
    detection: {
      order: ['localStorage', 'navigator', 'htmlTag'],
      caches: ['localStorage'],
      lookupLocalStorage: 'northstar-language',
    },
    react: { useSuspense: true },
  })

i18n.on('languageChanged', syncDocumentLanguage)

void initialization.then(() => {
  const language = i18n.resolvedLanguage || i18n.language || 'en'
  syncDocumentLanguage(language)
})

export { i18n }
