'use client'

import { isNil } from 'lodash'
import type { ReactNode } from 'react'
import { createContext, useContext, useId, useMemo } from 'react'

type FormFieldContextValue = {
  htmlFor?: string
  required?: boolean
  error?: ReactNode
  disabled?: boolean
}

const FormFieldContext = createContext<FormFieldContextValue | null>(null)

const useFormField = () => {
  return useContext(FormFieldContext)
}

const FormFieldProvider = ({
  children,
  htmlFor,
  required,
  error,
  disabled,
}: FormFieldContextValue & { children: ReactNode }) => {
  const parentCtx = useFormField() || {}
  const generatedHtmlFor = `form-field-${useId()}`

  const value = useMemo(
    () => ({
      // New contexts should always generate new `htmlFor` ids
      htmlFor: htmlFor || generatedHtmlFor, // NOSONAR
      // A disabled parent should always disable its children, even when
      // disabled prop is explicitly set to false
      disabled: disabled || parentCtx?.disabled,
      // Allow overriding `required` and `error` from parent when prop is
      // explicitly set
      required: !isNil(required) ? required : parentCtx?.required,
      error: !isNil(error) ? error : parentCtx?.error,
    }),
    [
      disabled,
      parentCtx.disabled,
      required,
      parentCtx.required,
      error,
      parentCtx.error,
      htmlFor,
      generatedHtmlFor,
    ]
  )

  return <FormFieldContext.Provider value={value}>{children}</FormFieldContext.Provider>
}

export type { FormFieldContextValue }
export { FormFieldProvider, useFormField }
