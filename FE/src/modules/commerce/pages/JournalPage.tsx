import { useTranslation } from 'react-i18next'
import { Link } from 'react-router-dom'
import { usePosts } from '../hooks/use-commerce-data'
import { formatDate } from '../utils/format'

export function JournalPage() {
  const { t } = useTranslation('storefront')
  const { data } = usePosts()

  return (
    <section className="journal-page">
      <header>
        <span className="store-kicker">{t('journal.eyebrow')}</span>
        <h1>{t('journal.title')}</h1>
      </header>
      <div className="journal-list">
        {data?.map((post, index) => (
          <article key={post.id}>
            <Link to={`/journal/${post.slug}`}>
              <img src={post.cover_image || ''} alt="" />
            </Link>
            <div>
              <span>
                0{index + 1} / {formatDate(post.published_at)}
              </span>
              <h2>
                <Link to={`/journal/${post.slug}`}>{post.title}</Link>
              </h2>
              <p>{post.excerpt}</p>
              <Link to={`/journal/${post.slug}`}>{t('journal.read')}</Link>
            </div>
          </article>
        ))}
      </div>
    </section>
  )
}
