import { useState, useEffect, useRef, useMemo } from 'react'
import { TailwindModal, TailwindModalHeader, TailwindModalBody, TailwindModalTitle, TailwindModalDescription } from '@/components/ui/tailwind-modal'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'
import { WandMagicSparkles, PaperPlane, User, Close, Lightbulb, CheckCircle, Star } from 'flowbite-react-icons/outline'
import { toast } from 'sonner'
import { cn } from '@/lib/utils'
import { fetchWithCache } from '@/lib/apiCache'
import { ModalSkeleton } from './ModalSkeleton'

const API_URL = import.meta.env.VITE_API_URL || 
  (typeof window !== 'undefined' && window.location.hostname === 'tilyn.ai' 
    ? 'https://tilyn.ai' 
    : 'http://localhost:8000')

// Helper function to render text with bold markdown (**text**)
const renderMessageContent = (content: string) => {
  const parts = content.split(/(\*\*.*?\*\*)/g)
  
  return parts.map((part, index) => {
    if (part.startsWith('**') && part.endsWith('**')) {
      const boldText = part.slice(2, -2)
      return <strong key={index} className="font-semibold">{boldText}</strong>
    }
    return part
  })
}

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
  const [messages, setMessages] = useState<Message[]>([])
  
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [hasStarted, setHasStarted] = useState(false) // Track if user clicked start
  
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
      setMessages([])
      setInput('')
      setSessionId(null)
      setIsLoading(false)
      setHasStarted(false)
      isInitialMount.current = true
    }
  }, [isOpen])

  // Generate session ID on open (don't call API automatically)
  useEffect(() => {
    if (isOpen && !sessionId) {
      const newSessionId = `insights_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
      setSessionId(newSessionId)
    }
  }, [isOpen])

  const startDebriefSession = async () => {
    const apiStartTime = performance.now()
    
    try {
      const url = `${API_URL}/insights/debrief/start`
      
      const data = await fetchWithCache(
        url,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            user_id: userId,
            startup_id: startupId || 'unknown',
            startup_name: startupName,
            meeting_prep_outline: 'Meeting insights debrief'
          })
        },
        `insights_debrief_${startupId}`,
        300000, // Cache for 5 minutes
        5000 // 5 second timeout
      )

      const apiDuration = performance.now() - apiStartTime
      console.log(`✅ Insights session API completed in ${apiDuration.toFixed(2)}ms`)

      if (data.success) {
        setSessionId(data.session_id)
        console.log('✅ Insights session started:', data.session_id)
      } else {
        console.warn('⚠️ Insights session API not available, using local mode')
        setSessionId(`local_${Date.now()}`)
      }
    } catch (error) {
      const apiDuration = performance.now() - apiStartTime
      console.error(`❌ Failed to start insights session after ${apiDuration.toFixed(2)}ms:`, error)
      
      if (error instanceof Error) {
        console.error('Error details:', {
          name: error.name,
          message: error.message,
          stack: error.stack
        })
      }
      
      console.warn('⚠️ Using local mode due to error')
      setSessionId(`local_${Date.now()}`)
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
      const response = await fetch(`${API_URL}/insights/debrief/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId,
          user_message: userMessage.content,
          startup_name: startupName,
          meeting_prep_outline: 'Meeting insights debrief',
          conversation_history: messages.map(m => ({
            role: m.role,
            content: m.content,
            timestamp: new Date(m.timestamp).toISOString()
          }))
        })
      })

      if (!response.ok) throw new Error('Failed to send message')
      
      const data = await response.json()
      
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.message || data.response,
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
    <TailwindModal isOpen={isOpen} onClose={onClose} size="xl" className="p-0 flex flex-col h-[90vh] max-h-[90vh]">
      {/* Header */}
      <div className="flex-shrink-0 border-b border-gray-700 dark:border-gray-700 bg-gray-800 dark:bg-gray-800 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="flex items-center justify-center w-10 h-10 rounded-lg bg-gradient-to-br from-purple-500 to-pink-600 shadow-md">
              <Lightbulb className="text-white w-5 h-5"  />
            </div>
            <div className="flex-1 min-w-0">
              <h2 className="text-lg font-bold text-white">
                Insights Debrief
              </h2>
              <p className="text-sm text-gray-300 truncate">
                {startupName}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Badge variant="outline" className="hidden sm:flex items-center gap-1.5 bg-green-50 dark:bg-green-950/30 border-green-200 dark:border-green-800 text-green-700 dark:text-green-400">
              <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
              Recording
            </Badge>
            <Button
              variant="ghost"
              size="icon"
              onClick={onClose}
              className="h-8 w-8 rounded-lg text-gray-400 hover:text-white hover:bg-gray-700"
            >
              <Close className="w-5 h-5"  />
            </Button>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div 
        ref={messagesContainerRef}
        className="flex-1 min-h-0 overflow-y-auto px-6 py-4 space-y-4 bg-gray-50 dark:bg-gray-900"
      >
          {/* Welcome Screen - Before Starting Session */}
          {!hasStarted && messages.length === 0 && (
            <div className="h-full flex items-center justify-center">
              <div className="max-w-md text-center space-y-6">
                <div className="w-16 h-16 bg-gradient-to-br from-purple-500 to-pink-600 rounded-2xl flex items-center justify-center mx-auto shadow-lg">
                  <Lightbulb className="w-8 h-8 text-white" />
                </div>
                <div className="space-y-2">
                  <h3 className="text-xl font-bold text-gray-900 dark:text-white">
                    AI Insights Debrief
                  </h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Start your debrief session for <span className="font-semibold text-gray-900 dark:text-white">{startupName}</span>. Share your observations and I'll help you organize them into actionable insights.
                  </p>
                </div>
                <Button
                  onClick={() => {
                    setHasStarted(true)
                    startDebriefSession()
                    // Add welcome message after starting
                    setMessages([{
                      id: '1',
                      role: 'assistant',
                      content: `👋 Welcome to your **${startupName}** debrief session!\n\nI'll help you capture and analyze insights from your meeting. Let's start with:\n\n• What were your key observations?\n• What stood out about their approach?\n• Any concerns or red flags?\n\nShare your thoughts, and I'll help you organize them into actionable insights.`,
                      timestamp: Date.now()
                    }])
                  }}
                  className="w-full bg-gradient-to-r from-purple-500 to-pink-600 hover:from-purple-600 hover:to-pink-700 text-white font-semibold py-3 rounded-lg shadow-md transition-all"
                  size="lg"
                >
                  <Lightbulb className="w-5 h-5 mr-2" />
                  Start Debrief Session
                </Button>
              </div>
            </div>
          )}
          
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
                  <WandMagicSparkles className="text-white w-5 h-5"  />
                </div>
              )}
              
              <div
                className={cn(
                  "max-w-[85%] rounded-2xl px-4 py-3 shadow-sm",
                  message.role === 'user'
                    ? 'bg-gradient-to-br from-purple-500 to-pink-600 text-white'
                    : 'bg-white/90 backdrop-blur-sm text-gray-900 border border-gray-200/50'
                )}
              >
                <div className="text-sm leading-relaxed whitespace-pre-wrap break-words">
                  {renderMessageContent(message.content)}
                </div>
                <div className={cn(
                  "text-xs mt-2",
                  message.role === 'user' 
                    ? 'text-purple-100' 
                    : 'text-gray-500'
                )}>
                  {new Date(message.timestamp).toLocaleTimeString([], { 
                    hour: '2-digit', 
                    minute: '2-digit' 
                  })}
                </div>
              </div>

              {message.role === 'user' && (
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center shadow-md">
                  <User className="text-white w-5 h-5"  />
                </div>
              )}
            </div>
          ))}

          {isLoading && (
            <div className="flex gap-3 justify-start">
              <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-purple-500 to-pink-600 flex items-center justify-center shadow-md">
                <WandMagicSparkles className="text-white w-5 h-5"  />
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
              className="flex-1 min-h-[44px] max-h-[120px] resize-none rounded-xl border-2 border-gray-300 dark:border-gray-600 focus:border-purple-500 focus:ring-2 focus:ring-purple-500 bg-white dark:bg-gray-900 text-gray-900 dark:text-white placeholder:text-gray-500 dark:placeholder:text-gray-400"
              rows={1}
              style={{ height: '44px' }}
            />
            <Button
              onClick={handleSend}
              disabled={!input.trim() || isLoading || !sessionId}
              className="h-11 w-11 rounded-xl bg-gradient-to-r from-purple-500 to-pink-600 hover:from-purple-600 hover:to-pink-700 text-white shadow-md disabled:opacity-50 disabled:cursor-not-allowed flex-shrink-0"
            >
              <PaperPlane size={20} weight="fill" />
            </Button>
          </div>
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-2 text-center">
            Press Enter to send, Shift+Enter for new line
          </p>
        </div>
    </TailwindModal>
  )
}
