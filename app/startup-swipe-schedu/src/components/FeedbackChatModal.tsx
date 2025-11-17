import { useState, useEffect, useRef } from 'react'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Card } from '@/components/ui/card'
import { WandMagicSparkles, PaperPlane, Star } from 'flowbite-react-icons/outline'
import { motion, AnimatePresence } from 'framer-motion'
import { toast } from 'sonner'

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

  useEffect(() => {
    if (isOpen && modalState === 'initial' && startupName && userId) {
      startDebriefSession()
    }
  }, [isOpen, startupName, userId])

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
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="!flex !flex-col !h-screen md:!h-[90vh] !w-full md:!max-w-2xl !rounded-none md:!rounded-lg !border-0 md:!border !p-0 md:!p-4 !m-0 overflow-hidden !fixed !inset-0 md:!inset-auto md:!top-1/2 md:!left-1/2 md:!-translate-x-1/2 md:!-translate-y-1/2">
        {/* Header */}
        <div className="flex-shrink-0 border-b px-4 md:px-6 py-3 md:py-4">
          <div className="flex items-center gap-2 min-w-0">
            <WandMagicSparkles className="text-purple-500 flex-shrink-0 w-5 h-5"  />
            <div className="min-w-0">
              <h2 className="font-semibold text-sm md:text-base truncate">Insights: {startupName}</h2>
              <p className="text-xs text-muted-foreground mt-0.5">
                {modalState === 'conversation' && 'Share your meeting experience'}
                {modalState === 'questions' && 'Answer key follow-up questions'}
                {modalState === 'feedback' && 'Rate insights & add notes'}
                {modalState === 'completed' && 'All set!'}
              </p>
            </div>
          </div>
        </div>

        {/* Chat Conversation State */}
        {modalState === 'conversation' && (
          <div className="flex-1 overflow-hidden flex flex-col">
            {/* Messages */}
            <div className="flex-1 overflow-y-auto px-4 md:px-6 py-3 md:py-4 space-y-3 md:space-y-4">
              <AnimatePresence>
                {messages.map((msg, idx) => (
                  <motion.div
                    key={idx}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <Card className={`max-w-[85%] md:max-w-[70%] p-3 md:p-4 text-xs md:text-sm ${
                      msg.role === 'user'
                        ? 'bg-purple-500 text-white'
                        : 'bg-background border'
                    }`}>
                      <p className="leading-relaxed">{msg.content}</p>
                      <p className={`text-xs mt-1.5 ${
                        msg.role === 'user' ? 'text-purple-100' : 'text-muted-foreground'
                      }`}>
                        {new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </p>
                    </Card>
                  </motion.div>
                ))}
              </AnimatePresence>
              <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="flex-shrink-0 border-t px-4 md:px-6 py-3 bg-muted/50 space-y-2">
              <div className="flex gap-2">
                <Textarea
                  ref={textareaRef}
                  value={currentMessage}
                  onChange={(e) => setCurrentMessage(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="What happened in the meeting?"
                  className="min-h-[60px] md:min-h-[70px] resize-none text-xs md:text-sm"
                  disabled={isLoading}
                />
                <Button
                  onClick={sendMessage}
                  disabled={!currentMessage.trim() || isLoading}
                  size="sm"
                  className="flex-shrink-0 self-end"
                >
                  <PaperPlane className="w-4 h-4"  />
                </Button>
              </div>
              
              {messages.length > 2 && (
                <Button
                  onClick={moveToQuestions}
                  disabled={isLoading}
                  variant="outline"
                  size="sm"
                  className="w-full"
                >
                  Continue to Questions
                </Button>
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
      </DialogContent>
    </Dialog>
  )
}
