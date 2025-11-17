import { useState, useEffect, useRef } from 'react'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Card } from '@/components/ui/card'
import { Sparkle, PaperPlaneRight, Star, X, ArrowRight, CheckCircle } from '@phosphor-icons/react'
import { motion, AnimatePresence } from 'framer-motion'
import { toast } from 'sonner'
import { cn } from '@/lib/utils'

interface Message {
  role: 'user' | 'assistant'
  content: string
  timestamp: string
}

interface ImprovedInsightsModalProps {
  isOpen: boolean
  onClose: () => void
  userId: string
  startupId?: string
  startupName: string
  startupDescription: string
}

type ModalState = 'initial' | 'conversation' | 'questions' | 'feedback' | 'completed'

export function ImprovedInsightsModal({
  isOpen,
  onClose,
  userId,
  startupId,
  startupName,
  startupDescription
}: ImprovedInsightsModalProps) {
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

  // Reset state when modal closes
  useEffect(() => {
    if (!isOpen) {
      setModalState('initial')
      setSessionId(null)
      setMessages([])
      setCurrentMessage('')
      setError(null)
      setQuestions([])
      setQuestionAnswers(['', '', ''])
      setRatings({ 0: 0, 1: 0, 2: 0 })
      setFinalNotes('')
    }
  }, [isOpen])

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
      setError('Failed to start insights session. Please try again.')
      toast.error('Failed to start insights session')
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

  const submitFeedback = async () => {
    if (!sessionId) return

    setIsLoading(true)
    setError(null)

    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/insights/debrief/submit-feedback`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId,
          startup_name: startupName,
          questions: questions.map((q, i) => ({
            question: q,
            answer: questionAnswers[i] || '',
            rating: ratings[i] || 0
          })),
          final_notes: finalNotes
        })
      })

      if (!response.ok) {
        throw new Error(`Failed to submit feedback: ${response.status}`)
      }

      const data = await response.json()
      if (!data.success) {
        throw new Error(data.error || 'Failed to submit feedback')
      }

      setModalState('completed')
      toast.success('Insights saved successfully!')
      
    } catch (err) {
      console.error('Error submitting feedback:', err)
      setError('Failed to save insights. Please try again.')
      toast.error('Failed to save insights')
    } finally {
      setIsLoading(false)
    }
  }

  const renderLoadingState = () => (
    <div className="flex flex-col items-center justify-center py-12 px-4">
      <motion.div
        animate={{ rotate: 360 }}
        transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
        className="mb-6"
      >
        <Sparkle size={48} weight="fill" className="text-yellow-500" />
      </motion.div>
      <p className="text-lg font-semibold text-gray-700 dark:text-gray-300 mb-2">
        Generating AI Insights...
      </p>
      <p className="text-sm text-gray-500 dark:text-gray-400 text-center max-w-md">
        Our AI is analyzing {startupName} and preparing personalized insights for you
      </p>
    </div>
  )

  const renderConversation = () => (
    <div className="flex flex-col h-[600px]">
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50 dark:bg-gray-900">
        <AnimatePresence>
          {messages.map((msg, idx) => (
            <motion.div
              key={idx}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              className={cn(
                "flex",
                msg.role === 'user' ? "justify-end" : "justify-start"
              )}
            >
              <div className={cn(
                "max-w-[80%] rounded-xl px-4 py-3 shadow-md",
                msg.role === 'user' 
                  ? "bg-gradient-to-br from-blue-500 to-indigo-600 text-white" 
                  : "bg-white dark:bg-gray-800 text-gray-900 dark:text-white border-2 border-gray-200 dark:border-gray-700"
              )}>
                <p className="text-sm font-medium whitespace-pre-wrap">{msg.content}</p>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
        
        {isLoading && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex justify-start"
          >
            <div className="bg-white dark:bg-gray-800 rounded-xl px-4 py-3 border-2 border-gray-200 dark:border-gray-700">
              <div className="flex gap-2">
                <motion.div
                  animate={{ scale: [1, 1.2, 1] }}
                  transition={{ duration: 0.6, repeat: Infinity, delay: 0 }}
                  className="w-2 h-2 rounded-full bg-yellow-500"
                />
                <motion.div
                  animate={{ scale: [1, 1.2, 1] }}
                  transition={{ duration: 0.6, repeat: Infinity, delay: 0.2 }}
                  className="w-2 h-2 rounded-full bg-yellow-500"
                />
                <motion.div
                  animate={{ scale: [1, 1.2, 1] }}
                  transition={{ duration: 0.6, repeat: Infinity, delay: 0.4 }}
                  className="w-2 h-2 rounded-full bg-yellow-500"
                />
              </div>
            </div>
          </motion.div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="p-4 border-t-2 border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800">
        <div className="flex gap-2">
          <Textarea
            ref={textareaRef}
            value={currentMessage}
            onChange={(e) => setCurrentMessage(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault()
                sendMessage()
              }
            }}
            placeholder="Ask about the startup..."
            className="flex-1 min-h-[44px] max-h-32 resize-none"
            disabled={isLoading}
          />
          <Button
            onClick={sendMessage}
            disabled={!currentMessage.trim() || isLoading}
            className="bg-gradient-to-r from-yellow-400 to-amber-500 hover:from-yellow-500 hover:to-amber-600 text-white px-4"
          >
            <PaperPlaneRight size={20} weight="fill" />
          </Button>
        </div>
        <div className="mt-3 flex justify-end">
          <Button
            onClick={moveToQuestions}
            disabled={isLoading || messages.length < 2}
            className="bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 text-white gap-2"
          >
            Continue to Questions
            <ArrowRight size={16} weight="bold" />
          </Button>
        </div>
      </div>
    </div>
  )

  const renderQuestions = () => (
    <div className="p-6 space-y-6 max-h-[600px] overflow-y-auto">
      <p className="text-sm text-gray-600 dark:text-gray-400 mb-6">Please answer these questions to complete your insights</p>

      {questions.map((question, idx) => (
        <Card key={idx} className="p-5 border-2 border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 shadow-md">
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-bold text-gray-900 dark:text-white mb-3">
                Question {idx + 1}
              </label>
              <p className="text-sm text-gray-700 dark:text-gray-300 mb-4 leading-relaxed">
                {question}
              </p>
            </div>

            <Textarea
              value={questionAnswers[idx]}
              onChange={(e) => {
                const newAnswers = [...questionAnswers]
                newAnswers[idx] = e.target.value
                setQuestionAnswers(newAnswers)
              }}
              placeholder="Your answer..."
              className="min-h-[100px]"
            />

            <div>
              <p className="text-xs font-semibold text-gray-600 dark:text-gray-400 mb-2">
                Rate this question's importance
              </p>
              <div className="flex gap-2">
                {[1, 2, 3, 4, 5].map((star) => (
                  <button
                    key={star}
                    onClick={() => setRatings({ ...ratings, [idx]: star })}
                    className="transition-transform hover:scale-110"
                  >
                    <Star
                      size={24}
                      weight={star <= (ratings[idx] || 0) ? "fill" : "regular"}
                      className={star <= (ratings[idx] || 0) ? "text-yellow-500" : "text-gray-300 dark:text-gray-600"}
                    />
                  </button>
                ))}
              </div>
            </div>
          </div>
        </Card>
      ))}

      <div>
        <label className="block text-sm font-bold text-gray-900 dark:text-white mb-3">
          Additional Notes (Optional)
        </label>
        <Textarea
          value={finalNotes}
          onChange={(e) => setFinalNotes(e.target.value)}
          placeholder="Any additional insights or notes..."
          className="min-h-[120px]"
        />
      </div>

      <div className="flex gap-3 pt-4">
        <Button
          onClick={() => setModalState('conversation')}
          variant="outline"
          className="flex-1"
        >
          Back to Chat
        </Button>
        <Button
          onClick={submitFeedback}
          disabled={isLoading}
          className="flex-1 bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 text-white"
        >
          {isLoading ? 'Saving...' : 'Complete Insights'}
        </Button>
      </div>
    </div>
  )

  const renderCompleted = () => (
    <div className="flex flex-col items-center justify-center py-12 px-4">
      <motion.div
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        transition={{ type: "spring", duration: 0.5 }}
      >
        <CheckCircle size={80} weight="fill" className="text-green-500 mb-6" />
      </motion.div>
      <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-3">
        Insights Saved!
      </h3>
      <p className="text-gray-600 dark:text-gray-400 text-center max-w-md mb-8">
        Your insights for {startupName} have been successfully saved.
      </p>
      <Button
        onClick={onClose}
        className="bg-gradient-to-r from-blue-500 to-indigo-600 hover:from-blue-600 hover:to-indigo-700 text-white px-8"
      >
        Close
      </Button>
    </div>
  )

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl p-0 gap-0 bg-white dark:bg-gray-800 border-2 border-gray-300 dark:border-gray-600">
        <DialogHeader className="p-6 pb-0">
          <DialogTitle className="text-2xl font-bold flex items-center gap-3">
            <Sparkle size={28} weight="fill" className="text-yellow-500" />
            <span className="bg-gradient-to-r from-yellow-600 to-amber-600 bg-clip-text text-transparent">
              Insights AI
            </span>
          </DialogTitle>
        </DialogHeader>

        {error && (
          <div className="mx-6 mt-4 p-4 bg-red-50 dark:bg-red-900/20 border-2 border-red-200 dark:border-red-800 rounded-lg">
            <p className="text-sm font-semibold text-red-700 dark:text-red-400">{error}</p>
          </div>
        )}

        <div className="relative">
          {modalState === 'initial' && isLoading && renderLoadingState()}
          {modalState === 'conversation' && renderConversation()}
          {modalState === 'questions' && renderQuestions()}
          {modalState === 'completed' && renderCompleted()}
        </div>
      </DialogContent>
    </Dialog>
  )
}
