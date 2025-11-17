import { useState, useEffect } from 'react'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Card } from '@/components/ui/card'
import { Sparkle, Share, Copy, Question } from '@phosphor-icons/react'
import { motion } from 'framer-motion'
import { toast } from 'sonner'

interface TalkingPoint {
  title: string
  description: string
}

interface CriticalQuestion {
  title: string
  question: string
}

interface MeetingAIModalProps {
  isOpen: boolean
  onClose: () => void
  userId: string
  startup?: any
  startupId?: string
  startupName?: string
  startupDescription?: string
}

export function MeetingAIModal({
  isOpen,
  onClose,
  userId,
  startup,
  startupId: propStartupId,
  startupName: propStartupName,
  startupDescription: propStartupDescription
}: MeetingAIModalProps) {
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

  useEffect(() => {
    if (isOpen && !hasGenerated && startupId !== 'unknown') {
      console.log(`[MeetingAIModal] Opening for startup: ${startupName} (ID: ${startupId})`)
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

      setRawOutline(data.outline)
      parseOutline(data.outline)
      setHasGenerated(true)
      
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error'
      setError(`Failed to generate outline: ${errorMessage}`)
      toast.error('Failed to generate outline')
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
          title: `Point ${idx + 1}`,
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
          title: `Question ${idx + 1}`,
          question: cleaned
        })
      })
    }

    setTalkingPoints(points)
    setCriticalQuestions(questions)
  }

  const updateOutlineWithFeedback = async () => {
    if (!feedback.trim()) return

    setIsLoading(true)
    setError(null)

    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/whitepaper/meeting-prep/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: `session_${Date.now()}`,
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
      toast.success('Outline updated with your feedback')
      
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error'
      setError(`Failed to update: ${errorMessage}`)
      toast.error('Failed to update outline')
    } finally {
      setIsLoading(false)
    }
  }

  const shareByEmail = () => {
    const subject = `Meeting Prep: ${startupName}`
    const body = `Hi,\n\nHere's the meeting preparation brief for ${startupName}.\n\nKEY TALKING POINTS:\n${talkingPoints.map((p, i) => `${i + 1}. ${p.description}`).join('\n')}\n\nCRITICAL QUESTIONS:\n${criticalQuestions.map((q, i) => `${i + 1}. ${q.question}`).join('\n')}\n\nGenerated: ${new Date().toLocaleString()}`
    const mailtoLink = `mailto:?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`
    window.location.href = mailtoLink
    toast.success('Opening email client...')
  }

  const copyToClipboard = () => {
    const content = `MEETING PREP: ${startupName}\n\nKEY TALKING POINTS:\n${talkingPoints.map((p, i) => `${i + 1}. ${p.description}`).join('\n')}\n\nCRITICAL QUESTIONS:\n${criticalQuestions.map((q, i) => `${i + 1}. ${q.question}`).join('\n')}`
    navigator.clipboard.writeText(content)
    toast.success('Copied to clipboard!')
  }

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="flex flex-col h-[90vh] w-full max-w-4xl rounded-lg border p-0 md:p-4 overflow-hidden">
        <DialogHeader className="sr-only">
          <DialogTitle>AI Meeting Preparation for {startupName}</DialogTitle>
          <DialogDescription>
            AI-generated talking points and critical questions to help prepare for your meeting with {startupName}.
          </DialogDescription>
        </DialogHeader>
        
        {/* Visible Header */}
        <div className="flex-shrink-0 border-b px-4 md:px-6 py-3 md:py-4">
          <div className="flex items-center justify-between gap-3">
            <div className="flex items-center gap-2 min-w-0">
              <Sparkle size={20} weight="duotone" className="text-purple-500 flex-shrink-0" />
              <div className="min-w-0">
                <h2 className="font-semibold text-sm md:text-base truncate" aria-hidden="true">Meeting Prep: {startupName}</h2>
                <p className="text-xs text-muted-foreground mt-0.5">Talking points & critical questions</p>
              </div>
            </div>
            <div className="flex gap-2 flex-shrink-0">
              <Button
                size="sm"
                variant="ghost"
                onClick={copyToClipboard}
                title="Copy to clipboard"
                aria-label="Copy to clipboard"
              >
                <Copy size={16} />
              </Button>
              <Button
                size="sm"
                variant="ghost"
                onClick={shareByEmail}
                title="Share via email"
                aria-label="Share via email"
              >
                <Share size={16} />
              </Button>
            </div>
          </div>
        </div>

        {/* Content */}
        {!error && hasGenerated && (
          <div className="flex-1 overflow-hidden flex flex-col md:flex-row gap-0 md:gap-4">
            {/* Left Column: Talking Points */}
            <div className="flex-1 flex flex-col overflow-hidden md:border-r">
              <div className="flex-shrink-0 px-4 md:px-6 py-3 border-b">
                <h3 className="font-semibold text-sm md:text-base flex items-center gap-2">
                  <Sparkle size={16} weight="duotone" className="text-primary" />
                  <span>Key Talking Points</span>
                </h3>
              </div>
              <div className="flex-1 overflow-y-auto px-4 md:px-6 py-3 md:py-4 space-y-2 md:space-y-3">
                {talkingPoints.map((point, idx) => (
                  <motion.div
                    key={idx}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: idx * 0.1 }}
                  >
                    <Card className="p-3 md:p-4 bg-background hover:border-purple-300 transition-colors">
                      <div className="text-xs font-medium text-primary mb-1.5">
                        Point {idx + 1}
                      </div>
                      <div className="text-xs md:text-sm leading-relaxed text-foreground">
                        {point.description}
                      </div>
                    </Card>
                  </motion.div>
                ))}
              </div>
            </div>

            {/* Right Column: Critical Questions */}
            <div className="flex-1 flex flex-col overflow-hidden">
              <div className="flex-shrink-0 px-4 md:px-6 py-3 border-b md:border-b-0">
                <h3 className="font-semibold text-sm md:text-base flex items-center gap-2">
                  <Question size={16} weight="duotone" className="text-primary" />
                  <span>Critical Questions</span>
                </h3>
              </div>
              <div className="flex-1 overflow-y-auto px-4 md:px-6 py-3 md:py-4 space-y-2 md:space-y-3">
                {criticalQuestions.map((cq, idx) => (
                  <motion.div
                    key={idx}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: idx * 0.1 }}
                  >
                    <Card className="p-3 md:p-4 bg-background hover:border-blue-300 transition-colors">
                      <div className="text-xs font-medium text-primary mb-1.5">
                        Q{idx + 1}
                      </div>
                      <div className="text-xs md:text-sm leading-relaxed text-foreground">
                        {cq.question}
                      </div>
                    </Card>
                  </motion.div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Loading State */}
        {isLoading && (
          <div className="flex-1 flex items-center justify-center">
            <div className="text-center space-y-3">
              <div className="flex justify-center gap-1">
                <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
              </div>
              <p className="text-xs md:text-sm text-muted-foreground">Generating outline...</p>
            </div>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="flex-1 flex flex-col items-center justify-center p-6">
            <p className="text-sm text-red-600 dark:text-red-400 mb-4 text-center">{error}</p>
            <Button size="sm" onClick={generateOutline}>Try Again</Button>
          </div>
        )}

        {/* Feedback Input */}
        {hasGenerated && !error && (
          <div className="flex-shrink-0 border-t px-4 md:px-6 py-3 md:py-4 bg-muted/50 space-y-2">
            <label className="text-xs font-medium text-foreground">Refine with feedback</label>
            <div className="flex gap-2">
              <Textarea
                value={feedback}
                onChange={(e) => setFeedback(e.target.value)}
                placeholder="Focus on claims automation, team's insurance experience..."
                className="min-h-[60px] md:min-h-[70px] resize-none text-xs md:text-sm"
                disabled={isLoading}
              />
              <Button
                onClick={updateOutlineWithFeedback}
                disabled={!feedback.trim() || isLoading}
                size="sm"
                className="self-end flex-shrink-0"
              >
                Update
              </Button>
            </div>
          </div>
        )}
      </DialogContent>
    </Dialog>
  )
}
