import { useState, useEffect } from 'react'
import { useKV } from '@/lib/useKV'
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

// Helper function to calculate recommendation score
function calculateRecommendationScore(
  candidate: Startup,
  userVotes: { interested: Startup[], passed: Startup[] },
  swipeCount: number
): number {
  if (swipeCount < 20) return 0 // No recommendations until 20 swipes (Phase 2 starts after 20)

  const interestedTopics = new Set<string>()
  const interestedMaturity = new Map<string, number>()
  const interestedUseCases = new Set<string>()
  
  // Extract preferences from interested startups
  userVotes.interested.forEach(startup => {
    const topics = typeof startup.topics === 'string' ? startup.topics.split(',').map(t => t.trim()) : (startup.topics || [])
    topics.forEach(t => interestedTopics.add(t))
    
    if (startup.maturity) interestedMaturity.set(startup.maturity, (interestedMaturity.get(startup.maturity) || 0) + 1)
    
    const useCases = startup.axa_use_cases || startup.axaUseCases
    if (useCases) {
      try {
        const caseArray = Array.isArray(useCases) ? useCases : (typeof useCases === 'string' ? JSON.parse(useCases) : [])
        caseArray.forEach((uc: any) => {
          if (typeof uc === 'string') interestedUseCases.add(uc)
        })
      } catch {}
    }
  })

  let score = 0
  let matchCount = 0

  // Check topic match (weighted)
  const candTopics = typeof candidate.topics === 'string' ? candidate.topics.split(',').map(t => t.trim()) : (candidate.topics || [])
  const topicMatches = candTopics.filter(t => interestedTopics.has(t)).length
  if (topicMatches > 0) {
    score += topicMatches * 20
    matchCount += topicMatches
  }

  // Check maturity match (weighted)
  if (candidate.maturity && interestedMaturity.has(candidate.maturity)) {
    score += 15
    matchCount++
  }

  // Check use case match (weighted)
  const candUseCases = candidate.axa_use_cases || candidate.axaUseCases
  if (candUseCases) {
    try {
      const caseArray = Array.isArray(candUseCases) ? candUseCases : (typeof candUseCases === 'string' ? JSON.parse(candUseCases) : [])
      const ucMatches = caseArray.filter((uc: any) => typeof uc === 'string' && interestedUseCases.has(uc)).length
      if (ucMatches > 0) {
        score += ucMatches * 10
        matchCount++
      }
    } catch {}
  }

  return score
}

export function SwipeView({ startups, votes, currentUserId, currentUserName, onVote }: SwipeViewProps) {
  const isMobile = useIsMobile()
  const [currentIndex, setCurrentIndex] = useState(0)
  const [direction, setDirection] = useState<'left' | 'right' | null>(null)
  const [finnishedUsers, setFinnishedUsers] = useKV<string[]>('finnished-users', [])
  const [localVotedIds, setLocalVotedIds] = useState<Set<string>>(new Set())
  const [isProcessingSwipe, setIsProcessingSwipe] = useState(false)
  const [lockedStartup, setLockedStartup] = useState<Startup | null>(null)
  
  // Get user's votes to determine phase
  const userVotes = votes.filter(v => v.userId === currentUserId)
  const swipeCount = userVotes.length + localVotedIds.size
  
  // Determine which startups to use based on phase
  let startupPool: Startup[]
  
  if (swipeCount < 20) {
    // Phase 1: Only use Phase 1 startups (from API response, already Agentic + Other topics)
    startupPool = startups
  } else {
    // Phase 2: Use all startups (should include Tier 2, 3, 4 from Phase 2 API)
    // Include all startups since Phase 2 API returns the full pool
    startupPool = startups
  }

  // Sort by axa_overall_score (descending) - highest quality first
  const sortedByFit = [...startupPool].sort((a, b) => {
    const scoreA = (a.axa_overall_score || a.axaOverallScore || 0) as number
    const scoreB = (b.axa_overall_score || b.axaOverallScore || 0) as number
    return scoreB - scoreA
  })
  
  // Build recommendation data
  const interestedIds = new Set(userVotes.filter(v => v.interested).map(v => String(v.startupId)))
  const passedIds = new Set(userVotes.filter(v => !v.interested).map(v => String(v.startupId)))
  
  const userVotesData = {
    interested: sortedByFit.filter(s => interestedIds.has(String(s.id))),
    passed: sortedByFit.filter(s => passedIds.has(String(s.id)))
  }

  // Build the final list: First 20 sorted by funding, then recommendations with ~70% preference match + ~30% diversity
  let limitedStartups: Startup[]
  
  if (swipeCount >= 20) {
    const seenIds = new Set([...interestedIds, ...passedIds, ...localVotedIds])
    const unseen = sortedByFit.filter(s => !seenIds.has(String(s.id)))
    
    // Separate recommendations into preference-based and diverse
    const recommendations = unseen.map(s => ({
      startup: s,
      score: calculateRecommendationScore(s, userVotesData, swipeCount)
    }))
    
    // Sort by recommendation score (descending)
    recommendations.sort((a, b) => b.score - a.score)
    
    // Take top 70 preference-based matches
    const preferenceBasedCount = Math.floor(100 * 0.7)
    const preferenceBasedRecs = recommendations.slice(0, preferenceBasedCount).map(r => r.startup)
    
    // Take remaining 30 from the rest (diverse options)
    const diverseRecs = recommendations.slice(preferenceBasedCount).slice(0, 100 - preferenceBasedCount).map(r => r.startup)
    
    limitedStartups = [...preferenceBasedRecs, ...diverseRecs]
  } else {
    // Before 20 swipes (Phase 1), just show sorted by funding
    limitedStartups = sortedByFit
  }

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
      <div className="flex-1 flex flex-col min-h-0 overflow-hidden">
        {/* Recommendations Section - bounded */}
        <section className="flex-shrink-0 max-h-[120px] sm:max-h-[150px] overflow-y-auto px-4 py-2 sm:py-3 border-b border-white/10">
          <AIRecommendations
            startups={limitedStartups}
            votes={votes}
            currentUserId={currentUserId}
            onStartupClick={(id) => {
              const idx = unseenStartups.findIndex(s => s.id === id)
              if (idx >= 0) setCurrentIndex(idx)
            }}
          />
        </section>

        {/* Card Section - fills remaining space */}
        <section className="flex-1 flex items-center justify-center px-3 sm:px-4 py-2 pb-3 min-h-0">
          <div className="relative w-full max-w-[440px] h-full flex">
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
        </section>

        {/* Nav spacing reserve */}
        <div className="flex-shrink-0 h-[calc(var(--nav-height-mobile)+env(safe-area-inset-bottom)+4px)]" />
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
    </div>
  )
}


