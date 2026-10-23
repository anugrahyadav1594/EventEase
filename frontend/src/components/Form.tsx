/** Small form helpers used by every modal form. */
import type { ReactNode } from 'react'

interface FieldProps {
  label: string
  error?: string
  children: ReactNode
  full?: boolean
}

export function Field({ label, error, children, full }: FieldProps) {
  return (
    <div className={`field ${full ? 'form-grid--full' : ''}`}>
      <label>{label}</label>
      {children}
      {error ? <span className="field__error">{error}</span> : null}
    </div>
  )
}

interface SelectFieldProps {
  label: string
  value: string
  onChange: (value: string) => void
  options: { value: string; label: string }[]
  full?: boolean
  required?: boolean
}

export function SelectField({ label, value, onChange, options, full, required }: SelectFieldProps) {
  return (
    <Field label={label} full={full}>
      <select value={value} onChange={(event) => onChange(event.target.value)} required={required}>
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
    </Field>
  )
}

interface InputFieldProps {
  label: string
  type?: string
  value: string | number
  onChange: (value: string) => void
  placeholder?: string
  required?: boolean
  min?: number
  step?: string
  full?: boolean
}

export function InputField({
  label,
  type = 'text',
  value,
  onChange,
  placeholder,
  required,
  min,
  step,
  full,
}: InputFieldProps) {
  return (
    <Field label={label} full={full}>
      <input
        type={type}
        value={value}
        min={min}
        step={step}
        placeholder={placeholder}
        required={required}
        onChange={(event) => onChange(event.target.value)}
      />
    </Field>
  )
}

interface TextAreaFieldProps {
  label: string
  value: string
  onChange: (value: string) => void
  rows?: number
  full?: boolean
}

export function TextAreaField({ label, value, onChange, rows = 3, full = true }: TextAreaFieldProps) {
  return (
    <Field label={label} full={full}>
      <textarea rows={rows} value={value} onChange={(event) => onChange(event.target.value)} />
    </Field>
  )
}
