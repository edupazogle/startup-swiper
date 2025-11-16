import { useState } from 'react'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Sparkle, TrendUp, Target, Lightbulb } from '@phosphor-icons/react'
import { motion } from 'framer-motion'
import { toast } from 'sonner'
import { FeedbackChatModal } from '@/components/FeedbackChatModal'

interface AIStartupInsightsProps {
  startup: any
  userVotes: any[]
  userId?: string
  meetingId?: string
}

interface Insight {
  type: 'strength' | 'opportunity' | 'recommendation'
  content: string
}

export function AIStartupInsights({ startup, userVotes, userId, meetingId }: AIStartupInsightsProps) {
  const [insights, setInsights] = useState<Insight[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [hasGenerated, setHasGenerated] = useState(false)
  const [showFeedbackModal, setShowFeedbackModal] = useState(false)

  const generateInsights = async () => {
    setIsLoading(true)
    try {
      const interestedCategories = [...new Set(
        userVotes
          .filter(v => v.interested)
          .map(v => {
            const s = v.startup
            return s?.Category
          })
          .filter(Boolean)
      )]

      const context = `
Analyze this startup and provide 3-4 concise insights:

Startup: ${startup["Company Name"]}
Description: ${startup["Company Description"]}
Category: ${startup.Category}
Stage: ${startup.Stage}
USP: ${startup.USP}
Funding: ${startup.Funding}
Priority Score: ${startup["Final Priority Score"]}

User's interest patterns: ${interestedCategories.join(', ')}

Provide insights in JSON format with this structure:
{
  "insights": [
    {"type": "strength", "content": "brief insight"},
    {"type": "opportunity", "content": "brief insight"},
    {"type": "recommendation", "content": "brief insight"}
  ]
}

Focus on: key strengths, market opportunities, and why this startup might be relevant to someone interested in: ${interestedCategories.join(', ')}.
Keep each insight under 100 characters.
`

      const response = await window.spark.llm(context, 'gpt-4o', true)
      const data = JSON.parse(response)
      
      if (data.insights && Array.isArray(data.insights)) {
        setInsights(data.insights)
        setHasGenerated(true)
      }
    } catch (error) {
      toast.error('Failed to generate insights')
      console.error(error)
    } finally {
      setIsLoading(false)
    }
  }

  const getIcon = (type: string) => {
    switch (type) {
      case 'strength':
        return <TrendUp size={16} weight="duotone" className="text-green-500" />
      case 'opportunity':
        return <Target size={16} weight="duotone" className="text-blue-500" />
      case 'recommendation':
        return <Lightbulb size={16} weight="duotone" className="text-yellow-500" />
      default:
        return <Sparkle size={16} weight="duotone" className="text-primary" />
    }
  }

  const getLabel = (type: string) => {
    switch (type) {
      case 'strength':
        return 'Strength'
      case 'opportunity':
        return 'Opportunity'
      case 'recommendation':
        return 'Why This Matters'
      default:
        return 'Insight'
    }
  }

  if (!hasGenerated) {
    return (
      <>
        <Button
          onClick={() => setShowFeedbackModal(true)}
          disabled={isLoading}
          variant="outline"
          size="sm"
          className="w-full gap-2"
        >
          <Sparkle size={16} weight="fill" />
          Generate AI Insights
        </Button>
        
        {showFeedbackModal && (
          <FeedbackChatModal
            isOpen={showFeedbackModal}
            onClose={() => setShowFeedbackModal(false)}
            meetingId={meetingId || `meeting_${Date.now()}`}
            userId={userId || '1'}
            startupId={startup.id || startup["Company Name"]}
            startupName={startup["Company Name"] || startup.name}
            startupDescription={startup["Company Description"] || startup.description || ''}
          />
        )}
      </>
    )
  }

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <Sparkle size={18} weight="duotone" className="text-primary" />
          <span className="text-sm font-semibold">AI Insights</span>
        </div>
        <Button
          onClick={generateInsights}
          disabled={isLoading}
          variant="ghost"
          size="sm"
          className="h-7 text-xs"
        >
          Refresh
        </Button>
      </div>
      
      <div className="space-y-2">
        {insights.map((insight, idx) => (
          <motion.div
            key={idx}
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: idx * 0.1 }}
          >
            <Card className="p-3 bg-muted/30">
              <div className="flex gap-2">
                <div className="flex-shrink-0 mt-0.5">
                  {getIcon(insight.type)}
                </div>
                <div className="flex-1 min-w-0">
                  <Badge variant="secondary" className="text-[10px] mb-1">
                    {getLabel(insight.type)}
                  </Badge>
                  <p className="text-xs text-foreground/80 leading-relaxed">
                    {insight.content}
                  </p>
                </div>
              </div>
            </Card>
          </motion.div>
        ))}
      </div>
    </div>
  )
}
