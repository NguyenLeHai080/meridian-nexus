import { useEffect } from 'react'

export function useHomeReveal() {
  useEffect(() => {
    const revealElements = document.querySelectorAll<HTMLElement>('[data-nail-reveal]')
    const revealObserver = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (!entry.isIntersecting) continue
          entry.target.classList.add('nail-reveal--visible')
          revealObserver.unobserve(entry.target)
        }
      },
      { threshold: 0.14 },
    )
    for (const element of revealElements) revealObserver.observe(element)

    const removeTiltListeners: Array<() => void> = []
    for (const element of document.querySelectorAll<HTMLElement>('[data-nail-tilt]')) {
      const handlePointerMove = (event: PointerEvent) => {
        const bounds = element.getBoundingClientRect()
        const rotateX = ((event.clientY - bounds.top) / bounds.height - 0.5) * -10
        const rotateY = ((event.clientX - bounds.left) / bounds.width - 0.5) * 10
        element.style.setProperty('--nail-tilt-x', `${rotateX.toFixed(2)}deg`)
        element.style.setProperty('--nail-tilt-y', `${rotateY.toFixed(2)}deg`)
      }
      const resetTilt = () => {
        element.style.setProperty('--nail-tilt-x', '0deg')
        element.style.setProperty('--nail-tilt-y', '0deg')
      }
      element.addEventListener('pointermove', handlePointerMove)
      element.addEventListener('pointerleave', resetTilt)
      removeTiltListeners.push(() => {
        element.removeEventListener('pointermove', handlePointerMove)
        element.removeEventListener('pointerleave', resetTilt)
      })
    }

    const counterObserver = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (!entry.isIntersecting) continue
          const element = entry.target as HTMLElement
          const target = Number(element.dataset.nailCount ?? 0)
          const startedAt = performance.now()
          const update = (time: number) => {
            const progress = Math.min((time - startedAt) / 1400, 1)
            element.textContent = Math.round(target * (1 - (1 - progress) ** 3)).toLocaleString()
            if (progress < 1) requestAnimationFrame(update)
          }
          requestAnimationFrame(update)
          counterObserver.unobserve(element)
        }
      },
      { threshold: 0.7 },
    )
    for (const element of document.querySelectorAll<HTMLElement>('[data-nail-count]')) {
      counterObserver.observe(element)
    }

    return () => {
      revealObserver.disconnect()
      counterObserver.disconnect()
      for (const removeListeners of removeTiltListeners) removeListeners()
    }
  }, [])
}
