import { zodResolver } from '@hookform/resolvers/zod'
import { useForm } from 'react-hook-form'
import { useTranslation } from 'react-i18next'
import { getApiErrorMessage } from '@/core/api/errors'
import { Button } from '@/shared/components/Button'
import { TextField } from '@/shared/components/TextField'
import { createRegisterSchema, type RegisterFormValues } from '../schemas/auth.schemas'
import { useRegister } from '../hooks/use-auth-mutations'

export function RegisterForm() {
  const { t } = useTranslation('auth')
  const mutation = useRegister()
  const registerSchema = createRegisterSchema(t)
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<RegisterFormValues>({
    resolver: zodResolver(registerSchema),
    defaultValues: { name: '', email: '', password: '', password_confirmation: '' },
  })

  return (
    <form
      className="auth-form"
      onSubmit={handleSubmit((values) => mutation.mutate(values))}
      noValidate
    >
      <TextField
        label={t('register.name')}
        autoComplete="name"
        error={errors.name?.message}
        {...register('name')}
      />
      <TextField
        label={t('register.email')}
        type="email"
        autoComplete="email"
        error={errors.email?.message}
        {...register('email')}
      />
      <TextField
        label={t('register.password')}
        type="password"
        autoComplete="new-password"
        error={errors.password?.message}
        {...register('password')}
      />
      <TextField
        label={t('register.confirmPassword')}
        type="password"
        autoComplete="new-password"
        error={errors.password_confirmation?.message}
        {...register('password_confirmation')}
      />
      {mutation.isError && (
        <div className="form-alert" role="alert">
          {getApiErrorMessage(mutation.error)}
        </div>
      )}
      <Button type="submit" loading={mutation.isPending}>
        {t('register.submit')}
      </Button>
    </form>
  )
}
