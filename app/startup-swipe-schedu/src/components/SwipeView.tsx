import { useState, useEffect } from 'react'
import { useKV } from '@/lib/useKV'
import { useIsMobile } from '@/hooks/use-mobile'
import { SwipeableCard } from './SwipeableCard'
import { AIRecommendations } from './AIRecommendations'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { Badge } from '@/components/ui/badge'
import { Close, Heart, UsersGroup, Rocket, WandMagicSparkles } from 'flowbite-react-icons/outline'
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
            <UsersGroup className="w-5 h-5"   />
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
    <div className="w-full h-full flex flex-col lg:flex-row gap-4 p-2 sm:p-4 pb-2 max-w-[1800px] mx-auto">
      {/* Left Column - Progress, Stats & Info - Fixed Height */}
      <div className="hidden lg:flex flex-col gap-4 w-[320px] xl:w-[360px] flex-shrink-0 h-[calc(100vh-100px)] max-h-[1000px]">
        <div className="flex-1 flex flex-col gap-4 overflow-y-auto pr-2">
        {currentStartup && (
          <>
            {/* Progress Tracker */}
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md border border-gray-200 dark:border-gray-700 p-4 xl:p-6 flex-shrink-0">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-base xl:text-lg font-semibold text-gray-900 dark:text-white flex items-center gap-2">
                  <Rocket className="text-blue-600 dark:text-blue-500 w-5 h-5"  />
                  Your Progress
                </h3>
                <Badge variant="secondary" className="text-sm font-medium">
                  {swipeCount} reviewed
                </Badge>
              </div>
              <Progress value={progress} className="h-2 mb-3" />
              <div className="flex justify-between text-xs xl:text-sm">
                <span className="text-gray-600 dark:text-gray-400">
                  {limitedStartups.length - unseenStartups.length} of {limitedStartups.length}
                </span>
                <span className="text-gray-600 dark:text-gray-400">
                  {unseenStartups.length} left
                </span>
              </div>
            </div>

            {/* Team Insights */}
            {safeFinnishedUsers.length > 0 && (
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md border border-gray-200 dark:border-gray-700 p-4 xl:p-6 flex-shrink-0">
                <h3 className="text-base xl:text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
                  <UsersGroup className="text-blue-600 dark:text-blue-500 w-5 h-5"   />
                  Team Status
                </h3>
                <div className="flex items-center gap-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
                  <div className="flex-shrink-0 w-12 h-12 bg-blue-600 dark:bg-blue-500 rounded-full flex items-center justify-center">
                    <UsersGroup className="text-white w-6 h-6"   />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-900 dark:text-white">
                      {safeFinnishedUsers.length} {safeFinnishedUsers.length === 1 ? 'team member' : 'team members'}
                    </p>
                    <p className="text-xs text-gray-600 dark:text-gray-400">
                      completed all reviews
                    </p>
                  </div>
                </div>
              </div>
            )}

            {/* Swipe Phase Info */}
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md border border-gray-200 dark:border-gray-700 p-4 xl:p-6 flex-shrink-0">
              <h3 className="text-base xl:text-lg font-semibold text-gray-900 dark:text-white mb-3 flex items-center gap-2">
                <WandMagicSparkles className="text-blue-600 dark:text-blue-500 w-5 h-5"  />
                {swipeCount < 20 ? 'Phase 1: Discovery' : 'Phase 2: Personalized'}
              </h3>
              <p className="text-xs xl:text-sm text-gray-600 dark:text-gray-400 leading-relaxed">
                {swipeCount < 20 
                  ? `You're in the discovery phase. Review ${20 - swipeCount} more startups to unlock AI-powered personalized recommendations based on your interests.`
                  : 'You\'re now seeing AI-personalized recommendations! About 70% match your interests, with 30% diverse options to broaden your discovery.'}
              </p>
            </div>
          </>
        )}
        </div>
      </div>

      {/* Main Content - Swipe Card - Matching Height */}
      <div className="flex-1 flex flex-col gap-4 xl:gap-6 min-w-0 h-[calc(100vh-100px)] max-h-[1000px]">
        <div className="w-full flex-shrink-0">
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

        <div className="relative flex-1 w-full flex items-center justify-center px-2 sm:px-4 min-h-0">
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
                className="w-full h-full"
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
    </div>
  )
}


