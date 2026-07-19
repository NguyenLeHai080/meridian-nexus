import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '@/core/auth/auth-store'
import { getPostLoginPath } from '@/core/auth/auth-navigation'
import {
  forgotPassword,
  confirmMfa,
  login,
  logout,
  register,
  resetPassword,
  setupMfa,
  verifyEmail,
  verifyMfa,
} from '../api/auth.api'
import type { ResetPasswordInput } from '../types/auth.types'

export function useLogin() {
  const setSession = useAuthStore((state) => state.setSession)
  const navigate = useNavigate()
  const [challengeToken, setChallengeToken] = useState<string | null>(null)

  const passwordMutation = useMutation({
    mutationFn: login,
    onSuccess: ({ user, mfa_required: mfaRequired, challenge_token: challenge }) => {
      if (mfaRequired && challenge !== null) {
        setChallengeToken(challenge)
        return
      }
      if (user === null) {
        return
      }
      setSession(user)
      navigate(getPostLoginPath(user), { replace: true })
    },
  })
  const mfaMutation = useMutation({
    mutationFn: (code: string) => verifyMfa(challengeToken || '', code),
    onSuccess: ({ user }) => {
      setSession(user)
      navigate(getPostLoginPath(user), { replace: true })
    },
  })
  return { passwordMutation, mfaMutation, challengeToken }
}

export function useRegister() {
  const setSession = useAuthStore((state) => state.setSession)
  const navigate = useNavigate()

  return useMutation({
    mutationFn: register,
    onSuccess: ({ user, verification_required: verificationRequired }) => {
      if (verificationRequired || user === null) {
        navigate('/verify-email-sent', { replace: true })
        return
      }
      setSession(user)
      navigate('/profile', { replace: true })
    },
  })
}

export function useVerifyEmail() {
  const setSession = useAuthStore((state) => state.setSession)
  const navigate = useNavigate()
  return useMutation({
    mutationFn: verifyEmail,
    onSuccess: ({ user }) => {
      setSession(user)
      navigate('/profile', { replace: true })
    },
  })
}

export const useForgotPassword = () => useMutation({ mutationFn: forgotPassword })

export const useResetPassword = () =>
  useMutation({ mutationFn: (input: ResetPasswordInput) => resetPassword(input) })

export const useSetupMfa = () => useMutation({ mutationFn: setupMfa })

export function useConfirmMfa() {
  const setUser = useAuthStore((state) => state.setUser)
  return useMutation({
    mutationFn: confirmMfa,
    onSuccess: ({ user }) => setUser(user),
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
