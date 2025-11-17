import { useState, useRef, useEffect } from 'react'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Badge } from '@/components/ui/badge'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { ChatMessage } from '@/lib/types'
import { PaperPlane, WandMagicSparkles, User, WandMagicSparkles } from 'flowbite-react-icons/outline'
import { motion, AnimatePresence } from 'framer-motion'
import { useKV } from '@/lib/useKV'

interface AIAssistantProps {
  startups: any[]
  votes: any[]
  events: any[]
  currentUserName: string
}

export function AIAssistant({ startups, votes, events, currentUserName }: AIAssistantProps) {
  const [messages, setMessages] = useKV<ChatMessage[]>('ai-chat-messages', [])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const scrollRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [messages])

  const handleSend = async () => {
    if (!input.trim() || isLoading) return

    const userMessage: ChatMessage = {
      id: `msg-${Date.now()}`,
      role: 'user',
      content: input.trim(),
      timestamp: Date.now()
    }

    setMessages((current) => [...(current || []), userMessage])
    setInput('')
    setIsLoading(true)

    try {
      const interestedStartups = startups.filter(s => 
        votes.some(v => v.startupId === s.id && v.interested)
      )

      const upcomingEvents = events.filter(e => 
        new Date(e.startTime) > new Date()
      ).slice(0, 5)

      const userQuestion = input.trim()
      const totalStartups = startups.length
      const interestedCount = interestedStartups.length
      const upcomingCount = upcomingEvents.length
      const categories = [...new Set(interestedStartups.map(s => s.Category))].join(', ')

      const contextString = `You are an AI assistant for Startup Rise, a startup discovery platform at Slush 2025. 
Current user: ${currentUserName}

Context:
- Total startups: ${totalStartups}
- Interested startups: ${interestedCount}
- Upcoming events: ${upcomingCount}
- Interested startup categories: ${categories}

User question: ${userQuestion}

Provide helpful, concise responses about startups, events, or general advice. Be enthusiastic and supportive.`

      const response = await window.spark.llm(contextString)

      const assistantMessage: ChatMessage = {
        id: `msg-${Date.now()}`,
        role: 'assistant',
        content: response,
        timestamp: Date.now()
      }

      setMessages((current) => [...(current || []), assistantMessage])
    } catch (error) {
      const errorMessage: ChatMessage = {
        id: `msg-${Date.now()}`,
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: Date.now()
      }
      setMessages((current) => [...(current || []), errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const suggestedQuestions = [
    "What startups should I prioritize?",
    "Summarize my interests",
    "What meetings do I have?",
    "What's trending at Slush?"
  ]

  const handleSuggestion = (question: string) => {
    setInput(question)
  }

  return (
    <div className="h-full flex flex-col">
      <div className="bg-gradient-to-r from-primary/20 to-accent/20 p-4 md:p-6 border-b border-border/50">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-center gap-3">
            <Avatar className="w-12 h-12 bg-primary/10">
              <AvatarFallback>
                <WandMagicSparkles className="text-primary w-6 h-6"  />
              </AvatarFallback>
            </Avatar>
            <div>
              <h2 className="text-xl md:text-2xl font-semibold">AI Assistant</h2>
              <p className="text-sm text-muted-foreground">Ask me anything about startups and events</p>
            </div>
          </div>
        </div>
      </div>

      <div className="flex-1 max-w-4xl w-full mx-auto flex flex-col">
        <ScrollArea className="flex-1 p-4 md:p-6" ref={scrollRef}>
          {(!messages || messages.length === 0) && (
            <div className="flex flex-col items-center justify-center h-full text-center py-12">
              <WandMagicSparkles className="text-primary/50 mb-4 w-12 h-12"  />
              <h3 className="text-lg font-semibold mb-2">Hi {currentUserName}! 👋</h3>
              <p className="text-sm text-muted-foreground mb-6 max-w-md">
                I'm your AI assistant. Ask me anything about startups, get recommendations, or help with scheduling.
              </p>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-2 max-w-2xl w-full">
                {suggestedQuestions.map((question, idx) => (
                  <Button
                    key={idx}
                    variant="outline"
                    size="sm"
                    className="justify-start text-left w-full"
                    onClick={() => handleSuggestion(question)}
                  >
                    <WandMagicSparkles className="mr-2 flex-shrink-0 text-primary w-4 h-4"  />
                    <span className="text-sm">{question}</span>
                  </Button>
                ))}
              </div>
            </div>
          )}

          <AnimatePresence>
            {(messages || []).map((message) => (
              <motion.div
                key={message.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                className={`flex gap-3 mb-4 ${
                  message.role === 'user' ? 'justify-end' : 'justify-start'
                }`}
              >
                {message.role === 'assistant' && (
                  <Avatar className="w-8 h-8 bg-primary/10">
                    <AvatarFallback>
                      <WandMagicSparkles className="text-primary w-5 h-5"  />
                    </AvatarFallback>
                  </Avatar>
                )}
                <Card
                  className={`p-3 md:p-4 max-w-[80%] ${
                    message.role === 'user'
                      ? 'bg-primary text-primary-foreground'
                      : 'bg-card'
                  }`}
                >
                  <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                  <span className="text-xs opacity-70 mt-2 block">
                    {new Date(message.timestamp).toLocaleTimeString()}
                  </span>
                </Card>
                {message.role === 'user' && (
                  <Avatar className="w-8 h-8 bg-accent/10">
                    <AvatarFallback>
                      <User className="text-accent w-5 h-5"  />
                    </AvatarFallback>
                  </Avatar>
                )}
              </motion.div>
            ))}
          </AnimatePresence>

          {isLoading && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex gap-3 mb-4"
            >
              <Avatar className="w-8 h-8 bg-primary/10">
                <AvatarFallback>
                  <WandMagicSparkles className="text-primary w-5 h-5"  />
                </AvatarFallback>
              </Avatar>
              <Card className="p-3 md:p-4 bg-card">
                <div className="flex gap-1">
                  <span className="w-2 h-2 bg-primary/50 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                  <span className="w-2 h-2 bg-primary/50 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                  <span className="w-2 h-2 bg-primary/50 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                </div>
              </Card>
            </motion.div>
          )}
        </ScrollArea>

        <div className="p-4 border-t border-border/50 bg-card/50">
          <div className="flex gap-2">
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSend()}
              placeholder="Ask me anything..."
              disabled={isLoading}
              className="flex-1"
            />
            <Button
              onClick={handleSend}
              disabled={!input.trim() || isLoading}
              size="icon"
            >
              <PaperPlane className="w-5 h-5"  />
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}
