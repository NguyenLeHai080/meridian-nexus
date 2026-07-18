import { describe, expect, it } from 'vitest'

const coreSources = import.meta.glob('/src/core/**/*.{ts,tsx}', {
  eager: true,
  import: 'default',
  query: '?raw',
}) as Record<string, string>

const layoutSources = import.meta.glob('/src/shared/layouts/**/*.{ts,tsx}', {
  eager: true,
  import: 'default',
  query: '?raw',
}) as Record<string, string>

const frontendSources = import.meta.glob('/src/**/*.{ts,tsx}', {
  eager: true,
  import: 'default',
  query: '?raw',
}) as Record<string, string>

describe('core architecture', () => {
  it('does not depend on feature modules', () => {
    const violations = Object.entries(coreSources)
      .filter(([file]) => !file.endsWith('.test.ts') && !file.endsWith('.test.tsx'))
      .filter(([, source]) => source.includes('@/modules/') || source.includes('/modules/'))
      .map(([file]) => file)

    expect(violations).toEqual([])
  })

  it('keeps shared layouts readable without ternary expressions', () => {
    const violations: string[] = []

    for (const [file, source] of Object.entries(layoutSources)) {
      if (/\s\?\s/.test(source)) {
        violations.push(file)
      }
    }

    expect(violations).toEqual([])
  })

  it('does not use ternary expressions in frontend source', () => {
    const violations: string[] = []

    for (const [file, source] of Object.entries(frontendSources)) {
      if (/\s\?\s/.test(source)) {
        violations.push(file)
      }
    }

    expect(violations).toEqual([])
  })
})
