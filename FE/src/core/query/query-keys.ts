export const queryKeys = {
  auth: {
    root: ['auth'] as const,
    currentUser: ['auth', 'current-user'] as const,
  },
  admin: {
    root: ['admin'] as const,
    metadata: ['admin', 'metadata'] as const,
    dashboard: ['admin', 'dashboard'] as const,
    products: ['admin', 'products'] as const,
    categories: ['admin', 'categories'] as const,
    orders: ['admin', 'orders'] as const,
    promotions: ['admin', 'promotions'] as const,
    users: ['admin', 'users'] as const,
    roles: ['admin', 'roles'] as const,
    conversations: ['admin', 'conversations'] as const,
    conversation: (id: number | null) => ['admin', 'conversations', id] as const,
    posts: ['admin', 'posts'] as const,
    contacts: ['admin', 'contacts'] as const,
  },
  commerce: {
    home: (language: string) => ['commerce', 'home', language] as const,
    products: (language: string, params?: { search?: string; category?: string }) =>
      ['commerce', 'products', language, params] as const,
    product: (language: string, slug?: string) => ['commerce', 'product', language, slug] as const,
    posts: (language: string) => ['commerce', 'posts', language] as const,
    post: (language: string, slug?: string) => ['commerce', 'post', language, slug] as const,
    customerOrders: ['commerce', 'customer-orders'] as const,
    chat: (token?: string | null) => ['commerce', 'chat', token] as const,
  },
} as const
