import { useState, useRef, useEffect } from 'react'
import { useKV } from '@github/spark/hooks'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { ChatMessage } from '@/lib/types'
import { Startup } from '@/lib/types'
import { PaperPlaneRight, Robot, User } from '@phosphor-icons/react'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

interface StartupChatProps {
  startup?: Startup
}

export function StartupChat({ startup }: StartupChatProps) {
  const [messages, setMessages] = useKV<ChatMessage[]>('ai-assistant-messages', [])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const scrollRef = useRef<HTMLDivElement>(null)

  const displayName = startup ? (startup.name || startup["Company Name"] || 'Unknown Startup') : 'Slush 2025'

  useEffect(() => {
    if ((!messages || messages.length === 0)) {
      setMessages([{
        id: '1',
        role: 'assistant',
        content: `Hi! I'm your AI Concierge for Slush 2025, powered by NVIDIA NIM. ${startup ? `I can help you learn more about ${displayName}. Ask me anything about their business model, funding, team, technology, or market position.` : `Ask me about startups, meetings, schedules, or anything about the event! I have access to the startup database and can search by industry, location, funding, and more.`}`,
        timestamp: Date.now()
      }])
    }
  }, [])

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [messages])

  const handleSend = async () => {
    if (!input.trim() || isLoading) return

    const userMessage: ChatMessage = {
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
      
      // Add startup context to the question if viewing a specific startup
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

        question = `Based on this startup information:

${startupContext}

Answer this question: ${userMessage.content}`
      }

      // Call the backend concierge API with NVIDIA NIM
      const response = await fetch(`${API_URL}/concierge/ask`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question: question,
          user_context: startup ? { startup_name: displayName } : null
        })
      })

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`)
      }

      const data = await response.json()

      const assistantMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.answer || 'I apologize, but I could not generate a response.',
        timestamp: Date.now()
      }

      setMessages((prev) => [...(prev || []), assistantMessage])
    } catch (error) {
      console.error('Error getting AI response:', error)
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'Sorry, I encountered an error connecting to the AI assistant. Please try again.',
        timestamp: Date.now()
      }
      setMessages((prev) => [...(prev || []), errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const quickQuestions = startup ? [
    'What is their business model?',
    'Who are their competitors?',
    'What makes them unique?',
    'What is their market opportunity?'
  ] : [
    'What meetings do I have today?',
    'What startups should I prioritize?',
    'Tell me about the Slush schedule',
    'What are the key AI trends?'
  ]

  const handleQuickQuestion = (question: string) => {
    setInput(question)
  }

  const safeMessages = messages || []

  return (
    <div className="h-full flex flex-col p-4">
      <div className="flex items-center gap-2 mb-3">
        <div className="w-8 h-8 bg-accent/10 rounded-md flex items-center justify-center">
          <Robot size={18} weight="duotone" className="text-accent" />
        </div>
        <div>
          <h3 className="text-sm font-semibold text-foreground">AI Assistant</h3>
          <p className="text-xs text-muted-foreground">{startup ? `Ask about ${displayName}` : 'Your Slush 2025 companion'}</p>
        </div>
      </div>

      <Card className="flex-1 flex flex-col min-h-0 overflow-hidden">
        <div className="flex-1 overflow-y-auto p-3" ref={scrollRef}>
          <div className="space-y-3">
            {safeMessages.map((message) => (
              <div
                key={message.id}
                className={`flex gap-2 ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                {message.role === 'assistant' && (
                  <div className="w-6 h-6 bg-accent/10 rounded-md flex items-center justify-center flex-shrink-0 mt-0.5">
                    <Robot size={14} weight="duotone" className="text-accent" />
                  </div>
                )}
                
                <div
                  className={`max-w-[80%] rounded-md px-3 py-2 text-sm ${
                    message.role === 'user'
                      ? 'bg-white text-gray-900 shadow-sm border border-gray-200'
                      : 'bg-muted text-foreground'
                  }`}
                >
                  <p className="whitespace-pre-wrap leading-relaxed">{message.content}</p>
                </div>

                {message.role === 'user' && (
                  <div className="w-6 h-6 bg-primary/10 rounded-md flex items-center justify-center flex-shrink-0 mt-0.5">
                    <User size={14} weight="duotone" className="text-primary" />
                  </div>
                )}
              </div>
            ))}
            
            {isLoading && (
              <div className="flex gap-2 justify-start">
                <div className="w-6 h-6 bg-accent/10 rounded-md flex items-center justify-center flex-shrink-0 mt-0.5">
                  <Robot size={14} weight="duotone" className="text-accent" />
                </div>
                <div className="bg-muted rounded-md px-3 py-2">
                  <div className="flex gap-1">
                    <div className="w-2 h-2 bg-muted-foreground/40 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                    <div className="w-2 h-2 bg-muted-foreground/40 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                    <div className="w-2 h-2 bg-muted-foreground/40 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {safeMessages.length === 1 && (
          <div className="p-3 border-t border-border">
            <p className="text-xs text-muted-foreground mb-2">Quick questions:</p>
            <div className="flex flex-wrap gap-1.5">
              {quickQuestions.map((question, idx) => (
                <Badge
                  key={idx}
                  variant="outline"
                  className="cursor-pointer hover:bg-accent/10 transition-colors text-xs"
                  onClick={() => handleQuickQuestion(question)}
                >
                  {question}
                </Badge>
              ))}
            </div>
          </div>
        )}

        <div className="p-3 border-t border-border flex gap-2">
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask a question..."
            className="flex-1 text-sm"
            disabled={isLoading}
          />
          <Button
            onClick={handleSend}
            disabled={!input.trim() || isLoading}
            size="icon"
            className="flex-shrink-0"
          >
            <PaperPlaneRight size={16} weight="bold" />
          </Button>
        </div>
      </Card>
    </div>
  )
}
