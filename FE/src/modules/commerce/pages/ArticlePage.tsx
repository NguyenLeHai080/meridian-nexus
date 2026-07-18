import { useTranslation } from 'react-i18next'
import { Link, useParams } from 'react-router-dom'
import { usePost } from '../hooks/use-commerce-data'
import { formatDate } from '../utils/format'

export function ArticlePage() {
  const { t } = useTranslation('storefront')
  const { slug = '' } = useParams()
  const { data } = usePost(slug)

  if (data === undefined) {
    return <p className="catalog-loading">{t('journal.loading')}</p>
  }

  return (
    <article className="article-page">
      <header>
        <Link to="/journal">{t('journal.back')}</Link>
        <span>
          {formatDate(data.published_at)} / {t('journal.by')} {data.author}
        </span>
        <h1>{data.title}</h1>
        <p>{data.excerpt}</p>
      </header>
      <img src={data.cover_image || ''} alt="" />
      <div>
        {data.content
          .split('\n')
          .filter(Boolean)
          .map((text) => (
            <p key={text}>{text}</p>
          ))}
      </div>
    </article>
  )
}
