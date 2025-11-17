import { useState } from 'react'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { Star, Lightbulb, Close } from 'flowbite-react-icons/outline'
import { toast } from 'sonner'
import { InsightsAPI } from '@/lib/notificationManager'

interface MeetingInsightDialogProps {
  isOpen: boolean
  onClose: () => void
  meetingId: string
  meetingTitle: string
  startupId?: string
  startupName?: string
  userId: string
  onInsightSubmitted?: () => void
}

const INSIGHT_TAGS = [
  'Product',
  'Team',
  'Market Fit',
  'Technology',
  'Business Model',
  'Traction',
  'Funding',
  'Vision',
  'Competitive Advantage',
  'Scalability'
]

export function MeetingInsightDialog({
  isOpen,
  onClose,
  meetingId,
  meetingTitle,
  startupId,
  startupName,
  userId,
  onInsightSubmitted
}: MeetingInsightDialogProps) {
  const [insight, setInsight] = useState('')
  const [selectedTags, setSelectedTags] = useState<string[]>([])
  const [rating, setRating] = useState<number>(0)
  const [followUp, setFollowUp] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleTagToggle = (tag: string) => {
    setSelectedTags(prev =>
      prev.includes(tag)
        ? prev.filter(t => t !== tag)
        : [...prev, tag]
    )
  }

  const handleSubmit = async () => {
    if (!insight.trim()) {
      toast.error('Please write your insight')
      return
    }

    setIsSubmitting(true)

    try {
      await InsightsAPI.submitInsight({
        meetingId,
        userId,
        startupId,
        startupName,
        insight: insight.trim(),
        tags: selectedTags,
        rating: rating > 0 ? rating : undefined,
        followUp
      })

      toast.success('✅ Insight saved! Thank you for sharing.')
      
      // Reset form
      setInsight('')
      setSelectedTags([])
      setRating(0)
      setFollowUp(false)

      // Notify parent
      onInsightSubmitted?.()
      
      // Close dialog
      onClose()

    } catch (error) {
      console.error('Failed to submit insight:', error)
      toast.error('Failed to save insight. Please try again.')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[600px] max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Lightbulb className="text-yellow-500 w-6 h-6"  />
            Share Your Insight
          </DialogTitle>
          <DialogDescription>
            What did you learn from <span className="font-semibold">{meetingTitle}</span>?
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6 py-4">
          {/* Insight Text */}
          <div className="space-y-2">
            <Label htmlFor="insight">
              Your Key Insight <span className="text-red-500">*</span>
            </Label>
            <Textarea
              id="insight"
              placeholder="Share one key insight, learning, or takeaway from this meeting..."
              value={insight}
              onChange={(e) => setInsight(e.target.value)}
              rows={4}
              className="resize-none"
            />
            <p className="text-xs text-muted-foreground">
              {insight.length}/500 characters
            </p>
          </div>

          {/* Rating */}
          <div className="space-y-2">
            <Label>How valuable was this meeting?</Label>
            <div className="flex items-center gap-2">
              {[1, 2, 3, 4, 5].map((star) => (
                <button
                  key={star}
                  onClick={() => setRating(star)}
                  className="transition-transform hover:scale-110 focus:outline-none focus:ring-2 focus:ring-primary rounded"
                >
                  <Star
                    className={star <= rating ? 'text-yellow-500' : 'text-gray-400'}
                    />
                </button>
              ))}
              {rating > 0 && (
                <button
                  onClick={() => setRating(0)}
                  className="ml-2 text-muted-foreground hover:text-foreground"
                >
                  <Close className="w-5 h-5"  />
                </button>
              )}
            </div>
          </div>

          {/* Tags */}
          <div className="space-y-2">
            <Label>Related Topics (optional)</Label>
            <div className="flex flex-wrap gap-2">
              {INSIGHT_TAGS.map((tag) => (
                <Badge
                  key={tag}
                  variant={selectedTags.includes(tag) ? 'default' : 'outline'}
                  className="cursor-pointer hover:bg-primary/80 transition-colors"
                  onClick={() => handleTagToggle(tag)}
                >
                  {tag}
                </Badge>
              ))}
            </div>
          </div>

          {/* Follow-up */}
          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="followUp"
              checked={followUp}
              onChange={(e) => setFollowUp(e.target.checked)}
              className="w-4 h-4 rounded border-gray-300"
            />
            <Label htmlFor="followUp" className="cursor-pointer">
              I want to follow up with this startup
            </Label>
          </div>
        </div>

        {/* Actions */}
        <div className="flex justify-end gap-3">
          <Button variant="outline" onClick={onClose} disabled={isSubmitting} size="default">
            Cancel
          </Button>
          <Button onClick={handleSubmit} disabled={isSubmitting || !insight.trim()} size="default">
            {isSubmitting ? 'Saving...' : 'Save Insight'}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  )
}
