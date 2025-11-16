import { useState, useEffect } from 'react'

interface CacheEntry<T> {
  data: T
  timestamp: number
  ttl?: number
}

class MessageCache {
  private cache: Map<string, CacheEntry<any>> = new Map()

  set<T>(key: string, data: T, ttlMs: number = 3600000) {
    this.cache.set(key, {
      data,
      timestamp: Date.now(),
      ttl: ttlMs
    })
  }

  get<T>(key: string): T | null {
    const entry = this.cache.get(key)
    if (!entry) return null
    
    if (entry.ttl && Date.now() - entry.timestamp > entry.ttl) {
      this.cache.delete(key)
      return null
    }
    
    return entry.data as T
  }

  clear() {
    this.cache.clear()
  }

  remove(key: string) {
    this.cache.delete(key)
  }
}

export const messageCache = new MessageCache()

export function useMessageCache<T>(key: string, defaultValue: T, ttlMs?: number) {
  const [value, setValue] = useState<T>(() => {
    const cached = messageCache.get<T>(key)
    return cached !== null ? cached : defaultValue
  })

  useEffect(() => {
    messageCache.set(key, value, ttlMs)
  }, [value, key, ttlMs])

  return [value, setValue] as const
}

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: number | string
}

export function formatMessageTime(timestamp: number | string): string {
  if (typeof timestamp === 'string') return timestamp
  
  const date = new Date(timestamp)
  const now = new Date()
  
  // Same day
  if (date.toDateString() === now.toDateString()) {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }
  
  // Yesterday
  const yesterday = new Date(now)
  yesterday.setDate(yesterday.getDate() - 1)
  if (date.toDateString() === yesterday.toDateString()) {
    return `Yesterday ${date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`
  }
  
  // This week
  const weekAgo = new Date(now)
  weekAgo.setDate(weekAgo.getDate() - 7)
  if (date > weekAgo) {
    return date.toLocaleDateString([], { weekday: 'short', hour: '2-digit', minute: '2-digit' })
  }
  
  // Older
  return date.toLocaleDateString([], { month: 'short', day: 'numeric', year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined })
}

export function deduplicateMessages(messages: ChatMessage[]): ChatMessage[] {
  const seen = new Set<string>()
  return messages.filter(msg => {
    const key = `${msg.id}-${msg.content}`
    if (seen.has(key)) return false
    seen.add(key)
    return true
  })
}
