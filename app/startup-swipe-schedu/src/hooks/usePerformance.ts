import { useCallback, useRef } from 'react'

/**
 * Custom hook to debounce function calls
 * Useful for preventing rapid modal opens or API calls
 */
export function useDebounce<T extends (...args: any[]) => any>(
  callback: T,
  delay: number
): (...args: Parameters<T>) => void {
  const timeoutRef = useRef<NodeJS.Timeout>()

  return useCallback(
    (...args: Parameters<T>) => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current)
      }

      timeoutRef.current = setTimeout(() => {
        callback(...args)
      }, delay)
    },
    [callback, delay]
  )
}

/**
 * Custom hook to throttle function calls
 * Ensures function is called at most once per specified time
 */
export function useThrottle<T extends (...args: any[]) => any>(
  callback: T,
  delay: number
): (...args: Parameters<T>) => void {
  const lastRun = useRef(Date.now())

  return useCallback(
    (...args: Parameters<T>) => {
      const now = Date.now()

      if (now - lastRun.current >= delay) {
        callback(...args)
        lastRun.current = now
      }
    },
    [callback, delay]
  )
}

/**
 * Custom hook to prevent rapid successive calls
 * Useful for preventing double-clicks on modal open buttons
 */
export function usePreventRapidFire(delay = 1000) {
  const isActiveRef = useRef(false)

  const withPreventRapidFire = useCallback(
    <T extends (...args: any[]) => any>(callback: T) => {
      return (...args: Parameters<T>) => {
        if (isActiveRef.current) {
          console.log('Rapid fire prevented')
          return
        }

        isActiveRef.current = true
        callback(...args)

        setTimeout(() => {
          isActiveRef.current = false
        }, delay)
      }
    },
    [delay]
  )

  return withPreventRapidFire
}
