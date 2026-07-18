import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { Link, useNavigate } from 'react-router-dom'
import { useAuthStore } from '@/core/auth/auth-store'
import { getApiErrorMessage } from '@/core/api/errors'
import { useCheckout } from '../hooks/use-commerce-data'
import { useCartStore } from '../store/cart-store'
import { formatMoney } from '../utils/format'

export function CheckoutPage() {
  const { t } = useTranslation('storefront')
  const user = useAuthStore((state) => state.user)
  const items = useCartStore((state) => state.items)
  const remove = useCartStore((state) => state.remove)
  const clear = useCartStore((state) => state.clear)
  const navigate = useNavigate()
  const [promotion, setPromotion] = useState('')
  let total = 0

  for (const item of items) {
    let price = item.product.price
    if (item.product.sale_price !== null) {
      price = item.product.sale_price
    }
    total += price * item.quantity
  }

  const mutation = useCheckout(() => {
    clear()
    navigate('/profile')
  })

  if (items.length === 0) {
    return (
      <section className="empty-cart">
        <span>{t('checkout.emptyEyebrow')}</span>
        <h1>{t('checkout.emptyTitle')}</h1>
        <p>{t('checkout.emptyText')}</p>
        <Link className="store-button" to="/products">
          {t('checkout.browse')}
        </Link>
      </section>
    )
  }

  let shippingLabel = '$8.00'
  if (total >= 100) {
    shippingLabel = t('checkout.free')
  }

  let checkoutContent = (
    <div className="checkout-login">
      <p>{t('checkout.loginText')}</p>
      <Link className="store-button store-button--wide" to="/login">
        {t('checkout.login')}
      </Link>
    </div>
  )

  if (user !== null) {
    checkoutContent = (
      <form
        onSubmit={(event) => {
          event.preventDefault()
          const values = Object.fromEntries(new FormData(event.currentTarget)) as Record<
            string,
            string
          >
          mutation.mutate({
            items: items.map((item) => ({ product_id: item.product.id, quantity: item.quantity })),
            phone: values.phone,
            address: { line: values.line, city: values.city, country: values.country },
            promotion_code: promotion || undefined,
          })
        }}
      >
        <label>
          {t('checkout.phone')}
          <input name="phone" required />
        </label>
        <label>
          {t('checkout.address')}
          <input name="line" required />
        </label>
        <label>
          {t('checkout.city')}
          <input name="city" required />
        </label>
        <label>
          {t('checkout.country')}
          <input name="country" defaultValue="Vietnam" required />
        </label>
        {mutation.isError && <div className="form-alert">{getApiErrorMessage(mutation.error)}</div>}
        <button className="store-button store-button--wide" disabled={mutation.isPending}>
          {t('checkout.placeOrder')}
        </button>
      </form>
    )
  }

  return (
    <section className="checkout-page">
      <header>
        <span className="store-kicker">{t('checkout.eyebrow')}</span>
        <h1>{t('checkout.title')}</h1>
      </header>
      <div className="checkout-grid">
        <div className="cart-lines">
          {items.map((item) => {
            let price = item.product.price
            if (item.product.sale_price !== null) {
              price = item.product.sale_price
            }

            return (
              <article key={item.product.id}>
                <img src={item.product.images[0]} alt="" />
                <div>
                  <small>{item.product.sku}</small>
                  <h2>{item.product.name}</h2>
                  <p>
                    {t('checkout.quantity')}: {item.quantity}
                  </p>
                  <button onClick={() => remove(item.product.id)}>{t('checkout.remove')}</button>
                </div>
                <strong>{formatMoney(price * item.quantity)}</strong>
              </article>
            )
          })}
        </div>
        <aside>
          <h2>{t('checkout.summary')}</h2>
          <p>
            <span>{t('checkout.subtotal')}</span>
            <strong>{formatMoney(total)}</strong>
          </p>
          <p>
            <span>{t('checkout.shipping')}</span>
            <strong>{shippingLabel}</strong>
          </p>
          <div className="promo-input">
            <input
              placeholder={t('checkout.promotion')}
              value={promotion}
              onChange={(event) => setPromotion(event.target.value.toUpperCase())}
            />
          </div>
          {checkoutContent}
        </aside>
      </div>
    </section>
  )
}
