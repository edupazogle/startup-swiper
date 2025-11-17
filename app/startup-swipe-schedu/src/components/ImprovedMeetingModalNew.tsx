import { useState, useEffect, useRef, useMemo, useCallback } from 'react'
import { TailwindModal, TailwindModalHeader, TailwindModalBody, TailwindModalTitle, TailwindModalDescription } from '@/components/ui/tailwind-modal'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'
import { Briefcase, PaperPlane, WandMagicSparkles, User, Close, Lightbulb, QuestionCircle, CirclePlus, Refresh, Messages } from 'flowbite-react-icons/outline'
import { toast } from 'sonner'
import { cn } from '@/lib/utils'
import { fetchWithCache, apiCache } from '@/lib/apiCache'
import { OutlineSkeleton } from './ModalSkeleton'
import { usePerformanceMonitor } from '@/lib/performance'
import { FeedbackChatModal } from './FeedbackChatModal'

const API_URL = import.meta.env.VITE_API_URL || 
  (typeof window !== 'undefined' && window.location.hostname === 'tilyn.ai' 
    ? 'https://tilyn.ai' 
    : 'http://localhost:8000')

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
  
  // Performance monitoring
  const { mark, measureAndLog } = usePerformanceMonitor('MeetingModal')
  
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [isGenerating, setIsGenerating] = useState(false)
  const [hasStarted, setHasStarted] = useState(false)
  const [sessionId, setSessionId] = useState<string>('')
  const [currentOutline, setCurrentOutline] = useState<string>('')
  const [parsedOutline, setParsedOutline] = useState<{
    talkingPoints: string[]
    questions: string[]
    whitepaperRelevance: string
  } | null>(null)
  const [isDebriefModalOpen, setIsDebriefModalOpen] = useState(false)
  
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

  // Parse outline into structured format
  const parseOutline = (outline: string) => {
    const talkingPoints: string[] = []
    const questions: string[] = []
    let whitepaperRelevance = ''
    
    const lines = outline.split('\n')
    let currentSection = ''
    
    for (const line of lines) {
      const trimmed = line.trim()
      
      if (trimmed.includes('KEY TALKING POINTS') || trimmed.includes('TALKING POINTS')) {
        currentSection = 'talking'
        continue
      } else if (trimmed.includes('CRITICAL QUESTIONS') || trimmed.includes('QUESTIONS')) {
        currentSection = 'questions'
        continue
      } else if (trimmed.includes('WHITEPAPER RELEVANCE')) {
        currentSection = 'whitepaper'
        continue
      }
      
      // Extract numbered items
      const match = trimmed.match(/^(\d+\.|\d+\))\s+(.+)/)
      if (match && match[2]) {
        if (currentSection === 'talking') {
          talkingPoints.push(match[2])
        } else if (currentSection === 'questions') {
          questions.push(match[2])
        }
      } else if (currentSection === 'whitepaper' && trimmed && !trimmed.match(/^[═─]+$/)) {
        whitepaperRelevance += trimmed + ' '
      }
    }
    
    return { talkingPoints, questions, whitepaperRelevance: whitepaperRelevance.trim() }
  }

  // Reset on close
  useEffect(() => {
    if (!isOpen) {
      setMessages([])
      setInput('')
      setSessionId('')
      setCurrentOutline('')
      setParsedOutline(null)
      setIsLoading(false)
      setIsGenerating(false)
      setHasStarted(false)
      isInitialMount.current = true
    }
  }, [isOpen])

  // Generate session ID on open (don't call API automatically)
  useEffect(() => {
    if (isOpen && !sessionId) {
      const newSessionId = `meeting_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
      setSessionId(newSessionId)
    }
  }, [isOpen])

  const generateInitialOutline = async (sessionId: string) => {
    setIsGenerating(true)
    mark('apiCall')
    
    // Show informative toast
    toast.loading('Generating meeting outline... This may take up to 60 seconds.', { 
      id: 'outline-generation',
      duration: 60000 
    })
    
    const apiStartTime = performance.now()

    try {
      const params = new URLSearchParams({
        user_id: userId,
        startup_id: startupId,
        startup_name: startupName,
        startup_description: startupDescription
      })
      
      const url = `${API_URL}/whitepaper/meeting-prep/start?${params}`
      
      // Use cached fetch with 60 second timeout (LLM generation takes time)
      const cacheKey = `meeting_outline_${startupId}`
      const data = await fetchWithCache(
        url,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' }
        },
        cacheKey,
        1800000, // Cache for 30 minutes
        60000 // 60 second timeout for LLM generation
      )
      
      const apiDuration = performance.now() - apiStartTime
      console.log(`✅ API call completed in ${apiDuration.toFixed(2)}ms`)
      measureAndLog('apiCall', 'API Response Time')
      
      if (data.success && data.outline) {
        console.log('✅ Outline generated successfully, length:', data.outline.length)
        setCurrentOutline(data.outline)
        setParsedOutline(parseOutline(data.outline))
        
        measureAndLog('contentLoad', 'Content Load Time')
        
        // Don't add assistant message, just show toast
        setMessages([])
        toast.success('Meeting outline generated!', { id: 'outline-generation' })
      } else {
        console.error('❌ API returned non-success:', data)
        toast.dismiss('outline-generation')
        throw new Error(data.error || 'Failed to generate outline')
      }
    } catch (error) {
      const apiDuration = performance.now() - apiStartTime
      console.error(`❌ Failed to generate initial outline after ${apiDuration.toFixed(2)}ms:`, error)
      
      // Dismiss loading toast
      toast.dismiss('outline-generation')
      
      if (error instanceof Error) {
        console.error('Error details:', {
          name: error.name,
          message: error.message,
          stack: error.stack
        })
        
        if (error.message === 'Request timeout') {
          toast.error('Request timed out. The outline generation is taking longer than expected. Please try again.')
        } else {
          toast.error(`Failed to generate meeting outline: ${error.message}`)
        }
      } else {
        toast.error('Failed to generate meeting outline')
      }
      
      // Don't add error message to chat
      setMessages([])
    } finally {
      setIsGenerating(false)
    }
  }

  const regenerateOutline = async () => {
    if (isLoading || isGenerating) return

    setIsGenerating(true)

    try {
      const params = new URLSearchParams({
        user_id: userId,
        startup_id: startupId,
        startup_name: startupName,
        startup_description: startupDescription
      })
      
      // Clear cache for this startup to force fresh generation
      const cacheKey = `meeting_outline_${startupId}`
      apiCache.delete(cacheKey)
      
      // Use cached fetch with timeout
      const data = await fetchWithCache(
        `${API_URL}/whitepaper/meeting-prep/start?${params}`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' }
        },
        cacheKey,
        1800000, // Cache for 30 minutes
        10000 // 10 second timeout
      )
      
      if (data.success && data.outline) {
        setCurrentOutline(data.outline)
        setParsedOutline(parseOutline(data.outline))
        
        // Don't add assistant message
        toast.success('Outline regenerated!')
      }
    } catch (error) {
      console.error('Failed to regenerate outline:', error)
      toast.error('Failed to regenerate outline')
    } finally {
      setIsGenerating(false)
    }
  }

  const handleSend = async () => {
    if (!input.trim() || isLoading || isGenerating) return

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
      const params = new URLSearchParams({
        session_id: sessionId,
        message: userMessage.content,
        startup_name: startupName,
        startup_description: startupDescription,
        previous_outline: currentOutline
      })
      
      const response = await fetch(`${API_URL}/whitepaper/meeting-prep/chat?${params}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      })

      if (!response.ok) throw new Error('Failed to send message')
      
      const data = await response.json()
      
      if (data.success && data.outline) {
        setCurrentOutline(data.outline)
        setParsedOutline(parseOutline(data.outline))
        
        // Just update the outline, don't add assistant message
        toast.success('Outline updated based on your feedback')
      } else {
        throw new Error(data.error || 'Failed to process message')
      }
    } catch (error) {
      console.error('Failed to send message:', error)
      toast.error('Failed to send message')
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
    <TailwindModal isOpen={isOpen} onClose={onClose} size="xl" className="p-0 flex flex-col max-md:h-full md:h-[90vh] md:max-h-[90vh]">
      {/* Header */}
      <div className="flex-shrink-0 border-b border-gray-700 dark:border-gray-700 bg-gray-800 dark:bg-gray-800 px-4 py-3 md:px-6 md:py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="flex items-center justify-center w-10 h-10 rounded-lg bg-gradient-to-br from-blue-500 to-indigo-600 shadow-md">
              <Briefcase className="text-white w-5 h-5"  />
            </div>
            <div className="flex-1 min-w-0">
              <h2 className="text-lg font-bold text-white">
                Meeting Preparation
              </h2>
              <p className="text-sm text-gray-300 truncate">
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
              <Close className="w-5 h-5"  />
            </Button>
          </div>
        </div>
      </div>

        {/* Welcome Screen - Before Generation */}
        {!hasStarted && !parsedOutline && (
          <div className="flex-1 border-b border-gray-200 dark:border-gray-700 bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-gray-800 dark:to-gray-850 px-6 py-8 overflow-y-auto flex items-center justify-center">
            <div className="max-w-md text-center space-y-6">
              <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-2xl flex items-center justify-center mx-auto shadow-lg">
                <WandMagicSparkles className="w-8 h-8 text-white" />
              </div>
              <div className="space-y-2">
                <h3 className="text-xl font-bold text-gray-900 dark:text-white">
                  AI Meeting Preparation
                </h3>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Generate a personalized meeting outline with key talking points and strategic questions for <span className="font-semibold text-gray-900 dark:text-white">{startupName}</span>.
                </p>
              </div>
              <Button
                onClick={() => {
                  setHasStarted(true)
                  mark('contentLoad')
                  generateInitialOutline(sessionId)
                }}
                className="w-full bg-gradient-to-r from-blue-500 to-indigo-600 hover:from-blue-600 hover:to-indigo-700 text-white font-semibold py-3 rounded-lg shadow-md transition-all"
                size="lg"
              >
                <WandMagicSparkles className="w-5 h-5 mr-2" />
                Generate Meeting Outline
              </Button>
            </div>
          </div>
        )}

        {/* Loading State with Skeleton - Full Screen */}
        {hasStarted && isGenerating && !parsedOutline && (
          <div className="flex-1 border-b border-gray-200 dark:border-gray-700 bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-gray-800 dark:to-gray-850 px-6 py-4 overflow-y-auto">
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-bold text-gray-900 dark:text-white uppercase tracking-wide">
                  Generating Meeting Outline...
                </h3>
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                  <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                  <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                </div>
              </div>
              
              {/* Talking Points Skeleton */}
              <OutlineSkeleton />
              <OutlineSkeleton />
              
              {/* Questions Skeleton */}
              <OutlineSkeleton />
              <OutlineSkeleton />
              
              {/* More skeleton items to fill screen */}
              <OutlineSkeleton />
              <OutlineSkeleton />
            </div>
          </div>
        )}

        {/* Static Outline Display - Expanded and Scrollable */}
        {parsedOutline && (
          <div className="flex-1 border-b border-gray-200 dark:border-gray-700 bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-gray-800 dark:to-gray-850 px-6 py-4 overflow-y-auto">
            <div className="space-y-4">
              <div className="flex items-center justify-between sticky top-0 bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-gray-800 dark:to-gray-850 pb-3 z-10">
                <h3 className="text-sm font-bold text-gray-900 dark:text-white uppercase tracking-wide">
                  Meeting Outline
                </h3>
                <Badge className="bg-blue-500 text-white text-xs">
                  Generated
                </Badge>
              </div>
              
              {/* Talking Points */}
              {parsedOutline.talkingPoints.length > 0 && (
                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    <Briefcase className="w-4 h-4 text-blue-600 dark:text-blue-400" />
                    <h4 className="text-xs font-bold text-blue-900 dark:text-blue-300 uppercase">
                      Key Talking Points
                    </h4>
                  </div>
                  <div className="space-y-2">
                    {parsedOutline.talkingPoints.map((point, idx) => (
                      <div 
                        key={idx}
                        className="flex gap-2 items-start bg-white dark:bg-gray-800 rounded-lg px-3 py-2 border border-blue-200 dark:border-blue-800/50"
                      >
                        <span className="flex-shrink-0 flex items-center justify-center w-5 h-5 rounded-full bg-blue-500 text-white text-xs font-bold">
                          {idx + 1}
                        </span>
                        <p className="text-xs text-gray-700 dark:text-gray-300 leading-relaxed">
                          {point}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
              
              {/* Critical Questions */}
              {parsedOutline.questions.length > 0 && (
                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    <QuestionCircle className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
                    <h4 className="text-xs font-bold text-indigo-900 dark:text-indigo-300 uppercase">
                      Critical Questions
                    </h4>
                  </div>
                  <div className="space-y-2">
                    {parsedOutline.questions.map((question, idx) => (
                      <div 
                        key={idx}
                        className="flex gap-2 items-start bg-white dark:bg-gray-800 rounded-lg px-3 py-2 border border-indigo-200 dark:border-indigo-800/50"
                      >
                        <span className="flex-shrink-0 flex items-center justify-center w-5 h-5 rounded-full bg-indigo-500 text-white text-xs font-bold">
                          {idx + 1}
                        </span>
                        <p className="text-xs text-gray-700 dark:text-gray-300 leading-relaxed">
                          {question}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
              
              {/* Whitepaper Relevance */}
              {parsedOutline.whitepaperRelevance && (
                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    <Lightbulb className="w-4 h-4 text-purple-600 dark:text-purple-400" />
                    <h4 className="text-xs font-bold text-purple-900 dark:text-purple-300 uppercase">
                      Whitepaper Relevance
                    </h4>
                  </div>
                  <div className="bg-white dark:bg-gray-800 rounded-lg px-3 py-2 border border-purple-200 dark:border-purple-800/50">
                    <p className="text-xs text-gray-700 dark:text-gray-300 leading-relaxed">
                      {parsedOutline.whitepaperRelevance}
                    </p>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

      {/* Footer with Action Buttons */}
      <div className="flex-shrink-0 border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 px-6 py-4">
        <div className="flex gap-3">
          <Button
            onClick={regenerateOutline}
            disabled={isLoading || isGenerating || !parsedOutline}
            variant="outline"
            size="sm"
            className="gap-2 flex-1"
          >
            <Refresh className="w-4 h-4"  />
            {isGenerating ? 'Regenerating...' : 'Regenerate Outline'}
          </Button>
          <Button
            onClick={() => setIsDebriefModalOpen(true)}
            disabled={!parsedOutline}
            size="sm"
            className="gap-2 flex-1 bg-gradient-to-r from-purple-500 to-indigo-600 hover:from-purple-600 hover:to-indigo-700 text-white"
          >
            <Messages className="w-4 h-4" />
            Start Post-Meeting Debrief
          </Button>
        </div>
        <p className="text-xs text-gray-500 dark:text-gray-400 mt-2 text-center">
          After your meeting, use the debrief to capture insights and learnings
        </p>
      </div>

      {/* Feedback Chat Modal for Debrief */}
      <FeedbackChatModal
        isOpen={isDebriefModalOpen}
        onClose={() => setIsDebriefModalOpen(false)}
        userId={userId}
        startupId={startupId}
        startupName={startupName}
        startupDescription={startupDescription}
      />
    </TailwindModal>
  )
}
