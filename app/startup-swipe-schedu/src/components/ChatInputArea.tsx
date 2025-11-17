import { useEffect, useRef } from 'react'
import { PaperPlane } from 'flowbite-react-icons/outline'
import { motion } from 'framer-motion'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'

interface ChatInputAreaProps {
  value: string
  onChange: (value: string) => void
  onSubmit: (message: string) => void
  isLoading?: boolean
  placeholder?: string
  minRows?: number
  maxRows?: number
}

export function ChatInputArea({
  value,
  onChange,
  onSubmit,
  isLoading,
  placeholder = 'Ask a question...',
  minRows = 2,
  maxRows = 5
}: ChatInputAreaProps) {
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  // Auto-expand textarea based on content
  useEffect(() => {
    const textarea = textareaRef.current
    if (!textarea) return

    textarea.style.height = 'auto'
    const scrollHeight = Math.min(
      textarea.scrollHeight,
      parseInt(window.getComputedStyle(textarea).lineHeight) * maxRows
    )
    textarea.style.height = `${Math.max(scrollHeight, parseInt(window.getComputedStyle(textarea).lineHeight) * minRows)}px`
  }, [value, minRows, maxRows])

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      if (value.trim() && !isLoading) {
        onSubmit(value.trim())
      }
    }
  }

  const handleSubmit = () => {
    if (value.trim() && !isLoading) {
      onSubmit(value.trim())
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="px-3 sm:px-4 md:px-6 py-2 sm:py-2.5 border-t border-border bg-background space-y-1"
    >
      <div className="flex gap-1.5 sm:gap-2 items-end">
        <div className="flex-1 min-w-0">
          <label htmlFor="message-input" className="sr-only">
            Message input
          </label>
          <Textarea
            id="message-input"
            ref={textareaRef}
            value={value}
            onChange={(e) => onChange(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            disabled={isLoading}
            rows={minRows}
            className="resize-none text-xs sm:text-sm focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-0"
            aria-label="Message input field"
            aria-disabled={isLoading}
          />
        </div>
        <Button
          onClick={handleSubmit}
          disabled={!value.trim() || isLoading}
          size="icon"
          className="flex-shrink-0 h-9 w-9 bg-purple-600 hover:bg-purple-700 text-white"
          aria-label="Send message"
          aria-disabled={!value.trim() || isLoading}
        >
          <PaperPlane className="w-4 h-4"  />
        </Button>
      </div>
      <p className="text-[10px] text-muted-foreground px-1">
        Shift + Enter for new line
      </p>
    </motion.div>
  )
}
