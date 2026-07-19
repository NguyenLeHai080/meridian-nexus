import { zodResolver } from '@hookform/resolvers/zod'
import { useForm } from 'react-hook-form'
import { useTranslation } from 'react-i18next'
import { getApiErrorMessage } from '@/core/api/errors'
import { Button } from '@/shared/components/Button'
import { TextField } from '@/shared/components/TextField'
import { createLoginSchema, type LoginFormValues } from '../schemas/auth.schemas'
import { useLogin } from '../hooks/use-auth-mutations'

export function LoginForm() {
  const { t } = useTranslation('auth')
  const { passwordMutation, mfaMutation, challengeToken } = useLogin()
  const [mfaCode, setMfaCode] = useState('')
  const loginSchema = createLoginSchema(t)
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormValues>({
    resolver: zodResolver(loginSchema),
    defaultValues: { email: '', password: '' },
  })

  if (challengeToken !== null) {
    return (
      <form
        className="auth-form"
        onSubmit={(event) => {
          event.preventDefault()
          mfaMutation.mutate(mfaCode)
        }}
      >
        <p>{t('login.mfaText')}</p>
        <TextField
          label={t('login.mfaCode')}
          value={mfaCode}
          inputMode="numeric"
          autoComplete="one-time-code"
          onChange={(event) => setMfaCode(event.target.value)}
        />
        {mfaMutation.isError && (
          <div className="form-alert" role="alert">
            {getApiErrorMessage(mfaMutation.error)}
          </div>
        )}
        <Button type="submit" loading={mfaMutation.isPending}>
          {t('login.mfaSubmit')}
        </Button>
      </form>
    )
  }

  return (
    <form
      className="auth-form"
      onSubmit={handleSubmit((values) => passwordMutation.mutate(values))}
      noValidate
    >
      <TextField
        label={t('login.email')}
        type="email"
        autoComplete="email"
        error={errors.email?.message}
        {...register('email')}
      />
      <TextField
        label={t('login.password')}
        type="password"
        autoComplete="current-password"
        error={errors.password?.message}
        {...register('password')}
      />
      {passwordMutation.isError && (
        <div className="form-alert" role="alert">
          {getApiErrorMessage(passwordMutation.error)}
        </div>
      )}
      <Button type="submit" loading={passwordMutation.isPending}>
        {t('login.submit')}
      </Button>
    </form>
  )
}
import { useState } from 'react'
