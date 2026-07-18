export interface ApiResponse<T> {
  data: T
  message: string
  meta?: Record<string, unknown>
  request_id: string | null
}

export interface ApiErrorResponse {
  data: null
  message: string
  error?: {
    code: string
    details?: Record<string, unknown>
  }
  errors?: Record<string, string[]>
  request_id?: string | null
}

export interface PaginationMeta {
  pagination: {
    current_page: number
    from: number | null
    last_page: number
    per_page: number
    to: number | null
    total: number
  }
}
