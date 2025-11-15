import { useState, useEffect } from 'react'
import { useKV } from '@github/spark/hooks'
import { useIsMobile } from '@/hooks/use-mobile'
import { SwipeableCard } from './SwipeableCard'
import { AIRecommendations } from './AIRecommendations'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { Badge } from '@/components/ui/badge'
import { X, Heart, Users } from '@phosphor-icons/react'
import { Startup, Vote } from '@/lib/types'
import { motion, AnimatePresence } from 'framer-motion'

interface SwipeViewProps {
  startups: Startup[]
  votes: Vote[]
  currentUserId: string
  currentUserName: string
  onVote: (startupId: string, interested: boolean) => void
}

export function SwipeView({ startups, votes, currentUserId, currentUserName, onVote }: SwipeViewProps) {
  const isMobile = useIsMobile()
  const [currentIndex, setCurrentIndex] = useState(0)
  const [direction, setDirection] = useState<'left' | 'right' | null>(null)
  const [finnishedUsers, setFinnishedUsers] = useKV<string[]>('finnished-users', [])
  const [localVotedIds, setLocalVotedIds] = useState<Set<string>>(new Set())
  const [isProcessingSwipe, setIsProcessingSwipe] = useState(false)
  const [lockedStartup, setLockedStartup] = useState<Startup | null>(null)

  // Show all available startups
  const limitedStartups = startups

  const unseenStartups = limitedStartups.filter(
    startup => {
      const hasVote = votes.some(v => String(v.startupId) === String(startup.id) && v.userId === currentUserId)
      const hasLocalVote = localVotedIds.has(String(startup.id))
      return !hasVote && !hasLocalVote
    }
  )

  // Use locked startup during animation, otherwise use the current one from the array
  const currentStartup = lockedStartup || unseenStartups[currentIndex]
  const progress = limitedStartups.length > 0
    ? ((limitedStartups.length - unseenStartups.length) / limitedStartups.length) * 100
    : 0

  const safeFinnishedUsers = finnishedUsers ?? []

  useEffect(() => {
    if (currentIndex >= unseenStartups.length && unseenStartups.length > 0) {
      setCurrentIndex(0)
    }
  }, [unseenStartups.length, currentIndex])

  useEffect(() => {
    if (unseenStartups.length === 0 && limitedStartups.length > 0 && !safeFinnishedUsers.includes(currentUserId)) {
      setFinnishedUsers((current) => [...(current ?? []), currentUserId])
    }
  }, [unseenStartups.length, limitedStartups.length, currentUserId])

  const handleSwipe = (interested: boolean) => {
    if (!currentStartup || isProcessingSwipe) return

    // Lock the current startup to prevent it from changing during animation
    setLockedStartup(currentStartup)
    setIsProcessingSwipe(true)
    setDirection(interested ? 'right' : 'left')

    // Record the vote
    onVote(String(currentStartup.id), interested)

    // Wait for animation to complete before updating state
    setTimeout(() => {
      // Add to local voted IDs after animation
      setLocalVotedIds(prev => new Set(prev).add(String(currentStartup.id)))
      // Reset index to 0 since the array will be filtered
      setCurrentIndex(0)
      setDirection(null)
      setIsProcessingSwipe(false)
      setLockedStartup(null)
    }, 300)
  }

  if (unseenStartups.length === 0) {
    return (
      <div className="flex-1 flex items-center justify-center p-8">
        <div className="text-center max-w-md">
          <div className="text-6xl mb-6">❄️🇫🇮</div>
          <h2 className="text-2xl font-semibold mb-3">You are Finnished!</h2>
          <p className="text-muted-foreground leading-relaxed mb-6">
            You've reviewed all available startups. Check the dashboard to see team preferences and coordinate meetings.
          </p>
          <Badge variant="secondary" className="text-base px-4 py-2 gap-2">
            <Users size={20} weight="fill" />
            <span>{safeFinnishedUsers.length} {safeFinnishedUsers.length === 1 ? 'attendee has' : 'attendees have'} Finnished</span>
          </Badge>
        </div>
      </div>
    )
  }

  if (isMobile) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center gap-4 md:gap-8 p-4 pb-8">
        <div className="w-full max-w-md px-2">
          <AIRecommendations
            startups={limitedStartups}
            votes={votes}
            currentUserId={currentUserId}
            onStartupClick={(id) => {
              const idx = unseenStartups.findIndex(s => s.id === id)
              if (idx >= 0) setCurrentIndex(idx)
            }}
          />
          
          <div className="flex items-center justify-between mb-2 text-xs md:text-sm">
            <span className="text-muted-foreground">
              {limitedStartups.length - unseenStartups.length} of {limitedStartups.length}
            </span>
            <span className="text-muted-foreground">
              {unseenStartups.length} remaining
            </span>
          </div>
          <Progress value={progress} className="h-2" />
        </div>

        <div className="relative w-[min(90vw,440px)] h-[min(70vh,640px)]">
          <AnimatePresence>
            {currentStartup && (
              <motion.div
                key={currentStartup.id}
                initial={{ scale: 0.9, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                exit={{
                  x: direction === 'right' ? 500 : direction === 'left' ? -500 : 0,
                  opacity: 0,
                  rotate: direction === 'right' ? 25 : direction === 'left' ? -25 : 0,
                  transition: { duration: 0.3 }
                }}
              >
                <SwipeableCard
                  startup={currentStartup}
                  onSwipe={handleSwipe}
                  isProcessing={isProcessingSwipe}
                />
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        <div className="flex gap-4 md:gap-6 items-center">
          <Button
            size="lg"
            variant="outline"
            onClick={() => handleSwipe(false)}
            disabled={!currentStartup || isProcessingSwipe}
            className="w-14 h-14 md:w-16 md:h-16 rounded-full border-2 hover:bg-destructive/10 hover:border-destructive hover:text-destructive transition-colors"
          >
            <X size={28} weight="bold" className="md:w-8 md:h-8" />
          </Button>

          <Button
            size="lg"
            onClick={() => handleSwipe(true)}
            disabled={!currentStartup || isProcessingSwipe}
            className="w-14 h-14 md:w-16 md:h-16 rounded-full bg-pink-500/80 hover:bg-pink-500/90 text-white shadow-lg"
          >
            <Heart size={28} weight="fill" className="md:w-8 md:h-8" />
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className="flex-1 flex flex-col items-center justify-center gap-8 p-4 pb-8 max-w-[1600px] mx-auto">
      <div className="w-full max-w-md px-2">
        <AIRecommendations
          startups={limitedStartups}
          votes={votes}
          currentUserId={currentUserId}
          onStartupClick={(id) => {
            const idx = unseenStartups.findIndex(s => s.id === id)
            if (idx >= 0) setCurrentIndex(idx)
          }}
        />
        
        <div className="flex items-center justify-between mb-2 text-sm">
          <span className="text-muted-foreground">
            {limitedStartups.length - unseenStartups.length} of {limitedStartups.length}
          </span>
          <span className="text-muted-foreground">
            {unseenStartups.length} remaining
          </span>
        </div>
        <Progress value={progress} className="h-2" />
      </div>

      <div className="relative w-[440px] h-[640px]">
        <AnimatePresence>
          {currentStartup && (
            <motion.div
              key={currentStartup.id}
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{
                x: direction === 'right' ? 500 : direction === 'left' ? -500 : 0,
                opacity: 0,
                rotate: direction === 'right' ? 25 : direction === 'left' ? -25 : 0,
                transition: { duration: 0.3 }
              }}
            >
              <SwipeableCard
                startup={currentStartup}
                onSwipe={handleSwipe}
                isProcessing={isProcessingSwipe}
              />
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      <div className="flex gap-6 items-center">
        <Button
          size="lg"
          variant="outline"
          onClick={() => handleSwipe(false)}
          disabled={!currentStartup || isProcessingSwipe}
          className="w-16 h-16 rounded-full border-2 hover:bg-destructive/10 hover:border-destructive hover:text-destructive transition-colors"
        >
          <X size={32} weight="bold" />
        </Button>

        <Button
          size="lg"
          onClick={() => handleSwipe(true)}
          disabled={!currentStartup || isProcessingSwipe}
          className="w-16 h-16 rounded-full bg-pink-500/80 hover:bg-pink-500/90 text-white shadow-lg"
        >
          <Heart size={32} weight="fill" />
        </Button>
      </div>
    </div>
  )
}
