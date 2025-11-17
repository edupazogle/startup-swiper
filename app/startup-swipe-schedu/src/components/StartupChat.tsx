import { useState, useEffect } from 'react'
import { useKV } from '@/lib/useKV'
import { ChatMessage as ChatMessageType } from '@/lib/types'
import { Startup } from '@/lib/types'
import { WandMagicSparkles, Briefcase, UsersGroup, CalendarMonth } from 'flowbite-react-icons/outline'
import { ConciergeChatHeader } from './ConciergeChatHeader'
import { ChatMessageList, Message } from './ChatMessageList'
import { ChatInputArea } from './ChatInputArea'
import { QuickActionsBar, QuickAction } from './QuickActionsBar'
import { formatMessageTime, deduplicateMessages } from '@/lib/chatUtils'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

interface StartupChatProps {
  startup?: Startup
}

export function StartupChat({ startup }: StartupChatProps) {
  const [messages, setMessages] = useKV<ChatMessageType[]>('ai-assistant-messages', [])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const displayName = startup ? (startup.name || startup["Company Name"] || 'Unknown Startup') : 'Slush 2025'
  const subtitle = startup ? `Ask about ${displayName}` : 'Your Slush 2025 companion'

  // Initialize with welcome message
  useEffect(() => {
    if (!messages || messages.length === 0) {
      const welcomeMessage = startup
        ? `I'm here to help you dive deep into ${displayName}. Whether you need competitive intelligence, market insights, team analysis, or strategic guidance, I can help you make the most of your Slush connections.`
        : `I'm your intelligent companion for Slush 2025. I can help you navigate the event, discover amazing startups, connect with people, and stay on top of what's happening.`;

      setMessages([{
        id: '1',
        role: 'assistant',
        content: welcomeMessage,
        timestamp: Date.now()
      }])
    }
  }, [])

  const handleSend = async (retryCount = 0, maxRetries = 2) => {
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

      // Add startup context if viewing a specific startup
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
Employees: ${startup.employees || 'N/A'}
Founded: ${startup.dateFounded ? new Date(startup.dateFounded).getFullYear() : 'N/A'}
        `.trim()

        question = `Based on this startup information:\n\n${startupContext}\n\nAnswer this question: ${userMessage.content}`
      }

      const controller = new AbortController()
      const timeout = setTimeout(() => controller.abort(), 30000) // 30s timeout

      const response = await fetch(`${API_URL}/concierge/ask`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question: question,
          user_context: startup ? { startup_name: displayName } : null
        }),
        signal: controller.signal
      })

      clearTimeout(timeout)

      if (!response.ok) {
        if (response.status >= 500 && retryCount < maxRetries) {
          // Retry on server errors
          setTimeout(() => handleSend(retryCount + 1, maxRetries), 1000 * (retryCount + 1))
          return
        }
        throw new Error(`API error: ${response.status}`)
      }

      const data = await response.json()

      const assistantMessage: ChatMessageType = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.answer || 'I apologize, but I could not generate a response.',
        timestamp: Date.now()
      }

      setMessages((prev) => [...(prev || []), assistantMessage])
    } catch (error) {
      console.error('Error getting AI response:', error)
      
      let errorContent = 'Sorry, I encountered an error. Please try again.'
      if (error instanceof Error) {
        if (error.name === 'AbortError') {
          errorContent = 'Request timed out. Please try again.'
        } else if (error.message.includes('Failed to fetch')) {
          errorContent = 'Network error. Please check your connection and try again.'
        }
      }
      
      const errorMessage: ChatMessageType = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: errorContent,
        timestamp: Date.now()
      }
      setMessages((prev) => [...(prev || []), errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const handleQuickAction = async (actionLabel: string, retryCount = 0, maxRetries = 2) => {
    // Reset chat
    setMessages([])
    setInput('')
    setIsLoading(true)

    const actionQueries: { [key: string]: string } = {
      'LinkedIn': 'I want to write a LinkedIn post about my Slush experience',
      'Startups': 'Help me discover startups at Slush',
      'People': 'Help me find the right people to connect with',
      'Calendar': 'Help me navigate the Slush calendar and find key events'
    }

    const query = actionQueries[actionLabel] || actionLabel

    try {
      const controller = new AbortController()
      const timeout = setTimeout(() => controller.abort(), 30000)

      const response = await fetch(`${API_URL}/concierge/ask`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question: query,
          user_context: startup ? { startup_name: displayName } : null
        }),
        signal: controller.signal
      })

      clearTimeout(timeout)

      if (!response.ok) {
        if (response.status >= 500 && retryCount < maxRetries) {
          setTimeout(() => handleQuickAction(actionLabel, retryCount + 1, maxRetries), 1000 * (retryCount + 1))
          return
        }
        throw new Error(`API error: ${response.status}`)
      }

      const data = await response.json()

      const assistantMessage: ChatMessageType = {
        id: '1',
        role: 'assistant',
        content: data.answer || 'I apologize, but I could not generate a response.',
        timestamp: Date.now()
      }

      setMessages([assistantMessage])
    } catch (error) {
      console.error('Error getting AI response:', error)
      
      let errorContent = 'Sorry, I encountered an error. Please try again.'
      if (error instanceof Error) {
        if (error.name === 'AbortError') {
          errorContent = 'Request timed out. Please try again.'
        } else if (error.message.includes('Failed to fetch')) {
          errorContent = 'Network error. Please check your connection and try again.'
        }
      }
      
      const errorMessage: ChatMessageType = {
        id: '1',
        role: 'assistant',
        content: errorContent,
        timestamp: Date.now()
      }
      setMessages([errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const safeMessages = messages || []

  // Convert messages to display format and deduplicate
  const displayMessages: Message[] = deduplicateMessages(safeMessages).map(msg => ({
    id: msg.id,
    role: msg.role,
    content: msg.content,
    timestamp: formatMessageTime(msg.timestamp)
  }))

  // Quick actions with icons
  const quickActions: QuickAction[] = [
    {
      id: 'linkedin',
      label: 'LinkedIn',
      icon: <Briefcase className="w-4 h-4"  />,
      onClick: () => handleQuickAction('LinkedIn'),
      description: 'Write posts'
    },
    {
      id: 'startups',
      label: 'Startups',
      icon: <WandMagicSparkles className="w-4 h-4"  />,
      onClick: () => handleQuickAction('Startups'),
      description: 'Discover'
    },
    {
      id: 'people',
      label: 'People',
      icon: <UsersGroup className="w-4 h-4"   />,
      onClick: () => handleQuickAction('People'),
      description: 'Network'
    },
    {
      id: 'calendar',
      label: 'Calendar',
      icon: <CalendarMonth className="w-4 h-4"  />,
      onClick: () => handleQuickAction('Calendar'),
      description: 'Events'
    }
  ]

  return (
    <div className="h-full w-full flex flex-col bg-white/5 backdrop-blur-sm rounded-none md:rounded-lg border-0 md:border border-white/10 overflow-hidden">
      <ConciergeChatHeader
        title="AI Concierge"
        subtitle={subtitle}
        icon={<WandMagicSparkles className="text-purple-500 w-5 h-5"  />}
      />

      <ChatMessageList
        messages={displayMessages}
        isLoading={isLoading}
        showThinkingBubble={true}
        emptyStateMessage={
          <div className="space-y-2">
            <p className="font-medium text-sm sm:text-base">Start your conversation</p>
            <p className="text-xs sm:text-sm text-muted-foreground">Ask me anything about Slush or{startup ? ` about ${displayName}` : ''}</p>
          </div>
        }
      />

      <div className="flex-shrink-0 px-3 sm:px-4 md:px-6 py-1.5 sm:py-2 border-t border-border bg-background/95 backdrop-blur-sm">
        <QuickActionsBar
          actions={quickActions}
          isVisible={true}
          columns={2}
        />
      </div>

      <div className="flex-shrink-0">
        <ChatInputArea
          value={input}
          onChange={setInput}
          onSubmit={handleSend}
          isLoading={isLoading}
          placeholder="Ask a question..."
        />
      </div>
    </div>
  )
}
