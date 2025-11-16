import { useEffect, useRef } from 'react'
import { AnimatePresence } from 'framer-motion'
import { ChatMessage } from './ChatMessage'
import { ThinkingBubble } from './ThinkingBubble'

export interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp?: string
}

interface ChatMessageListProps {
  messages: Message[]
  isLoading?: boolean
  showThinkingBubble?: boolean
  emptyStateMessage?: React.ReactNode
}

export function ChatMessageList({
  messages,
  isLoading,
  showThinkingBubble,
  emptyStateMessage
}: ChatMessageListProps) {
  const scrollRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (scrollRef.current) {
      const scrollElement = scrollRef.current
      setTimeout(() => {
        scrollElement.scrollTop = scrollElement.scrollHeight
      }, 0)
    }
  }, [messages, isLoading])

  return (
    <div
      ref={scrollRef}
      className="flex-1 overflow-y-auto px-3 sm:px-4 md:px-6 py-3 sm:py-4 md:py-6 space-y-3 sm:space-y-4 bg-background"
      role="log"
      aria-live="polite"
      aria-label="Chat messages"
    >
      {messages.length === 0 && emptyStateMessage && (
        <div className="flex items-center justify-center h-full text-center">
          <div className="text-muted-foreground max-w-xs">{emptyStateMessage}</div>
        </div>
      )}

      <AnimatePresence mode="popLayout">
        {messages.map((message) => (
          <ChatMessage
            key={message.id}
            role={message.role}
            content={message.content}
            timestamp={message.timestamp}
          />
        ))}

        {isLoading && showThinkingBubble && (
          <div key="thinking-bubble" className="flex justify-start">
            <div className="bg-muted border border-border rounded-lg px-4 py-3 rounded-bl-none">
              <ThinkingBubble size="md" />
            </div>
          </div>
        )}
      </AnimatePresence>
    </div>
  )
}
