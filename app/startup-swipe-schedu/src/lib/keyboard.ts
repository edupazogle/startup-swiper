export type KeyCombo = string

export interface Shortcut {
  key: KeyCombo
  description: string
  handler: () => void
}

export class KeyboardShortcuts {
  private shortcuts: Map<KeyCombo, () => void> = new Map()
  private listeners: Map<string, boolean> = new Map()

  constructor() {
    this.setupGlobalListener()
  }

  private setupGlobalListener() {
    const handleKeyDown = (e: KeyboardEvent) => {
      const combo = this.getKeyCombo(e)
      const handler = this.shortcuts.get(combo)
      
      if (handler) {
        e.preventDefault()
        handler()
      }
    }

    if (typeof window !== 'undefined') {
      window.addEventListener('keydown', handleKeyDown)
    }
  }

  private getKeyCombo(e: KeyboardEvent): string {
    const parts: string[] = []
    if (e.ctrlKey || e.metaKey) parts.push('Cmd')
    if (e.shiftKey) parts.push('Shift')
    if (e.altKey) parts.push('Alt')
    parts.push(e.key.length === 1 ? e.key.toUpperCase() : e.key)
    return parts.join('+')
  }

  register(combo: KeyCombo, handler: () => void) {
    this.shortcuts.set(combo, handler)
  }

  unregister(combo: KeyCombo) {
    this.shortcuts.delete(combo)
  }

  clear() {
    this.shortcuts.clear()
  }

  static getOSShortcutKey(): string {
    if (typeof navigator !== 'undefined') {
      if (navigator.platform.toUpperCase().indexOf('MAC') >= 0) {
        return '⌘'
      }
    }
    return 'Ctrl'
  }

  static getFormattedShortcut(combo: KeyCombo): string {
    const osKey = this.getOSShortcutKey()
    return combo.replace(/Cmd/g, osKey)
  }
}

export const defaultChatShortcuts = {
  submit: 'Enter',
  newline: 'Shift+Enter',
  clear: 'Cmd+K',
  export: 'Cmd+E',
  search: 'Cmd+F'
}

export function formatShortcut(combo: string): string {
  const isMac = typeof navigator !== 'undefined' && navigator.platform.toUpperCase().indexOf('MAC') >= 0
  
  if (isMac) {
    return combo
      .replace('Cmd', '⌘')
      .replace('Alt', '⌥')
      .replace('Shift', '⇧')
  } else {
    return combo
      .replace('Cmd', 'Ctrl')
      .replace('Alt', 'Alt')
      .replace('Shift', 'Shift')
  }
}

export function useKeyboardShortcuts(shortcuts: Record<string, () => void>) {
  if (typeof window === 'undefined') return

  const handleKeyDown = (e: KeyboardEvent) => {
    const combo = getEventKeyCombo(e)
    const handler = shortcuts[combo]
    
    if (handler) {
      e.preventDefault()
      handler()
    }
  }

  window.addEventListener('keydown', handleKeyDown)

  return () => window.removeEventListener('keydown', handleKeyDown)
}

function getEventKeyCombo(e: KeyboardEvent): string {
  const parts: string[] = []
  if (e.ctrlKey) parts.push('Ctrl')
  if (e.metaKey) parts.push('Cmd')
  if (e.shiftKey) parts.push('Shift')
  if (e.altKey) parts.push('Alt')
  
  const key = e.key.length === 1 ? e.key.toUpperCase() : e.key
  parts.push(key)
  
  return parts.join('+')
}
