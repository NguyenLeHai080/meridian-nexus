import { forwardRef, type InputHTMLAttributes } from 'react'

interface TextFieldProps extends InputHTMLAttributes<HTMLInputElement> {
  label: string
  error?: string
}

export const TextField = forwardRef<HTMLInputElement, TextFieldProps>(
  ({ label, error, id, ...inputProps }, ref) => {
    const inputId = id || inputProps.name
    let errorDescriptionId: string | undefined

    if (error) {
      errorDescriptionId = `${inputId}-error`
    }

    return (
      <label className="field" htmlFor={inputId}>
        <span className="field__label">{label}</span>
        <input
          {...inputProps}
          ref={ref}
          id={inputId}
          className="field__input"
          aria-invalid={Boolean(error)}
          aria-describedby={errorDescriptionId}
        />
        {error && (
          <span id={`${inputId}-error`} className="field__error">
            {error}
          </span>
        )}
      </label>
    )
  },
)

TextField.displayName = 'TextField'
