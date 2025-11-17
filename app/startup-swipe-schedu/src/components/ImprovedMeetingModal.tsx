import { useState, useEffect } from 'react'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Card } from '@/components/ui/card'
import { Briefcase, Lightbulb, QuestionCircle, Close, CheckCircle, Refresh, FileCopy } from 'flowbite-react-icons/outline'
import { motion, AnimatePresence } from 'framer-motion'
import { toast } from 'sonner'
import { cn } from '@/lib/utils'

interface TalkingPoint {
  title: string
  description: string
}

interface CriticalQuestion {
  title: string
  question: string
}

interface ImprovedMeetingModalProps {
  isOpen: boolean
  onClose: () => void
  userId: string
  startup?: any
  startupId?: string
  startupName?: string
  startupDescription?: string
}

export function ImprovedMeetingModal({
  isOpen,
  onClose,
  userId,
  startup,
  startupId: propStartupId,
  startupName: propStartupName,
  startupDescription: propStartupDescription
}: ImprovedMeetingModalProps) {
  // Extract data from startup object if provided, otherwise use individual props
  const startupId = startup?.id || propStartupId || 'unknown'
  const startupName = startup?.name || startup?.['Company Name'] || propStartupName || 'Unknown Startup'
  const startupDescription = startup?.description || startup?.['Company Description'] || propStartupDescription || 'No description provided'
  
  const [talkingPoints, setTalkingPoints] = useState<TalkingPoint[]>([])
  const [criticalQuestions, setCriticalQuestions] = useState<CriticalQuestion[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [feedback, setFeedback] = useState('')
  const [hasGenerated, setHasGenerated] = useState(false)
  const [rawOutline, setRawOutline] = useState('')
  const [isRefining, setIsRefining] = useState(false)
  const [sessionId, setSessionId] = useState<string>('')

  // Reset state when modal closes
  useEffect(() => {
    if (!isOpen) {
      setTalkingPoints([])
      setCriticalQuestions([])
      setError(null)
      setFeedback('')
      setHasGenerated(false)
      setRawOutline('')
      setIsRefining(false)
      setSessionId('')
    }
  }, [isOpen])

  useEffect(() => {
    if (isOpen && !hasGenerated && startupId !== 'unknown') {
      loadOrGenerateOutline()
    }
  }, [isOpen])

  const loadOrGenerateOutline = async () => {
    setIsLoading(true)
    setError(null)
    
    try {
      // First, try to load existing outline from database
      const loadParams = new URLSearchParams({
        startup_id: startupId || 'unknown',
        startup_name: startupName,
        user_id: userId
      })
      
      const loadResponse = await fetch(
        `${import.meta.env.VITE_API_URL}/whitepaper/meeting-prep/load?${loadParams}`
      )
      
      if (loadResponse.ok) {
        const loadData = await loadResponse.json()
        if (loadData.found && loadData.outline) {
          // Use existing outline
          setRawOutline(loadData.outline)
          parseOutline(loadData.outline)
          setHasGenerated(true)
          setIsLoading(false)
          return
        }
      }
      
      // If not found, generate new outline
      generateOutline()
    } catch (err) {
      console.error('Error loading outline:', err)
      // Fallback to generating new outline
      generateOutline()
    }
  }

  const generateOutline = async () => {
    setIsLoading(true)
    setError(null)
    
    try {
      const params = new URLSearchParams({
        user_id: userId,
        startup_id: startupId || 'unknown',
        startup_name: startupName,
        startup_description: startupDescription || 'No description provided'
      })
      
      const response = await fetch(`${import.meta.env.VITE_API_URL}/whitepaper/meeting-prep/start?${params}`, {
        method: 'POST',
      })

      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`)
      }

      const data = await response.json()
      if (!data.success) {
        throw new Error(data.error || 'Failed to initialize')
      }

      setSessionId(data.session_id || `session_${Date.now()}`)
      setRawOutline(data.outline)
      parseOutline(data.outline)
      setHasGenerated(true)
      toast.success('Meeting prep generated!')
      
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error'
      setError(`Failed to generate meeting prep: ${errorMessage}`)
      toast.error('Failed to generate meeting prep')
    } finally {
      setIsLoading(false)
    }
  }

  const parseOutline = (outline: string) => {
    // Extract talking points (3 items)
    const tpMatch = outline.match(/📌 KEY TALKING POINTS:([\s\S]*?)❓ CRITICAL QUESTIONS:/)
    const points: TalkingPoint[] = []
    
    if (tpMatch) {
      const tpText = tpMatch[1]
      const lines = tpText.split('\n').filter(l => l.trim().match(/^\d+\./))
      lines.slice(0, 3).forEach((line, idx) => {
        const cleaned = line.replace(/^\s*\d+\.\s*/, '').trim()
        points.push({
          title: `Key Point ${idx + 1}`,
          description: cleaned
        })
      })
    }

    // Extract critical questions (3 items)
    const cqMatch = outline.match(/❓ CRITICAL QUESTIONS:([\s\S]*?)🎯 WHITEPAPER RELEVANCE:/)
    const questions: CriticalQuestion[] = []
    
    if (cqMatch) {
      const cqText = cqMatch[1]
      const lines = cqText.split('\n').filter(l => l.trim().match(/^\d+\./))
      lines.slice(0, 3).forEach((line, idx) => {
        const cleaned = line.replace(/^\s*\d+\.\s*/, '').trim()
        questions.push({
          title: `Critical Question ${idx + 1}`,
          question: cleaned
        })
      })
    }

    setTalkingPoints(points)
    setCriticalQuestions(questions)
  }

  const updateOutlineWithFeedback = async () => {
    if (!feedback.trim()) {
      toast.error('Please enter feedback to refine the meeting prep')
      return
    }

    setIsRefining(true)
    setError(null)

    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/whitepaper/meeting-prep/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId || `session_${Date.now()}`,
          user_id: userId,
          startup_id: startupId,
          message: feedback,
          startup_name: startupName,
          startup_description: startupDescription,
          previous_outline: rawOutline
        })
      })

      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`)
      }

      const data = await response.json()
      if (!data.success) {
        throw new Error(data.error || 'Failed to update')
      }

      setRawOutline(data.outline)
      parseOutline(data.outline)
      setFeedback('')
      toast.success('Meeting prep refined!')
      
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error'
      setError(`Failed to refine outline: ${errorMessage}`)
      toast.error('Failed to refine meeting prep')
    } finally {
      setIsRefining(false)
    }
  }

  const regenerateOutline = async () => {
    // Reset state and force new generation
    setHasGenerated(false)
    setTalkingPoints([])
    setCriticalQuestions([])
    setRawOutline('')
    setSessionId('')
    setFeedback('')
    // Now generate fresh outline
    await generateOutline()
  }

  const copyToClipboard = (text: string, label: string) => {
    navigator.clipboard.writeText(text)
    toast.success(`${label} copied to clipboard!`)
  }

  const renderLoadingState = () => (
    <div className="flex flex-col items-center justify-center py-16 px-4">
      <motion.div
        animate={{ rotate: 360 }}
        transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
        className="mb-6"
      >
        <Briefcase className="text-blue-500 w-14 h-14"  />
      </motion.div>
      <p className="text-xl font-bold text-gray-700 dark:text-gray-300 mb-3">
        Preparing Your Meeting...
      </p>
      <p className="text-sm text-gray-500 dark:text-gray-400 text-center max-w-md">
        AI is analyzing {startupName} and creating a comprehensive meeting guide
      </p>
      <div className="mt-6 flex gap-2">
        {[0, 1, 2].map((i) => (
          <motion.div
            key={i}
            animate={{ scale: [1, 1.2, 1], opacity: [0.5, 1, 0.5] }}
            transition={{ duration: 1, repeat: Infinity, delay: i * 0.2 }}
            className="w-2 h-2 rounded-full bg-blue-500"
          />
        ))}
      </div>
    </div>
  )

  const renderContent = () => (
    <div className="space-y-6 p-6 max-h-[600px] overflow-y-auto">
      {/* Talking Points */}
      <div>
        <div className="flex items-center gap-3 mb-4">
          <Lightbulb className="text-amber-500 w-7 h-7"  />
          <h3 className="text-xl font-bold text-gray-900 dark:text-white">Key Talking Points</h3>
        </div>
        
        <div className="space-y-3">
          {talkingPoints.map((point, idx) => (
            <motion.div
              key={idx}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: idx * 0.1 }}
            >
              <Card className="p-4 border-2 border-amber-200 dark:border-amber-800 bg-gradient-to-br from-amber-50 to-yellow-50 dark:from-amber-950/30 dark:to-yellow-950/30 shadow-md hover:shadow-lg transition-shadow">
                <div className="flex items-start justify-between gap-3">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="flex items-center justify-center w-7 h-7 rounded-full bg-amber-500 text-white font-bold text-sm">
                        {idx + 1}
                      </span>
                      <h4 className="font-bold text-gray-900 dark:text-white">{point.title}</h4>
                    </div>
                    <p className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed pl-9">
                      {point.description}
                    </p>
                  </div>
                  <button
                    onClick={() => copyToClipboard(point.description, 'Talking point')}
                    className="p-2 rounded-lg hover:bg-amber-100 dark:hover:bg-amber-900/30 transition-colors"
                  >
                    <FileCopy className="text-amber-600 dark:text-amber-400 w-5 h-5"  />
                  </button>
                </div>
              </Card>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Critical Questions */}
      <div>
        <div className="flex items-center gap-3 mb-4">
          <QuestionCircle className="text-blue-500 w-7 h-7"  />
          <h3 className="text-xl font-bold text-gray-900 dark:text-white">Critical Questions</h3>
        </div>
        
        <div className="space-y-3">
          {criticalQuestions.map((item, idx) => (
            <motion.div
              key={idx}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: (idx + 3) * 0.1 }}
            >
              <Card className="p-4 border-2 border-blue-200 dark:border-blue-800 bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-950/30 dark:to-indigo-950/30 shadow-md hover:shadow-lg transition-shadow">
                <div className="flex items-start justify-between gap-3">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="flex items-center justify-center w-7 h-7 rounded-full bg-blue-500 text-white font-bold text-sm">
                        {idx + 1}
                      </span>
                      <h4 className="font-bold text-gray-900 dark:text-white">{item.title}</h4>
                    </div>
                    <p className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed pl-9">
                      {item.question}
                    </p>
                  </div>
                  <button
                    onClick={() => copyToClipboard(item.question, 'Question')}
                    className="p-2 rounded-lg hover:bg-blue-100 dark:hover:bg-blue-900/30 transition-colors"
                  >
                    <FileCopy className="text-blue-600 dark:text-blue-400 w-5 h-5"  />
                  </button>
                </div>
              </Card>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Refinement Section */}
      <div className="pt-4 border-t-2 border-gray-200 dark:border-gray-700">
        <h4 className="text-sm font-bold text-gray-900 dark:text-white mb-3">
          Need to refine the meeting prep?
        </h4>
        <div className="flex gap-2">
          <Textarea
            value={feedback}
            onChange={(e) => setFeedback(e.target.value)}
            placeholder="E.g., 'Focus more on technical architecture' or 'Add questions about pricing model'"
            className="flex-1 min-h-[80px]"
            disabled={isRefining}
          />
        </div>
        <div className="flex gap-2 mt-3">
          <Button
            onClick={updateOutlineWithFeedback}
            disabled={isRefining || !feedback.trim()}
            className="bg-gradient-to-r from-purple-500 to-pink-600 hover:from-purple-600 hover:to-pink-700 text-white gap-2"
          >
            <Refresh className={isRefining ? "animate-spin" : ""}  />
            {isRefining ? 'Refining...' : 'Refine Meeting Prep'}
          </Button>
          <Button
            onClick={regenerateOutline}
            variant="outline"
            disabled={isLoading || isRefining}
            className="gap-2"
          >
            <Briefcase className="w-5 h-5"  />
            Regenerate
          </Button>
        </div>
      </div>

      {/* Success indicator at bottom */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center gap-2 p-3 bg-green-50 dark:bg-green-900/20 border-2 border-green-200 dark:border-green-800 rounded-lg"
      >
        <CheckCircle className="text-green-600 dark:text-green-400 w-5 h-5"   />
        <p className="text-sm font-semibold text-green-700 dark:text-green-300">
          Meeting prep ready! You can copy individual items or refine as needed.
        </p>
      </motion.div>
    </div>
  )

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl p-0 gap-0 bg-white dark:bg-gray-800 border-2 border-gray-300 dark:border-gray-600">
        <DialogHeader className="p-6 pb-4 border-b-2 border-gray-200 dark:border-gray-700 bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-950/30 dark:to-indigo-950/30">
          <DialogTitle className="text-2xl font-bold flex items-center gap-3">
            <Briefcase className="text-blue-500 w-8 h-8"  />
            <div>
              <span className="bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                Meeting AI
              </span>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400 mt-1">
                Prep for {startupName}
              </p>
            </div>
          </DialogTitle>
        </DialogHeader>

        {error && (
          <div className="mx-6 mt-4 p-4 bg-red-50 dark:bg-red-900/20 border-2 border-red-200 dark:border-red-800 rounded-lg">
            <p className="text-sm font-semibold text-red-700 dark:text-red-400">{error}</p>
          </div>
        )}

        <div className="relative">
          <AnimatePresence mode="wait">
            {isLoading && !hasGenerated ? (
              <motion.div
                key="loading"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
              >
                {renderLoadingState()}
              </motion.div>
            ) : (
              <motion.div
                key="content"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
              >
                {renderContent()}
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </DialogContent>
    </Dialog>
  )
}
