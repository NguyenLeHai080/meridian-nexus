import { Component, type ErrorInfo, type PropsWithChildren, type ReactNode } from 'react'
import { logger } from '@/core/observability/logger'
import { i18n } from '@/core/i18n/i18n'

interface State {
  hasError: boolean
}

export class AppErrorBoundary extends Component<PropsWithChildren, State> {
  public state: State = { hasError: false }

  public static getDerivedStateFromError(): State {
    return { hasError: true }
  }

  public componentDidCatch(error: Error, info: ErrorInfo): void {
    logger.error('Unhandled React render error.', {
      name: error.name,
      message: error.message,
      componentStack: info.componentStack,
    })
  }

  public render(): ReactNode {
    if (this.state.hasError) {
      return (
        <main className="not-found" role="alert">
          <span>{i18n.t('errors.eyebrow')}</span>
          <h1>{i18n.t('errors.title')}</h1>
          <button className="button" type="button" onClick={() => window.location.assign('/')}>
            {i18n.t('errors.reload')}
          </button>
        </main>
      )
    }

    return this.props.children
  }
}
