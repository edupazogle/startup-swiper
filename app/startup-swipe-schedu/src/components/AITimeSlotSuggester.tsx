import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Card } from '@/components/ui/card'
import { Sparkle, Clock } from '@phosphor-icons/react'
import { motion, AnimatePresence } from 'framer-motion'
import { toast } from 'sonner'

interface TimeSlot {
  startTime: string
  endTime: string
  reason: string
}

interface AITimeSlotSuggesterProps {
  events: any[]
  onSelectTimeSlot: (start: string, end: string) => void
}

export function AITimeSlotSuggester({ events, onSelectTimeSlot }: AITimeSlotSuggesterProps) {
  const [suggestions, setSuggestions] = useState<TimeSlot[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [hasGenerated, setHasGenerated] = useState(false)

  const generateSuggestions = async () => {
    setIsLoading(true)
    try {
      const upcomingEvents = events
        .filter(e => new Date(e.startTime) > new Date())
        .map(e => ({
          title: e.title,
          start: new Date(e.startTime).toISOString(),
          end: new Date(e.endTime).toISOString()
        }))

      const context = `
You are a smart meeting scheduler for Slush 2025 (Nov 18-20, 2024).

Existing upcoming meetings:
${upcomingEvents.map(e => `- ${e.title}: ${new Date(e.start).toLocaleString()} to ${new Date(e.end).toLocaleString()}`).join('\n')}

Suggest 3 optimal 30-minute meeting time slots that:
1. Don't overlap with existing meetings
2. Are during business hours (9 AM - 6 PM)
3. Are within the Slush dates (Nov 18-20, 2024)
4. Avoid lunch time (12:00-13:00)
5. Prefer morning slots (better for networking)

Return as JSON:
{
  "suggestions": [
    {
      "startTime": "2024-11-18T10:00:00",
      "endTime": "2024-11-18T10:30:00",
      "reason": "Morning slot, no conflicts"
    }
  ]
}
`

      const response = await window.spark.llm(context, 'gpt-4o', true)
      const data = JSON.parse(response)

      if (data.suggestions && Array.isArray(data.suggestions)) {
        setSuggestions(data.suggestions.slice(0, 3))
        setHasGenerated(true)
      }
    } catch (error) {
      toast.error('Failed to generate time suggestions')
      console.error(error)
    } finally {
      setIsLoading(false)
    }
  }

  if (!hasGenerated) {
    return (
      <Button
        onClick={generateSuggestions}
        disabled={isLoading}
        variant="outline"
        size="sm"
        className="w-full gap-2"
      >
        <Sparkle size={16} weight={isLoading ? 'duotone' : 'fill'} className={isLoading ? 'animate-pulse' : ''} />
        {isLoading ? 'Finding optimal times...' : 'Suggest Meeting Times'}
      </Button>
    )
  }

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Sparkle size={16} weight="duotone" className="text-primary" />
          <span className="text-sm font-semibold">Suggested Times</span>
        </div>
        <Button
          onClick={generateSuggestions}
          disabled={isLoading}
          variant="ghost"
          size="sm"
          className="h-7 text-xs"
        >
          Refresh
        </Button>
      </div>

      <AnimatePresence>
        <div className="space-y-2">
          {suggestions.map((slot, idx) => {
            const start = new Date(slot.startTime)
            const end = new Date(slot.endTime)
            
            return (
              <motion.div
                key={idx}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: idx * 0.1 }}
              >
                <Card 
                  className="p-3 hover:bg-muted/50 transition-colors cursor-pointer"
                  onClick={() => {
                    onSelectTimeSlot(slot.startTime, slot.endTime)
                    toast.success('Time slot selected!')
                  }}
                >
                  <div className="flex items-start gap-3">
                    <Clock size={18} weight="duotone" className="text-primary flex-shrink-0 mt-0.5" />
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="font-semibold text-sm">
                          {start.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                        </span>
                        <Badge variant="secondary" className="text-[10px]">
                          {start.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })} - {end.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })}
                        </Badge>
                      </div>
                      <p className="text-xs text-muted-foreground">
                        {slot.reason}
                      </p>
                    </div>
                  </div>
                </Card>
              </motion.div>
            )
          })}
        </div>
      </AnimatePresence>
    </div>
  )
}
