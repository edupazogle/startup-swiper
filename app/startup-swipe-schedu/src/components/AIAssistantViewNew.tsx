import { useState, useEffect, useRef } from 'react'
import { useKV } from '@/lib/useKV'
import { ChatMessage as ChatMessageType } from '@/lib/types'
import { Startup } from '@/lib/types'
import { 
  Sparkle, 
  PaperPlaneTilt, 
  Robot, 
  User,
  Lightning,
  Briefcase,
  CalendarDots,
  Users as UsersIcon
} from '@phosphor-icons/react'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'
import { cn } from '@/lib/utils'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

interface AIAssistantViewNewProps {
  startup?: Startup
}

export function AIAssistantViewNew({ startup }: AIAssistantViewNewProps) {
  const [messages, setMessages] = useKV<ChatMessageType[]>('ai-assistant-messages', [])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  const displayName = startup ? (startup.name || startup["Company Name"] || 'Unknown Startup') : 'Slush 2025'
  const subtitle = startup ? `Ask about ${displayName}` : 'Your Slush 2025 AI Companion'

  // Initialize with welcome message
  useEffect(() => {
    if (!messages || messages.length === 0) {
      const welcomeMessage = startup
        ? `👋 Hi! I'm your AI assistant for **${displayName}**.\n\nI can help you with:\n• Competitive intelligence & market insights\n• Team & leadership analysis\n• Strategic recommendations\n• Investment potential evaluation\n\nWhat would you like to know?`
        : `👋 Welcome to Slush 2025!\n\nI'm your intelligent companion. I can help you:\n• Discover amazing startups\n• Navigate the event schedule\n• Connect with the right people\n• Stay on top of what's happening\n\nHow can I assist you today?`;

      setMessages([{
        id: '1',
        role: 'assistant',
        content: welcomeMessage,
        timestamp: Date.now()
      }])
    }
  }, [])

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 120)}px`
    }
  }, [input])

  const handleSend = async () => {
    if (!input.trim() || isLoading) return

    const userMessage: ChatMessageType = {
      id: Date.now().toString(),
      role: 'user',
      content: input.trim(),
      timestamp: Date.now()
    }

    setMessages((prev) => [...(prev || []), userMessage])
    setInput('')
    setIsLoading(true)

    try {
      let question = userMessage.content

      if (startup) {
        const startupContext = `
Company: ${displayName}
Description: ${startup.description || startup["Company Description"] || 'N/A'}
Value Proposition: ${startup.shortDescription || startup["USP"] || 'N/A'}
Topics: ${startup.topics?.join(', ') || 'N/A'}
Tech: ${startup.tech?.join(', ') || 'N/A'}
Location: ${startup.billingCity && startup.billingCountry ? `${startup.billingCity}, ${startup.billingCountry}` : (startup.billingCountry || 'N/A')}
Funding: ${startup.totalFunding ? `$${startup.totalFunding}M` : 'N/A'}
Stage: ${startup.maturity || 'N/A'}
        `.trim()

        question = `Based on this startup information:\n\n${startupContext}\n\nAnswer this question: ${userMessage.content}`
      }

      const response = await fetch(`${API_URL}/concierge/ask`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question: question,
          user_context: startup ? { startup_name: displayName } : null
        })
      })

      if (!response.ok) throw new Error(`API error: ${response.status}`)

      const data = await response.json()

      const assistantMessage: ChatMessageType = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.answer || 'I apologize, but I could not generate a response.',
        timestamp: Date.now()
      }

      setMessages((prev) => [...(prev || []), assistantMessage])
    } catch (error) {
      console.error('Error:', error)
      const errorMessage: ChatMessageType = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: Date.now()
      }
      setMessages((prev) => [...(prev || []), errorMessage])
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

  const quickActions = [
    { icon: Lightning, label: 'Quick Insights', color: 'yellow' },
    { icon: Briefcase, label: 'Investment Analysis', color: 'blue' },
    { icon: UsersIcon, label: 'Team Overview', color: 'purple' },
    { icon: CalendarDots, label: 'Meeting Prep', color: 'green' }
  ]

  return (
    <div className="h-full w-full flex flex-col bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <div className="border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 px-4 py-4 md:px-6">
        <div className="flex items-center gap-3">
          <div className="flex items-center justify-center w-10 h-10 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 shadow-md">
            <Sparkle size={20} weight="fill" className="text-white" />
          </div>
          <div className="flex-1 min-w-0">
            <h1 className="text-lg md:text-xl font-bold text-gray-900 dark:text-white truncate">
              AI Concierge
            </h1>
            <p className="text-sm text-gray-500 dark:text-gray-400 truncate">
              {subtitle}
            </p>
          </div>
          <Badge variant="outline" className="hidden sm:flex items-center gap-1.5 bg-green-50 dark:bg-green-950/30 border-green-200 dark:border-green-800 text-green-700 dark:text-green-400">
            <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
            Online
          </Badge>
        </div>
      </div>

      {/* Quick Actions */}
      {messages.length <= 1 && (
        <div className="px-4 py-3 md:px-6 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
          <div className="flex flex-wrap gap-2">
            {quickActions.map((action) => (
              <Button
                key={action.label}
                variant="outline"
                size="sm"
                onClick={() => setInput(action.label)}
                className="gap-2 text-xs"
              >
                <action.icon size={14} weight="duotone" />
                {action.label}
              </Button>
            ))}
          </div>
        </div>
      )}

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-4 md:px-6 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={cn(
              "flex gap-3 md:gap-4",
              message.role === 'user' ? 'justify-end' : 'justify-start'
            )}
          >
            {message.role === 'assistant' && (
              <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center shadow-md">
                <Robot size={18} weight="fill" className="text-white" />
              </div>
            )}
            
            <div
              className={cn(
                "max-w-[85%] md:max-w-[75%] rounded-2xl px-4 py-3 shadow-sm",
                message.role === 'user'
                  ? 'bg-gradient-to-br from-blue-500 to-blue-600 text-white'
                  : 'bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 border border-gray-200 dark:border-gray-700'
              )}
            >
              <div className="text-sm md:text-base leading-relaxed whitespace-pre-wrap break-words">
                {message.content}
              </div>
              {message.timestamp && (
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
              )}
            </div>

            {message.role === 'user' && (
              <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gray-200 dark:bg-gray-700 flex items-center justify-center">
                <User size={18} weight="fill" className="text-gray-600 dark:text-gray-300" />
              </div>
            )}
          </div>
        ))}

        {isLoading && (
          <div className="flex gap-3 md:gap-4 justify-start">
            <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center shadow-md">
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
      <div className="border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 px-4 py-4 md:px-6">
        <div className="flex gap-2 md:gap-3 items-end">
          <Textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type your message..."
            disabled={isLoading}
            className="flex-1 min-h-[44px] max-h-[120px] resize-none rounded-xl border-gray-300 dark:border-gray-600 focus:border-blue-500 dark:focus:border-blue-500 focus:ring-blue-500 dark:bg-gray-900"
            rows={1}
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
    </div>
  )
}
