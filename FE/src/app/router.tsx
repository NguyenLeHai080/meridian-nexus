import { createBrowserRouter, Navigate } from 'react-router-dom'
import { AdminRoute } from '@/core/auth/AdminRoute'
import { GuestRoute } from '@/core/auth/GuestRoute'
import { ProtectedRoute } from '@/core/auth/ProtectedRoute'
import { AdminLayout } from '@/shared/layouts/AdminLayout'
import { AuthLayout } from '@/shared/layouts/AuthLayout'
import { PublicLayout } from '@/shared/layouts/PublicLayout'
import { NotFoundPage } from '@/shared/pages/NotFoundPage'

export const router = createBrowserRouter([
  {
    element: <PublicLayout />,
    children: [
      {
        path: '/',
        lazy: async () => ({
          Component: (await import('@/modules/commerce/pages/HomePage')).HomePage,
        }),
      },
      {
        path: '/about',
        lazy: async () => ({
          Component: (await import('@/modules/commerce/pages/AboutPage')).AboutPage,
        }),
      },
      {
        path: '/products',
        lazy: async () => ({
          Component: (await import('@/modules/commerce/pages/ProductsPage')).ProductsPage,
        }),
      },
      {
        path: '/products/:slug',
        lazy: async () => ({
          Component: (await import('@/modules/commerce/pages/ProductDetailPage')).ProductDetailPage,
        }),
      },
      {
        path: '/contact',
        lazy: async () => ({
          Component: (await import('@/modules/commerce/pages/ContactPage')).ContactPage,
        }),
      },
      {
        path: '/journal',
        lazy: async () => ({
          Component: (await import('@/modules/commerce/pages/JournalPage')).JournalPage,
        }),
      },
      {
        path: '/journal/:slug',
        lazy: async () => ({
          Component: (await import('@/modules/commerce/pages/ArticlePage')).ArticlePage,
        }),
      },
      {
        path: '/checkout',
        lazy: async () => ({
          Component: (await import('@/modules/commerce/pages/CheckoutPage')).CheckoutPage,
        }),
      },
      {
        element: <ProtectedRoute />,
        children: [
          {
            path: '/profile',
            lazy: async () => ({
              Component: (await import('@/modules/commerce/pages/ProfilePage')).ProfilePage,
            }),
          },
        ],
      },
    ],
  },
  {
    element: <GuestRoute />,
    children: [
      {
        element: <AuthLayout />,
        children: [
          {
            path: '/login',
            lazy: async () => ({
              Component: (await import('@/modules/auth/pages/LoginPage')).LoginPage,
            }),
          },
          {
            path: '/register',
            lazy: async () => ({
              Component: (await import('@/modules/auth/pages/RegisterPage')).RegisterPage,
            }),
          },
        ],
      },
    ],
  },
  {
    element: <ProtectedRoute />,
    children: [
      { path: '/dashboard', element: <Navigate to="/admin" replace /> },
      { path: '/admin/dashboard', element: <Navigate to="/admin" replace /> },
      {
        element: <AdminRoute />,
        children: [
          {
            element: <AdminLayout />,
            children: [
              {
                path: '/admin',
                lazy: async () => ({
                  Component: (await import('@/modules/admin/pages/AdminDashboardPage'))
                    .AdminDashboardPage,
                }),
              },
              {
                path: '/admin/products',
                lazy: async () => ({
                  Component: (await import('@/modules/admin/pages/AdminProductsPage'))
                    .AdminProductsPage,
                }),
              },
              {
                path: '/admin/orders',
                lazy: async () => ({
                  Component: (await import('@/modules/admin/pages/AdminOrdersPage'))
                    .AdminOrdersPage,
                }),
              },
              {
                path: '/admin/promotions',
                lazy: async () => ({
                  Component: (await import('@/modules/admin/pages/AdminPromotionsPage'))
                    .AdminPromotionsPage,
                }),
              },
              {
                path: '/admin/content',
                lazy: async () => ({
                  Component: (await import('@/modules/admin/pages/AdminContentPage'))
                    .AdminContentPage,
                }),
              },
              {
                path: '/admin/users',
                lazy: async () => ({
                  Component: (await import('@/modules/admin/pages/AdminUsersPage')).AdminUsersPage,
                }),
              },
              {
                path: '/admin/chat',
                lazy: async () => ({
                  Component: (await import('@/modules/admin/pages/AdminChatPage')).AdminChatPage,
                }),
              },
            ],
          },
        ],
      },
    ],
  },
  { path: '*', element: <NotFoundPage /> },
])
