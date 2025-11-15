import { useEffect, useState } from 'react'

export function useKV<T>(key: string, initial: T): [T, (value: T | ((prev: T) => T)) => void] {
  const read = () => {
    try {
      const raw = localStorage.getItem(key)
      return raw ? (JSON.parse(raw) as T) : initial
    } catch {
      return initial
    }
  }

  const [value, setValue] = useState<T>(read)

  useEffect(() => {
    try {
      localStorage.setItem(key, JSON.stringify(value))
    } catch {
      /* ignore */
    }
  }, [key, value])

  const setter = (next: T | ((prev: T) => T)) => {
    setValue((prev) => (typeof next === 'function' ? (next as (p: T) => T)(prev) : next))
  }

  return [value, setter]
}
