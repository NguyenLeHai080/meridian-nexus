import { useMutation } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '@/core/auth/auth-store'
import { getPostLoginPath } from '@/core/auth/auth-navigation'
import { login, logout, register } from '../api/auth.api'

export function useLogin() {
  const setSession = useAuthStore((state) => state.setSession)
  const navigate = useNavigate()

  return useMutation({
    mutationFn: login,
    onSuccess: ({ user }) => {
      setSession(user)
      navigate(getPostLoginPath(user), { replace: true })
    },
  })
}

export function useRegister() {
  const setSession = useAuthStore((state) => state.setSession)
  const navigate = useNavigate()

  return useMutation({
    mutationFn: register,
    onSuccess: ({ user }) => {
      setSession(user)
      navigate('/profile', { replace: true })
    },
  })
}

export function useLogout() {
  const clearSession = useAuthStore((state) => state.clearSession)
  const navigate = useNavigate()

  return useMutation({
    mutationFn: logout,
    onSettled: () => {
      clearSession()
      navigate('/login', { replace: true })
    },
  })
}
