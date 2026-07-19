export const queryKeys = {
  auth: {
    root: ['auth'] as const,
    currentUser: ['auth', 'current-user'] as const,
  },
  admin: {
    root: ['admin'] as const,
    metadata: ['admin', 'metadata'] as const,
    dashboard: ['admin', 'dashboard'] as const,
    products: (page?: number) => {
      if (page === undefined) {
        return ['admin', 'products'] as const
      }
      return ['admin', 'products', page] as const
    },
    categories: ['admin', 'categories'] as const,
    orders: (page?: number) => {
      if (page === undefined) {
        return ['admin', 'orders'] as const
      }
      return ['admin', 'orders', page] as const
    },
    promotions: ['admin', 'promotions'] as const,
    users: (page?: number) => {
      if (page === undefined) {
        return ['admin', 'users'] as const
      }
      return ['admin', 'users', page] as const
    },
    roles: ['admin', 'roles'] as const,
    conversations: (page?: number) => {
      if (page === undefined) {
        return ['admin', 'conversations'] as const
      }
      return ['admin', 'conversations', page] as const
    },
    conversation: (id: number | null) => ['admin', 'conversations', id] as const,
    posts: (page?: number) => {
      if (page === undefined) {
        return ['admin', 'posts'] as const
      }
      return ['admin', 'posts', page] as const
    },
    contacts: (page?: number) => {
      if (page === undefined) {
        return ['admin', 'contacts'] as const
      }
      return ['admin', 'contacts', page] as const
    },
  },
  commerce: {
    home: (language: string) => ['commerce', 'home', language] as const,
    products: (language: string, params?: { search?: string; category?: string }) =>
      ['commerce', 'products', language, params] as const,
    product: (language: string, slug?: string) => ['commerce', 'product', language, slug] as const,
    posts: (language: string) => ['commerce', 'posts', language] as const,
    post: (language: string, slug?: string) => ['commerce', 'post', language, slug] as const,
    customerOrders: (page?: number) => {
      if (page === undefined) {
        return ['commerce', 'customer-orders'] as const
      }
      return ['commerce', 'customer-orders', page] as const
    },
    chat: (token?: string | null) => ['commerce', 'chat', token] as const,
  },
} as const
