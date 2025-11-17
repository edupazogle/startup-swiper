import { useState, useEffect } from 'react'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { WandMagicSparkles, ArrowRight } from 'flowbite-react-icons/outline'
import { motion, AnimatePresence } from 'framer-motion'
import { toast } from 'sonner'

interface AIRecommendationsProps {
  startups: any[]
  votes: any[]
  currentUserId: string
  onStartupClick?: (startupId: string) => void
}

interface Recommendation {
  startupId: string
  reason: string
  confidence: number
}

export function AIRecommendations({ startups, votes, currentUserId, onStartupClick }: AIRecommendationsProps) {
  const [recommendations, setRecommendations] = useState<Recommendation[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [isVisible, setIsVisible] = useState(true)

  const userVotes = votes.filter(v => v.userId === currentUserId)
  const interestedStartups = startups.filter(s => 
    userVotes.some(v => v.startupId === s.id && v.interested)
  )

  const shouldShowRecommendations = interestedStartups.length >= 2 && recommendations.length === 0

  useEffect(() => {
    if (shouldShowRecommendations && !isLoading) {
      generateRecommendations()
    }
  }, [interestedStartups.length])

  const generateRecommendations = async () => {
    if (isLoading) return
    
    setIsLoading(true)
    try {
      const unseenStartups = startups.filter(s => 
        !userVotes.some(v => v.startupId === s.id)
      )

      if (unseenStartups.length === 0) {
        setIsLoading(false)
        return
      }

      const interestedCategories = [...new Set(interestedStartups.map(s => s.Category))]
      const interestedStages = [...new Set(interestedStartups.map(s => s.Stage))]

      const context = `
Based on user interests, recommend top 3 startups from the unseen list.

User has shown interest in:
- Categories: ${interestedCategories.join(', ')}
- Stages: ${interestedStages.join(', ')}
- Companies: ${interestedStartups.slice(0, 3).map(s => s["Company Name"]).join(', ')}

Unseen startups (pick 3 best matches):
${unseenStartups.slice(0, 10).map((s, i) => 
  `${i + 1}. ${s["Company Name"]} (${s.Category}, ${s.Stage}) - ${s["Company Description"].slice(0, 100)}`
).join('\n')}

Return recommendations as JSON:
{
  "recommendations": [
    {
      "startupId": "startup-id",
      "reason": "brief reason why this matches user interests (max 80 chars)",
      "confidence": 0.95
    }
  ]
}

Only recommend startups that genuinely match the user's interests.
`

      const response = await window.spark.llm(context, 'gpt-4o', true)
      const data = JSON.parse(response)

      if (data.recommendations && Array.isArray(data.recommendations)) {
        const validRecs = data.recommendations
          .filter((r: any) => unseenStartups.some(s => s.id === r.startupId))
          .slice(0, 3)
        
        setRecommendations(validRecs)
        if (validRecs.length > 0) {
          toast.success('AI found some great matches for you!')
        }
      }
    } catch (error) {
      console.error('Failed to generate recommendations:', error)
    } finally {
      setIsLoading(false)
    }
  }

  if (!isVisible || recommendations.length === 0) {
    return null
  }

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -20 }}
        className="mb-4"
      >
        <Card className="p-4 bg-gradient-to-br from-primary/10 to-accent/10 border-primary/20">
          <div className="flex items-start justify-between mb-3">
            <div className="flex items-center gap-2">
              <WandMagicSparkles className="text-primary w-5 h-5"  />
              <h3 className="font-semibold text-sm">AI Recommendations</h3>
            </div>
            <Button
              variant="ghost"
              size="sm"
              className="h-6 text-xs -mt-1 -mr-2"
              onClick={() => setIsVisible(false)}
            >
              Dismiss
            </Button>
          </div>

          <p className="text-xs text-muted-foreground mb-3">
            Based on your interests, we think you'll like these:
          </p>

          <div className="space-y-2">
            {recommendations.map((rec, idx) => {
              const startup = startups.find(s => s.id === rec.startupId)
              if (!startup) return null

              return (
                <motion.div
                  key={rec.startupId}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: idx * 0.1 }}
                >
                  <Card className="p-3 hover:bg-muted/50 transition-colors cursor-pointer" onClick={() => onStartupClick?.(rec.startupId)}>
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <h4 className="font-semibold text-sm truncate">
                            {startup["Company Name"]}
                          </h4>
                          <Badge variant="secondary" className="text-[10px]">
                            {Math.round(rec.confidence * 100)}% match
                          </Badge>
                        </div>
                        <p className="text-xs text-muted-foreground mb-2">
                          {rec.reason}
                        </p>
                        <div className="flex gap-1 flex-wrap">
                          <Badge variant="outline" className="text-[10px]">
                            {startup.Category}
                          </Badge>
                          <Badge variant="outline" className="text-[10px]">
                            {startup.Stage}
                          </Badge>
                        </div>
                      </div>
                      <ArrowRight className="text-muted-foreground flex-shrink-0 mt-1 w-4 h-4"  />
                    </div>
                  </Card>
                </motion.div>
              )
            })}
          </div>

          <Button
            variant="outline"
            size="sm"
            className="w-full mt-3 gap-2"
            onClick={generateRecommendations}
            disabled={isLoading}
          >
            <WandMagicSparkles size={14} className={isLoading ? 'animate-pulse' : ''}  />
            {isLoading ? 'Finding more...' : 'Refresh Recommendations'}
          </Button>
        </Card>
      </motion.div>
    </AnimatePresence>
  )
}
