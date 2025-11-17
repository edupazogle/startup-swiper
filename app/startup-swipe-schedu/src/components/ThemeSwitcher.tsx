import { useEffect, useState } from 'react'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Button } from '@/components/ui/button'
import { Moon, Sun } from 'flowbite-react-icons/outline'

const THEMES = [
  'corporate',
  'light',
  'dark',
  'cupertino',
  'emerald',
  'sunrise',
  'sunset',
  'ocean',
  'forest',
  'desert',
  'night',
  'cyberpunk'
]

const STORAGE_KEY = 'app-theme'

export function ThemeSwitcher() {
  const [theme, setTheme] = useState<string>(() => {
    const stored = typeof window !== 'undefined' ? localStorage.getItem(STORAGE_KEY) : null
    return stored || document.documentElement.getAttribute('data-theme') || 'ocean'
  })

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
    localStorage.setItem(STORAGE_KEY, theme)
  }, [theme])

  const toggleDarkLight = () => {
    setTheme(prev => (prev === 'dark' ? 'light' : 'dark'))
  }

  return (
    <div className="flex items-center gap-2">
      <Select value={theme} onValueChange={setTheme}>
        <SelectTrigger className="h-8 w-[140px]">
          <SelectValue placeholder="Theme" />
        </SelectTrigger>
        <SelectContent>
          {THEMES.map(t => (
            <SelectItem key={t} value={t}>
              {t.charAt(0).toUpperCase() + t.slice(1)}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
      <Button
        size="icon"
        variant="outline"
        aria-label="Toggle dark/light"
        onClick={toggleDarkLight}
        className="h-8 w-8"
      >
        {theme === 'dark' ? <Sun className="w-4 h-4"  /> : <Moon className="w-4 h-4"  />}
      </Button>
    </div>
  )
}

export default ThemeSwitcher