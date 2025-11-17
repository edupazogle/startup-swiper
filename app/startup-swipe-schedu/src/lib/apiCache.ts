// Simple in-memory cache for API responses
interface CacheEntry<T> {
  data: T
  timestamp: number
}

class APICache {
  private cache = new Map<string, CacheEntry<any>>()
  private defaultTTL = 3600000 // 1 hour

  set<T>(key: string, data: T, ttl?: number): void {
    this.cache.set(key, {
      data,
      timestamp: Date.now()
    })
  }

  get<T>(key: string, ttl?: number): T | null {
    const entry = this.cache.get(key)
    if (!entry) return null

    const maxAge = ttl || this.defaultTTL
    const age = Date.now() - entry.timestamp

    if (age > maxAge) {
      this.cache.delete(key)
      return null
    }

    return entry.data as T
  }

  has(key: string, ttl?: number): boolean {
    return this.get(key, ttl) !== null
  }

  clear(): void {
    this.cache.clear()
  }

  delete(key: string): void {
    this.cache.delete(key)
  }

  // Clean up expired entries
  cleanup(): void {
    const now = Date.now()
    for (const [key, entry] of this.cache.entries()) {
      if (now - entry.timestamp > this.defaultTTL) {
        this.cache.delete(key)
      }
    }
  }
}

export const apiCache = new APICache()

// Auto cleanup every 5 minutes
if (typeof window !== 'undefined') {
  setInterval(() => apiCache.cleanup(), 300000)
}

// Utility function for fetch with timeout and caching
export async function fetchWithCache<T>(
  url: string,
  options: RequestInit = {},
  cacheKey?: string,
  cacheTTL?: number,
  timeout = 10000
): Promise<T> {
  // Check cache first
  const key = cacheKey || `${options.method || 'GET'}:${url}`
  const cached = apiCache.get<T>(key, cacheTTL)
  if (cached) {
    console.log(`✓ Cache hit: ${key}`)
    return cached
  }

  // Add timeout
  const controller = new AbortController()
  const timeoutId = setTimeout(() => controller.abort(), timeout)

  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal
    })

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`)
    }

    const data = await response.json()
    
    // Cache successful responses
    apiCache.set(key, data, cacheTTL)
    
    return data
  } catch (error) {
    if (error instanceof Error && error.name === 'AbortError') {
      throw new Error('Request timeout')
    }
    throw error
  } finally {
    clearTimeout(timeoutId)
  }
}
