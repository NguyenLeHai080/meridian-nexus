import { env } from '@/core/config/env'

type LogContext = Record<string, unknown>

function write(level: 'info' | 'warn' | 'error', message: string, context: LogContext = {}): void {
  if (!env.isDevelopment) {
    return
  }

  console[level](`[${level.toUpperCase()}] ${message}`, context)
}

export const logger = {
  info: (message: string, context?: LogContext) => write('info', message, context),
  warn: (message: string, context?: LogContext) => write('warn', message, context),
  error: (message: string, context?: LogContext) => write('error', message, context),
}
