import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function parseArray(value: unknown): string[] {
  if (Array.isArray(value)) {
    return value.filter(v => typeof v === 'string' && v.trim()).map(v => String(v).trim())
  }
  
  if (typeof value === 'string' && value) {
    let current = value
    // Handle double-encoded JSON (parse up to 2 times)
    for (let i = 0; i < 2; i++) {
      try {
        const parsed = JSON.parse(current)
        if (Array.isArray(parsed)) {
          return parsed.filter(v => v !== null && v !== undefined).map(v => String(v).trim()).filter(v => v)
        }
        // If parsed is a string, continue trying to parse it
        if (typeof parsed === 'string') {
          current = parsed
          continue
        }
      } catch {
        // Not JSON, break out
        break
      }
    }
    
    if (value.includes(',')) {
      return value.split(',').map(v => String(v).trim()).filter(v => v)
    }
    return [value.trim()].filter(v => v)
  }
  
  return []
}
