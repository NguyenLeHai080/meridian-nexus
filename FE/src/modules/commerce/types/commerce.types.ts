export interface Category {
  id: number
  name: string
  slug: string
  description: string
  products_count: number
  is_active?: boolean
}

export interface Product {
  id: number
  name: string
  slug: string
  sku: string
  excerpt: string | null
  description: string | null
  price: number
  sale_price: number | null
  stock: number
  images: string[]
  is_featured: boolean
  category: Pick<Category, 'id' | 'name' | 'slug'> | null
  published_at: string
}

export interface Promotion {
  id: number
  name: string
  code: string | null
  type: 'percent' | 'fixed'
  value: string
  minimum_order: string
  ends_at: string | null
  is_active: boolean
}

export interface Post {
  id: number
  title: string
  slug: string
  excerpt: string | null
  content: string
  cover_image: string | null
  author: string | null
  status: 'draft' | 'published' | 'archived'
  published_at: string | null
  created_at?: string
}

export interface OrderItem {
  id: number
  product_name: string
  sku: string
  unit_price: number
  quantity: number
  total: number
}

export interface Order {
  id: number
  number: string
  customer_name: string
  customer_email: string
  status: string
  payment_status: string
  subtotal: number
  discount: number
  shipping_fee: number
  total: number
  items: OrderItem[]
  created_at: string
}

export interface ConversationMessage {
  id: number
  sender_type: 'customer' | 'staff'
  body: string
  created_at: string
}

export interface Conversation {
  id: number
  token: string
  status: string
  customer: string
  assigned_to: string | null
  messages: ConversationMessage[]
  last_message_at: string
}

export interface StorefrontHome {
  locale: string
  supported_locales: SupportedLocaleOption[]
  site: StorefrontSite
  featured_products: Product[]
  categories: Category[]
  promotions: Promotion[]
  latest_posts: Post[]
}

export interface SupportedLocaleOption {
  value: string
  label: string
}

export interface StorefrontSite {
  brand: { name: string; mark: string }
  announcement: string
  navigation: { path: string; label: string }[]
  contact: { email: string }
  footer: {
    tagline: string
    newsletter_title: string
    newsletter_text: string
    legal: string
    note: string
  }
  home_hero: {
    eyebrow: string
    title: string
    accent: string
    description: string
    image: string
    image_alt: string
    cta_label: string
    cta_path: string
  }
}
