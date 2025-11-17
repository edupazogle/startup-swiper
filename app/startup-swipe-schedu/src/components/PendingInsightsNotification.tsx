import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { Bell, Close, Lightbulb } from 'flowbite-react-icons/outline'
import { MeetingInsightDialog } from './MeetingInsightDialog'
import { InsightsAPI } from '@/lib/notificationManager'

interface PendingInsight {
  notificationId: number
  meetingId: string
  meetingTitle: string
  meetingEndTime: string
  scheduledFor: string
  sent: boolean
}

interface PendingInsightsNotificationProps {
  userId: string
  onRefresh?: () => void
}

export function PendingInsightsNotification({ userId, onRefresh }: PendingInsightsNotificationProps) {
  const [pendingInsights, setPendingInsights] = useState<PendingInsight[]>([])
  const [currentInsight, setCurrentInsight] = useState<PendingInsight | null>(null)
  const [isDialogOpen, setIsDialogOpen] = useState(false)
  const [isVisible, setIsVisible] = useState(true)

  useEffect(() => {
    loadPendingInsights()
    
    // Check for pending insights every 30 seconds
    const interval = setInterval(loadPendingInsights, 30000)
    
    return () => clearInterval(interval)
  }, [userId])

  const loadPendingInsights = async () => {
    try {
      const insights = await InsightsAPI.getPendingInsights(userId)
      setPendingInsights(insights)
      
      // If there are insights and banner is hidden, show it
      if (insights.length > 0 && !isVisible) {
        setIsVisible(true)
      }
    } catch (error) {
      console.error('Failed to load pending insights:', error)
    }
  }

  const handleShareInsight = (insight: PendingInsight) => {
    setCurrentInsight(insight)
    setIsDialogOpen(true)
  }

  const handleDismiss = async (notificationId: number) => {
    try {
      await InsightsAPI.dismissNotification(notificationId, userId)
      await loadPendingInsights()
    } catch (error) {
      console.error('Failed to dismiss notification:', error)
    }
  }

  const handleInsightSubmitted = async () => {
    await loadPendingInsights()
    onRefresh?.()
  }

  const handleHideBanner = () => {
    setIsVisible(false)
  }

  if (pendingInsights.length === 0 || !isVisible) {
    return null
  }

  const insight = pendingInsights[0] // Show first pending insight

  return (
    <>
      <Card className="fixed top-4 left-1/2 -translate-x-1/2 z-50 w-[90vw] max-w-2xl shadow-2xl border-2 border-yellow-500/50 bg-gradient-to-r from-yellow-500/10 via-orange-500/10 to-yellow-500/10 backdrop-blur-lg">
        <div className="p-4 flex items-start gap-4">
          <div className="flex-shrink-0 mt-1">
            <div className="w-10 h-10 rounded-full bg-yellow-500/20 flex items-center justify-center animate-pulse">
              <Lightbulb className="text-yellow-500 w-6 h-6"  />
            </div>
          </div>
          
          <div className="flex-1 min-w-0">
            <div className="flex items-start justify-between gap-2">
              <h3 className="font-semibold text-lg flex items-center gap-2">
                <Bell className="text-yellow-500 w-5 h-5"  />
                Share Your Insight
              </h3>
              <Button
                variant="ghost"
                size="sm"
                onClick={handleHideBanner}
                className="h-8 w-8 p-0 rounded-full"
              >
                <Close className="w-5 h-5"  />
              </Button>
            </div>
            
            <p className="text-sm text-muted-foreground mt-1">
              How was <span className="font-semibold text-foreground">{insight.meetingTitle}</span>?
            </p>
            
            {pendingInsights.length > 1 && (
              <p className="text-xs text-muted-foreground mt-1">
                +{pendingInsights.length - 1} more {pendingInsights.length === 2 ? 'meeting' : 'meetings'} waiting for insights
              </p>
            )}
            
            <div className="flex gap-2 mt-3">
              <Button
                size="sm"
                onClick={() => handleShareInsight(insight)}
                className="bg-yellow-500 hover:bg-yellow-600 text-black"
              >
                <Lightbulb className="mr-1 w-4 h-4"  />
                Share Insight
              </Button>
              
              <Button
                size="sm"
                variant="outline"
                onClick={() => handleDismiss(insight.notificationId)}
              >
                Later
              </Button>
            </div>
          </div>
        </div>
        
        {/* Progress indicator if multiple insights */}
        {pendingInsights.length > 1 && (
          <div className="px-4 pb-3">
            <div className="flex gap-1">
              {pendingInsights.slice(0, 5).map((_, index) => (
                <div
                  key={index}
                  className={`h-1 flex-1 rounded-full ${
                    index === 0 ? 'bg-yellow-500' : 'bg-gray-600'
                  }`}
                />
              ))}
              {pendingInsights.length > 5 && (
                <div className="text-xs text-muted-foreground ml-2">
                  +{pendingInsights.length - 5}
                </div>
              )}
            </div>
          </div>
        )}
      </Card>

      {currentInsight && (
        <MeetingInsightDialog
          isOpen={isDialogOpen}
          onClose={() => {
            setIsDialogOpen(false)
            setCurrentInsight(null)
          }}
          meetingId={currentInsight.meetingId}
          meetingTitle={currentInsight.meetingTitle}
          userId={userId}
          onInsightSubmitted={handleInsightSubmitted}
        />
      )}
    </>
  )
}
