import { useState, useEffect, useRef } from 'react'
import { TailwindModal } from '@/components/ui/tailwind-modal'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { WandMagicSparkles, PaperPlane, Star, User, Close } from 'flowbite-react-icons/outline'
import { motion, AnimatePresence } from 'framer-motion'
import { toast } from 'sonner'
import { cn } from '@/lib/utils'

interface Message {
  role: 'user' | 'assistant'
  content: string
  timestamp: string
}

interface FeedbackChatModalProps {
  isOpen: boolean
  onClose: () => void
  userId: string
  startupId?: string
  startupName: string
  startupDescription: string
}

type ModalState = 'initial' | 'conversation' | 'questions' | 'feedback' | 'completed'

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

export function FeedbackChatModal({
  isOpen,
  onClose,
  userId,
  startupId,
  startupName,
  startupDescription
}: FeedbackChatModalProps) {
  const [modalState, setModalState] = useState<ModalState>('initial')
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [messages, setMessages] = useState<Message[]>([])
  const [currentMessage, setCurrentMessage] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [hasStarted, setHasStarted] = useState(false)
  
  // For questions state
  const [questions, setQuestions] = useState<string[]>([])
  const [questionAnswers, setQuestionAnswers] = useState<string[]>(['', '', ''])
  
  // For feedback state
  const [ratings, setRatings] = useState<Record<number, number>>({ 0: 0, 1: 0, 2: 0 })
  const [finalNotes, setFinalNotes] = useState('')

  const messagesEndRef = useRef<HTMLDivElement>(null)
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' })
    }
  }, [messages])

  // Reset on close
  useEffect(() => {
    if (!isOpen) {
      setModalState('initial')
      setMessages([])
      setCurrentMessage('')
      setSessionId(null)
      setIsLoading(false)
      setHasStarted(false)
      setQuestions([])
      setQuestionAnswers(['', '', ''])
      setRatings({ 0: 0, 1: 0, 2: 0 })
      setFinalNotes('')
      setError(null)
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
    setIsLoading(true)
    setError(null)
    
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/insights/debrief/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: userId,
          startup_id: String(startupId || 'unknown'),
          startup_name: startupName,
          meeting_prep_outline: "Meeting insights debrief"
        })
      })

      if (!response.ok) {
        throw new Error(`Failed to start debrief: ${response.status}`)
      }

      const data = await response.json()
      if (!data.success) {
        throw new Error(data.error || 'Failed to initialize')
      }

      setSessionId(data.session_id)
      setMessages([{
        role: 'assistant',
        content: data.message,
        timestamp: new Date().toISOString()
      }])
      setModalState('conversation')
      
    } catch (err) {
      console.error('Error starting debrief:', err)
      setError('Failed to start debrief. Please try again.')
      toast.error('Failed to start debrief')
    } finally {
      setIsLoading(false)
    }
  }

  const sendMessage = async () => {
    if (!currentMessage.trim() || !sessionId || isLoading) return

    const userMessage: Message = {
      role: 'user',
      content: currentMessage,
      timestamp: new Date().toISOString()
    }

    setMessages(prev => [...prev, userMessage])
    const messageContent = currentMessage
    setCurrentMessage('')
    setIsLoading(true)

    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/insights/debrief/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId,
          user_message: messageContent,
          startup_name: startupName,
          meeting_prep_outline: "Meeting prep context",
          conversation_history: [...messages, userMessage]
        })
      })

      if (!response.ok) {
        throw new Error(`Failed to send message: ${response.status}`)
      }

      const data = await response.json()
      if (!data.success) {
        throw new Error(data.error || 'Failed to process message')
      }

      setMessages(prev => [...prev, {
        role: 'assistant',
        content: data.message,
        timestamp: new Date().toISOString()
      }])

    } catch (err) {
      console.error('Error sending message:', err)
      toast.error('Failed to send message')
      setMessages(prev => prev.filter(m => m !== userMessage))
      setCurrentMessage(messageContent)
    } finally {
      setIsLoading(false)
    }
  }

  const moveToQuestions = async () => {
    if (!sessionId) return
    
    setIsLoading(true)
    setError(null)

    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/insights/debrief/generate-questions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId,
          startup_name: startupName,
          meeting_prep_outline: "Meeting prep context",
          conversation_history: messages
        })
      })

      if (!response.ok) {
        throw new Error(`Failed to generate questions: ${response.status}`)
      }

      const data = await response.json()
      if (!data.success) {
        throw new Error(data.error || 'Failed to generate questions')
      }

      setQuestions(data.questions || [])
      setModalState('questions')
      
    } catch (err) {
      console.error('Error generating questions:', err)
      setError('Failed to generate questions. Please try again.')
      toast.error('Failed to generate questions')
    } finally {
      setIsLoading(false)
    }
  }

  const moveToFeedback = () => {
    setModalState('feedback')
  }

  const submitFeedback = async () => {
    if (!sessionId) return

    setIsLoading(true)
    setError(null)

    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/insights/debrief/complete`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId,
          startup_id: String(startupId || 'unknown'),
          startup_name: startupName,
          user_id: userId,
          meeting_prep_outline: "Meeting prep context",
          conversation_history: messages,
          ratings: ratings,
          final_notes: finalNotes
        })
      })

      if (!response.ok) {
        throw new Error(`Failed to submit feedback: ${response.status}`)
      }

      const data = await response.json()
      if (!data.success) {
        throw new Error(data.error || 'Failed to submit')
      }

      toast.success('Debrief saved successfully!')
      setModalState('completed')
      // Store completion data for potential recovery
      sessionStorage.setItem(`debrief_${sessionId}`, JSON.stringify({
        startup_name: startupName,
        insights_extraction_success: data.insights_extraction_success || false,
        insights_saved: data.insights_saved || 0
      }))
      setTimeout(() => {
        onClose()
      }, 2000)
      
    } catch (err) {
      console.error('Error submitting feedback:', err)
      setError('Failed to submit. Please try again.')
      toast.error('Failed to submit feedback')
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const StarRating = ({ value, onChange, index }: { value: number; onChange: (v: number) => void; index: number }) => {
    return (
      <div className="flex gap-1">
        {[1, 2, 3, 4, 5].map((star) => (
          <button
            key={star}
            onClick={() => onChange(star)}
            className="transition-all"
          >
            <Star
              className={star <= value ? 'text-yellow-400' : 'text-gray-300'}
              />
          </button>
        ))}
      </div>
    )
  }

  return (
    <TailwindModal isOpen={isOpen} onClose={onClose} size="xl" className="p-0 flex flex-col max-md:h-full md:h-[90vh] md:max-h-[90vh]">
      {/* Header */}
      <div className="flex-shrink-0 border-b border-gray-700 dark:border-gray-700 bg-gray-800 dark:bg-gray-800 px-4 py-3 md:px-6 md:py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="flex items-center justify-center w-10 h-10 rounded-lg bg-gradient-to-br from-purple-500 to-pink-600 shadow-md">
              <Star className="text-white w-5 h-5"  />
            </div>
            <div className="flex-1 min-w-0">
              <h2 className="text-lg font-bold text-white">
                {modalState === 'conversation' && 'Insights Debrief'}
                {modalState === 'questions' && 'Key Questions'}
                {modalState === 'feedback' && 'Rate Your Insights'}
                {modalState === 'completed' && 'Complete!'}
              </h2>
              <p className="text-sm text-gray-300 truncate">
                {startupName}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            {modalState === 'conversation' && (
              <Badge variant="outline" className="hidden sm:flex items-center gap-1.5 bg-green-50 dark:bg-green-950/30 border-green-200 dark:border-green-800 text-green-700 dark:text-green-400">
                <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
                Recording
              </Badge>
            )}
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

        {/* Welcome Screen / Chat Conversation State */}
        {(modalState === 'initial' || modalState === 'conversation') && (
          <div className="flex-1 overflow-hidden flex flex-col">
            {/* Messages */}
            <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4 bg-gray-50 dark:bg-gray-900">
              {/* Welcome Screen - Before Starting Session */}
              {!hasStarted && messages.length === 0 && (
                <div className="h-full flex items-center justify-center">
                  <div className="max-w-md text-center space-y-6">
                    <div className="w-16 h-16 bg-gradient-to-br from-purple-500 to-pink-600 rounded-2xl flex items-center justify-center mx-auto shadow-lg">
                      <Star className="w-8 h-8 text-white" />
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
                        setModalState('conversation')
                        startDebriefSession()
                        // Add welcome message after starting
                        setMessages([{
                          role: 'assistant',
                          content: `👋 Welcome to your **${startupName}** debrief session!\n\nI'll help you capture and analyze insights from your meeting. Let's start with:\n\n• What were your key observations?\n• What stood out about their approach?\n• Any concerns or red flags?\n\nShare your thoughts, and I'll help you organize them into actionable insights.`,
                          timestamp: new Date().toISOString()
                        }])
                      }}
                      className="w-full bg-gradient-to-r from-purple-500 to-pink-600 hover:from-purple-600 hover:to-pink-700 text-white font-semibold py-3 rounded-lg shadow-md transition-all"
                      size="lg"
                    >
                      <Star className="w-5 h-5 mr-2" />
                      Start Debrief Session
                    </Button>
                  </div>
                </div>
              )}
              
              <AnimatePresence>
                {messages.map((msg, idx) => (
                  <motion.div
                    key={idx}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className={cn(
                      "flex gap-3",
                      msg.role === 'user' ? 'justify-end' : 'justify-start'
                    )}
                  >
                    {msg.role === 'assistant' && (
                      <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-purple-500 to-pink-600 flex items-center justify-center shadow-md">
                        <WandMagicSparkles className="text-white w-5 h-5"  />
                      </div>
                    )}
                    
                    <div
                      className={cn(
                        "max-w-[85%] rounded-2xl px-4 py-3 shadow-sm",
                        msg.role === 'user'
                          ? 'bg-gradient-to-br from-purple-500 to-pink-600 text-white'
                          : 'bg-white/90 backdrop-blur-sm text-gray-900 dark:text-white border border-gray-200/50 dark:border-gray-700/50'
                      )}
                    >
                      <div className="text-sm leading-relaxed whitespace-pre-wrap break-words">
                        {renderMessageContent(msg.content)}
                      </div>
                      <div className={cn(
                        "text-xs mt-2",
                        msg.role === 'user' 
                          ? 'text-purple-100' 
                          : 'text-gray-500 dark:text-gray-400'
                      )}>
                        {new Date(msg.timestamp).toLocaleTimeString([], { 
                          hour: '2-digit', 
                          minute: '2-digit' 
                        })}
                      </div>
                    </div>

                    {msg.role === 'user' && (
                      <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center shadow-md">
                        <User className="text-white w-5 h-5"  />
                      </div>
                    )}
                  </motion.div>
                ))}
              </AnimatePresence>
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
                  value={currentMessage}
                  onChange={(e) => setCurrentMessage(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="Share your insights..."
                  disabled={isLoading}
                  className="flex-1 min-h-[44px] max-h-[120px] resize-none rounded-xl border-2 border-gray-300 dark:border-gray-600 focus:border-purple-500 focus:ring-2 focus:ring-purple-500 bg-white dark:bg-gray-900 text-gray-900 dark:text-white placeholder:text-gray-500 dark:placeholder:text-gray-400"
                  rows={1}
                  style={{ height: '44px' }}
                />
                <Button
                  onClick={sendMessage}
                  disabled={!currentMessage.trim() || isLoading || !sessionId}
                  className="h-11 w-11 rounded-xl bg-gradient-to-r from-purple-500 to-pink-600 hover:from-purple-600 hover:to-pink-700 text-white shadow-md disabled:opacity-50 disabled:cursor-not-allowed flex-shrink-0"
                >
                  <PaperPlane size={20} weight="fill" />
                </Button>
              </div>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-2 text-center">
                Press Enter to send, Shift+Enter for new line
              </p>
              
              {messages.length >= 1 && (
                <div className="pt-2">
                  <Button
                    onClick={moveToQuestions}
                    disabled={isLoading}
                    className="w-full bg-gradient-to-r from-blue-500 to-indigo-600 hover:from-blue-600 hover:to-indigo-700 text-white font-semibold py-2.5 rounded-lg shadow-md transition-all"
                    size="sm"
                  >
                    Continue to Questions →
                  </Button>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Questions State */}
        {modalState === 'questions' && (
          <div className="flex-1 overflow-hidden flex flex-col">
            <div className="flex-1 overflow-y-auto px-4 md:px-6 py-3 md:py-4 space-y-3 md:space-y-4">
              {questions.map((question, idx) => (
                <motion.div
                  key={idx}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: idx * 0.1 }}
                >
                  <Card className="p-3 md:p-4 border">
                    <div className="text-xs md:text-sm font-medium text-foreground mb-2">
                      {idx + 1}. {question}
                    </div>
                    <Textarea
                      value={questionAnswers[idx]}
                      onChange={(e) => {
                        const newAnswers = [...questionAnswers]
                        newAnswers[idx] = e.target.value
                        setQuestionAnswers(newAnswers)
                      }}
                      placeholder="Your response..."
                      className="min-h-[70px] md:min-h-[80px] resize-none text-xs md:text-sm"
                    />
                  </Card>
                </motion.div>
              ))}
            </div>

            <div className="flex-shrink-0 border-t px-4 md:px-6 py-3 bg-muted/50 flex gap-2">
              <Button
                onClick={() => setModalState('conversation')}
                variant="outline"
                size="sm"
              >
                Back
              </Button>
              <Button
                onClick={moveToFeedback}
                size="sm"
                className="flex-1"
              >
                Continue
              </Button>
            </div>
          </div>
        )}

        {/* Feedback State */}
        {modalState === 'feedback' && (
          <div className="flex-1 overflow-hidden flex flex-col">
            <div className="flex-1 overflow-y-auto px-4 md:px-6 py-3 md:py-4 space-y-4 md:space-y-6">
              <div>
                <h3 className="text-xs md:text-sm font-semibold mb-3">Rate the insights</h3>
                <div className="space-y-3">
                  {questions.map((question, idx) => (
                    <div key={idx} className="space-y-1.5">
                      <p className="text-xs text-muted-foreground line-clamp-2">{question}</p>
                      <StarRating
                        value={ratings[idx] || 0}
                        onChange={(v) => setRatings({ ...ratings, [idx]: v })}
                        index={idx}
                      />
                    </div>
                  ))}
                </div>
              </div>

              <div>
                <label className="text-xs md:text-sm font-medium block mb-2">Additional notes</label>
                <Textarea
                  value={finalNotes}
                  onChange={(e) => setFinalNotes(e.target.value)}
                  placeholder="Any follow-ups or observations..."
                  className="min-h-[100px] md:min-h-[120px] resize-none text-xs md:text-sm"
                />
              </div>
            </div>

            <div className="flex-shrink-0 border-t px-4 md:px-6 py-3 bg-muted/50 flex gap-2">
              <Button
                onClick={() => setModalState('questions')}
                variant="outline"
                size="sm"
              >
                Back
              </Button>
              <Button
                onClick={submitFeedback}
                disabled={isLoading}
                size="sm"
                className="flex-1"
              >
                {isLoading ? 'Saving...' : 'Save & Close'}
              </Button>
            </div>
          </div>
        )}

        {/* Completed State */}
        {modalState === 'completed' && (
          <div className="flex-1 flex flex-col items-center justify-center px-4 md:px-6 py-6 md:py-8">
            <div className="text-center space-y-3 md:space-y-4 max-w-sm">
              <div className="text-5xl md:text-6xl">✨</div>
              <h3 className="text-lg md:text-xl font-semibold">Complete!</h3>
              <p className="text-xs md:text-sm text-muted-foreground">
                Your insights have been saved and will appear on your dashboard.
              </p>
              <div className="bg-blue-50 dark:bg-blue-950/30 border border-blue-200 dark:border-blue-800 rounded-lg p-2.5 md:p-3 mt-3">
                <p className="text-xs text-blue-700 dark:text-blue-300">
                  ✓ You can close this window now.
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="flex-1 flex flex-col items-center justify-center px-4 md:px-6 py-6">
            <div className="text-center space-y-3 max-w-sm">
              <p className="text-xs md:text-sm text-red-600 dark:text-red-400">{error}</p>
              <Button size="sm" onClick={startDebriefSession}>Try Again</Button>
            </div>
          </div>
        )}
    </TailwindModal>
  )
}
