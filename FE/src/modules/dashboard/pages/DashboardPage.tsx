import { useTranslation } from 'react-i18next'
import { useAuthStore } from '@/core/auth/auth-store'

const modules = [
  { number: '01', key: 'identity' },
  { number: '02', key: 'operations' },
  { number: '03', key: 'intelligence' },
]

export function DashboardPage() {
  const { t } = useTranslation('common')
  const user = useAuthStore((state) => state.user)
  let firstName = ''

  if (user !== null) {
    firstName = user.name.split(' ')[0]
  }

  return (
    <section className="dashboard">
      <header className="dashboard__header">
        <div>
          <div className="eyebrow">{t('workspace.eyebrow')}</div>
          <h1>{t('workspace.welcome', { name: firstName })}</h1>
        </div>
        <span className="system-status">
          <i />
          {t('workspace.operational')}
        </span>
      </header>
      <div className="dashboard__statement">
        <span>{t('workspace.foundation')}</span>
        <p>{t('workspace.description')}</p>
      </div>
      <div className="module-list">
        {modules.map((module) => (
          <article className="module-row" key={module.number}>
            <span>{module.number}</span>
            <div>
              <h2>{t(`workspace.modules.${module.key}.name`)}</h2>
              <p>{t(`workspace.modules.${module.key}.detail`)}</p>
            </div>
            <strong>{t(`workspace.modules.${module.key}.status`)}</strong>
          </article>
        ))}
      </div>
    </section>
  )
}
