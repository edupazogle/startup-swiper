import { useState, useEffect, useRef, useMemo, useCallback } from 'react'
import { Dialog, DialogContent } from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'
import { 
  Briefcase, 
  PaperPlaneTilt, 
  Robot, 
  User, 
  X,
  Lightbulb,
  Question,
  Target,
  ArrowClockwise
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

interface ImprovedMeetingModalNewProps {
  isOpen: boolean
  onClose: () => void
  userId: string
  startup?: any
  startupId?: string
  startupName?: string
  startupDescription?: string
}

export function ImprovedMeetingModalNew({
  isOpen,
  onClose,
  userId,
  startup,
  startupId: propStartupId,
  startupName: propStartupName,
  startupDescription: propStartupDescription
}: ImprovedMeetingModalNewProps) {
  const startupId = startup?.id || propStartupId || 'unknown'
  const startupName = startup?.name || startup?.['Company Name'] || propStartupName || 'Unknown Startup'
  const startupDescription = startup?.description || startup?.['Company Description'] || propStartupDescription || 'No description provided'
  
  const welcomeMessage = useMemo(() => 
    `👋 Let's prepare for your meeting with **${startupName}**!

I'll help you create:
• Key talking points and discussion topics
• Critical questions to ask
• Strategic recommendations

What would you like to focus on? Or I can generate a comprehensive meeting outline for you.`,
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
  const [sessionId, setSessionId] = useState<string>('')
  
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

  // Auto-resize textarea with RAF
  useEffect(() => {
    if (textareaRef.current && input) {
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
      setSessionId('')
      setIsLoading(false)
      isInitialMount.current = true
    }
  }, [isOpen])

  // Generate session ID
  useEffect(() => {
    if (isOpen && !sessionId) {
      setSessionId(`meeting_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`)
    }
  }, [isOpen])

  const generateMeetingOutline = async () => {
    if (isLoading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: 'Generate a comprehensive meeting outline',
      timestamp: Date.now()
    }

    setMessages(prev => [...prev, userMessage])
    setIsLoading(true)

    try {
      const response = await fetch(`${API_URL}/meeting-prep/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId,
          user_id: userId,
          startup_id: startupId,
          startup_name: startupName,
          startup_description: startupDescription
        })
      })

      if (!response.ok) throw new Error('Failed to generate outline')
      
      const data = await response.json()
      
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.outline || data.response,
        timestamp: Date.now()
      }

      setMessages(prev => [...prev, assistantMessage])
      toast.success('Meeting outline generated!')
    } catch (error) {
      console.error('Failed to generate outline:', error)
      toast.error('Failed to generate meeting outline')
      
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'Sorry, I encountered an error generating the outline. Please try again or ask me specific questions.',
        timestamp: Date.now()
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const handleSend = async () => {
    if (!input.trim() || isLoading) return

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
      const response = await fetch(`${API_URL}/meeting-prep/message`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId,
          user_id: userId,
          startup_id: startupId,
          startup_name: startupName,
          startup_description: startupDescription,
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
        aria-describedby="meeting-description"
      >
        {/* Header */}
        <div className="flex-shrink-0 border-b border-gray-700 dark:border-gray-700 bg-gray-800 dark:bg-gray-800 px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="flex items-center justify-center w-10 h-10 rounded-lg bg-gradient-to-br from-blue-500 to-indigo-600 shadow-md">
                <Briefcase size={20} weight="fill" className="text-white" />
              </div>
              <div className="flex-1 min-w-0">
                <h2 id="meeting-title" className="text-lg font-bold text-white">
                  Meeting Preparation
                </h2>
                <p id="meeting-description" className="text-sm text-gray-300 truncate">
                  {startupName}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Badge variant="outline" className="hidden sm:flex items-center gap-1.5 bg-blue-500/10 border-blue-500/30 text-blue-400">
                <span className="w-2 h-2 rounded-full bg-blue-500 animate-pulse"></span>
                AI Assistant
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
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center shadow-md">
                  <Robot size={18} weight="fill" className="text-white" />
                </div>
              )}
              
              <div
                className={cn(
                  "max-w-[85%] rounded-2xl px-4 py-3 shadow-sm",
                  message.role === 'user'
                    ? 'bg-gradient-to-br from-blue-500 to-blue-600 text-white'
                    : 'bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 border border-gray-200 dark:border-gray-700'
                )}
              >
                <div className="text-sm leading-relaxed whitespace-pre-wrap break-words">
                  {message.content}
                </div>
                <div className={cn(
                  "text-xs mt-2",
                  message.role === 'user' 
                    ? 'text-blue-100' 
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
              <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center shadow-md">
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
              placeholder="Ask about the meeting or request specific insights..."
              disabled={isLoading}
              className="flex-1 min-h-[44px] max-h-[120px] resize-none rounded-xl border-gray-300 dark:border-gray-600 focus:border-blue-500 dark:focus:border-blue-500 focus:ring-blue-500 bg-white dark:bg-gray-900 text-gray-900 dark:text-white placeholder:text-gray-500 dark:placeholder:text-gray-400"
              rows={1}
              style={{ height: '44px' }}
            />
            <Button
              onClick={handleSend}
              disabled={!input.trim() || isLoading}
              className="h-11 w-11 rounded-xl bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white shadow-md disabled:opacity-50 disabled:cursor-not-allowed flex-shrink-0"
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
