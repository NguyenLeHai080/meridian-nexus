import { useAuthStore } from '@/core/auth/auth-store'
import { ChatWidget } from '@/modules/commerce/components/ChatWidget'
import { useStorefrontHome } from '@/modules/commerce/hooks/use-commerce-data'
import { useCartStore } from '@/modules/commerce/store/cart-store'
import { PageLoader } from '@/shared/components/PageLoader'
import { StoreFooter } from './storefront/StoreFooter'
import { StoreHeader } from './storefront/StoreHeader'
import { StoreMain } from './storefront/StoreMain'

export function PublicLayout() {
  const user = useAuthStore((state) => state.user)
  const cartCount = useCartStore((state) => {
    let count = 0

    for (const item of state.items) {
      count += item.quantity
    }

    return count
  })
  const storefront = useStorefrontHome()

  if (storefront.data === undefined) {
    return <PageLoader />
  }

  const site = storefront.data.site

  return (
    <div className="storefront">
      <StoreHeader site={site} user={user} cartCount={cartCount} />
      <StoreMain />
      <StoreFooter site={site} />
      <ChatWidget />
    </div>
  )
}
