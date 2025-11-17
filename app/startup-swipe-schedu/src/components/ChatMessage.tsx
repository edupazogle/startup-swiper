import { useState } from 'react'
import { motion } from 'framer-motion'
import { FileCopy, Check } from 'flowbite-react-icons/outline'

interface ChatMessageProps {
  role: 'user' | 'assistant'
  content: string
  timestamp?: string
  isLoading?: boolean
}

const messageVariants = {
  initial: {
    opacity: 0,
    y: 10,
    scale: 0.95
  },
  animate: {
    opacity: 1,
    y: 0,
    scale: 1,
    transition: {
      duration: 0.3
    }
  },
  exit: {
    opacity: 0,
    y: -10,
    scale: 0.95,
    transition: {
      duration: 0.2
    }
  }
}

export function ChatMessage({
  role,
  content,
  timestamp,
  isLoading
}: ChatMessageProps) {
  const isUser = role === 'user'
  const [copied, setCopied] = useState(false)

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(content)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch (err) {
      console.error('Failed to copy:', err)
    }
  }

  return (
    <motion.div
      variants={messageVariants}
      initial="initial"
      animate="animate"
      exit="exit"
      className={`flex w-full gap-2 ${isUser ? 'justify-end' : 'justify-start'}`}
      role="article"
      aria-label={`Message from ${role === 'user' ? 'you' : 'assistant'}`}
    >
      <div
        className={`max-w-[90%] sm:max-w-[85%] md:max-w-[75%] lg:max-w-[60%] rounded-lg px-3 sm:px-4 py-2 sm:py-3 group relative ${
          isUser
            ? 'bg-purple-500 text-white rounded-br-none'
            : 'bg-muted border border-border text-foreground rounded-bl-none'
        }`}
        role={isUser ? 'log' : 'status'}
        aria-live={isUser ? 'off' : 'polite'}
      >
        <p className="text-sm sm:text-base leading-relaxed whitespace-pre-wrap break-words">
          {content}
        </p>
        {timestamp && (
          <p className={`text-xs mt-2 ${isUser ? 'text-purple-100' : 'text-muted-foreground'}`}>
            <time>{timestamp}</time>
          </p>
        )}
        
        {!isUser && !isLoading && (
          <button
            onClick={handleCopy}
            className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity p-1 hover:bg-muted-foreground/10 rounded"
            aria-label="Copy message"
            title="Copy message"
          >
            {copied ? (
              <Check className="text-green-500 w-4 h-4"  />
            ) : (
              <FileCopy className="text-muted-foreground w-4 h-4"  />
            )}
          </button>
        )}
      </div>
    </motion.div>
  )
}
