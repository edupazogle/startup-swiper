import { useState, useEffect, useRef, useMemo } from 'react'
import { Dialog, DialogContent } from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'
import { 
  Sparkle, 
  PaperPlaneTilt, 
  Robot, 
  User, 
  X,
  Lightbulb,
  CheckCircle,
  Star
} from '@phosphor-icons/react'
import { toast } from 'sonner'
import { cn } from '@/lib/utils'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: number
}

interface ImprovedInsightsModalNewProps {
  isOpen: boolean
  onClose: () => void
  userId: string
  startupId?: string
  startupName: string
  startupDescription: string
}

export function ImprovedInsightsModalNew({
  isOpen,
  onClose,
  userId,
  startupId,
  startupName,
  startupDescription
}: ImprovedInsightsModalNewProps) {
  // Memoize welcome message to prevent recalculation
  const welcomeMessage = useMemo(() => 
    `👋 Welcome to your **${startupName}** debrief session!

I'll help you capture and analyze insights from your meeting. Let's start with:

• What were your key observations?
• What stood out about their approach?
• Any concerns or red flags?

Share your thoughts, and I'll help you organize them into actionable insights.`,
    [startupName]
  )

  const [messages, setMessages] = useState<Message[]>([{
    id: '1',
    role: 'assistant',
    content: welcomeMessage,
    timestamp: Date.now()
  }])
  
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [sessionId, setSessionId] = useState<string | null>(null)
  
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const messagesContainerRef = useRef<HTMLDivElement>(null)
  const textareaRef = useRef<HTMLTextAreaElement>(null)
  const isInitialMount = useRef(true)

  // Scroll to bottom on mount and new messages
  useEffect(() => {
    if (messagesContainerRef.current) {
      if (isInitialMount.current) {
        messagesContainerRef.current.scrollTop = messagesContainerRef.current.scrollHeight
        isInitialMount.current = false
      } else {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
      }
    }
  }, [messages])

  // Auto-resize textarea with debounce
  useEffect(() => {
    if (textareaRef.current && input) {
      // Use RAF for smooth resizing
      requestAnimationFrame(() => {
        if (textareaRef.current) {
          textareaRef.current.style.height = '44px'
          const newHeight = Math.min(textareaRef.current.scrollHeight, 120)
          textareaRef.current.style.height = `${newHeight}px`
        }
      })
    }
  }, [input])

  // Reset on close
  useEffect(() => {
    if (!isOpen) {
      setMessages([{
        id: '1',
        role: 'assistant',
        content: welcomeMessage,
        timestamp: Date.now()
      }])
      setInput('')
      setSessionId(null)
      setIsLoading(false)
      isInitialMount.current = true
    }
  }, [isOpen])

  // Start session automatically
  useEffect(() => {
    if (isOpen && !sessionId) {
      startDebriefSession()
    }
  }, [isOpen])

  const startDebriefSession = async () => {
    try {
      const response = await fetch(`${API_URL}/insights/session/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: userId,
          startup_id: startupId || 'unknown',
          startup_name: startupName,
          startup_description: startupDescription
        })
      })

      if (!response.ok) throw new Error('Failed to start session')
      
      const data = await response.json()
      setSessionId(data.session_id)
      console.log('✓ Insights session started:', data.session_id)
    } catch (error) {
      console.error('Failed to start insights session:', error)
      toast.error('Failed to start debrief session')
    }
  }

  const handleSend = async () => {
    if (!input.trim() || isLoading || !sessionId) return

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input.trim(),
      timestamp: Date.now()
    }

    setMessages(prev => [...prev, userMessage])
    setInput('')
    setIsLoading(true)

    try {
      const response = await fetch(`${API_URL}/insights/debrief/message`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId,
          user_message: userMessage.content
        })
      })

      if (!response.ok) throw new Error('Failed to send message')
      
      const data = await response.json()
      
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.response,
        timestamp: Date.now()
      }

      setMessages(prev => [...prev, assistantMessage])
    } catch (error) {
      console.error('Failed to send message:', error)
      toast.error('Failed to send message')
      
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: Date.now()
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent 
        className="max-w-3xl h-[80vh] md:h-[80vh] h-screen md:rounded-lg rounded-none p-0 gap-0 flex flex-col w-full max-w-full md:max-w-3xl"
        aria-describedby="insights-description"
      >
        {/* Header */}
        <div className="flex-shrink-0 border-b border-gray-700 dark:border-gray-700 bg-gray-800 dark:bg-gray-800 px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="flex items-center justify-center w-10 h-10 rounded-lg bg-gradient-to-br from-purple-500 to-pink-600 shadow-md">
                <Lightbulb size={20} weight="fill" className="text-white" />
              </div>
              <div className="flex-1 min-w-0">
                <h2 id="insights-title" className="text-lg font-bold text-white">
                  Insights Debrief
                </h2>
                <p id="insights-description" className="text-sm text-gray-300 truncate">
                  {startupName}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Badge variant="outline" className="hidden sm:flex items-center gap-1.5 bg-green-500/10 border-green-500/30 text-green-400">
                <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
                Recording
              </Badge>
              <Button
                variant="ghost"
                size="icon"
                onClick={onClose}
                className="h-8 w-8 rounded-lg text-gray-400 hover:text-white hover:bg-gray-700"
              >
                <X size={18} />
              </Button>
            </div>
          </div>
        </div>

        {/* Messages */}
        <div 
          ref={messagesContainerRef}
          className="flex-1 min-h-0 overflow-y-auto px-6 py-4 space-y-4 bg-gray-50 dark:bg-gray-900"
        >
          {messages.map((message) => (
            <div
              key={message.id}
              className={cn(
                "flex gap-3",
                message.role === 'user' ? 'justify-end' : 'justify-start'
              )}
            >
              {message.role === 'assistant' && (
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-purple-500 to-pink-600 flex items-center justify-center shadow-md">
                  <Robot size={18} weight="fill" className="text-white" />
                </div>
              )}
              
              <div
                className={cn(
                  "max-w-[85%] rounded-2xl px-4 py-3 shadow-sm",
                  message.role === 'user'
                    ? 'bg-gradient-to-br from-purple-500 to-purple-600 text-white'
                    : 'bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 border border-gray-200 dark:border-gray-700'
                )}
              >
                <div className="text-sm leading-relaxed whitespace-pre-wrap break-words">
                  {message.content}
                </div>
                <div className={cn(
                  "text-xs mt-2",
                  message.role === 'user' 
                    ? 'text-purple-100' 
                    : 'text-gray-500 dark:text-gray-400'
                )}>
                  {new Date(message.timestamp).toLocaleTimeString([], { 
                    hour: '2-digit', 
                    minute: '2-digit' 
                  })}
                </div>
              </div>

              {message.role === 'user' && (
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gray-200 dark:bg-gray-700 flex items-center justify-center">
                  <User size={18} weight="fill" className="text-gray-600 dark:text-gray-300" />
                </div>
              )}
            </div>
          ))}

          {isLoading && (
            <div className="flex gap-3 justify-start">
              <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-purple-500 to-pink-600 flex items-center justify-center shadow-md">
                <Robot size={18} weight="fill" className="text-white" />
              </div>
              <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl px-4 py-3 shadow-sm">
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="flex-shrink-0 border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 px-6 py-4">
          <div className="flex gap-3 items-end">
            <Textarea
              ref={textareaRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Share your insights..."
              disabled={isLoading}
              className="flex-1 min-h-[44px] max-h-[120px] resize-none rounded-xl border-gray-300 dark:border-gray-600 focus:border-purple-500 dark:focus:border-purple-500 focus:ring-purple-500 bg-white dark:bg-gray-900 text-gray-900 dark:text-white placeholder:text-gray-500 dark:placeholder:text-gray-400"
              rows={1}
              style={{ height: '44px' }}
            />
            <Button
              onClick={handleSend}
              disabled={!input.trim() || isLoading || !sessionId}
              className="h-11 w-11 rounded-xl bg-gradient-to-r from-purple-500 to-purple-600 hover:from-purple-600 hover:to-purple-700 text-white shadow-md disabled:opacity-50 disabled:cursor-not-allowed flex-shrink-0"
            >
              <PaperPlaneTilt size={20} weight="fill" />
            </Button>
          </div>
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-2 text-center">
            Press Enter to send, Shift+Enter for new line
          </p>
        </div>
      </DialogContent>
    </Dialog>
  )
}
