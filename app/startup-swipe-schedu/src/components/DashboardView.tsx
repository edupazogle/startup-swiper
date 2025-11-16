import { useMemo, useState, useEffect } from 'react'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { Button } from '@/components/ui/button'
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Separator } from '@/components/ui/separator'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { AITimeSlotSuggester } from '@/components/AITimeSlotSuggester'
import { FeedbackChatModal } from '@/components/FeedbackChatModal'
import { MeetingAIModal } from '@/components/MeetingAIModal'
import { StartupFiltersPanel } from '@/components/StartupFiltersPanel'
import { Startup, Vote, CalendarEvent } from '@/lib/types'
import { Users, Heart, CalendarBlank, Check, Rocket, MapPin, CurrencyDollar, GlobeHemisphereWest, Calendar, TrendUp, MagnifyingGlass, X, Target, CheckCircle, Star, Sparkle, Briefcase } from '@phosphor-icons/react'
import { toast } from 'sonner'
import { useKV } from '@github/spark/hooks'
import { getTopicColor, getTechColor, getMaturityColor, getLocationColor } from '@/lib/badgeColors'
import { cn, parseArray } from '@/lib/utils'
import { api } from '@/lib/api'
import { fetchAllTopics } from '@/lib/topicsUseCases'

interface DashboardViewProps {
  startups: Startup[]
  votes: Vote[]
  events: CalendarEvent[]
  currentUserId: string
  onScheduleMeeting: (startupId: string, eventData: Omit<CalendarEvent, 'id' | 'attendees' | 'startupId' | 'startupName'>) => void
}

interface StartupWithVotes extends Startup {
  interestedVotes: Vote[]
  passedVotes: Vote[]
  scheduledEvent?: CalendarEvent
  averageRating?: number
  totalRatings?: number
}

interface TopicHierarchy {
  id: number
  name: string
  use_cases: UseCase[]
}

interface UseCase {
  id: number
  name: string
}

export function DashboardView({ startups, votes, events, currentUserId, onScheduleMeeting }: DashboardViewProps) {
  const [selectedStartup, setSelectedStartup] = useState<StartupWithVotes | null>(null)
  const [isScheduleDialogOpen, setIsScheduleDialogOpen] = useState(false)
  const [showInsightsAI, setShowInsightsAI] = useState(false)
  const [showMeetingAI, setShowMeetingAI] = useState(false)
  const [searchQuery, setSearchQuery] = useState<string>('')
  const [sortBy, setSortBy] = useState<'votes' | 'funding' | 'grade'>('votes')
  const [selectedStages, setSelectedStages] = useState<Set<string>>(new Set())
  const [selectedTopics, setSelectedTopics] = useState<Set<string>>(new Set())
  const [selectedTechs, setSelectedTechs] = useState<Set<string>>(new Set())
  const [selectedUseCases, setSelectedUseCases] = useState<Set<string>>(new Set())
  const [selectedGrades, setSelectedGrades] = useState<Set<string>>(new Set())
  const [topicHierarchy, setTopicHierarchy] = useState<TopicHierarchy[]>([])
  const [localVotes, setLocalVotes] = useState<Vote[]>(votes)
  const [formData, setFormData] = useState({
    startTime: '',
    endTime: '',
    location: '',
    description: ''
  })
  const [startupRatings, setStartupRatings] = useKV<Record<string, Record<string, number>>>('startup-ratings', {})

  // Fetch topic hierarchy on mount
  useEffect(() => {
    const fetchTopicHierarchy = async () => {
      try {
        const response = await fetchAllTopics()
        setTopicHierarchy(response.topics || [])
      } catch (error) {
        console.error('Failed to fetch topic hierarchy:', error)
      }
    }
    fetchTopicHierarchy()
  }, [])

  // Clear use cases when topic is deselected
  useEffect(() => {
    if (selectedTopics.size === 0) {
      setSelectedUseCases(new Set())
    }
  }, [selectedTopics])

  // Extract unique stages, topics, and techs for filters
  const uniqueStages = useMemo(() => {
    const stages = new Set<string>()
    startups.forEach(s => {
      const stage = s.Stage || s.currentInvestmentStage || s.maturity
      if (stage && String(stage).trim()) stages.add(String(stage).trim())
    })
    return Array.from(stages).sort()
  }, [startups])

  const uniqueTopics = useMemo(() => {
    const topics = new Set<string>()
    startups.forEach(s => {
      const topicArray = parseArray(s.topics)
      if (Array.isArray(topicArray)) {
        topicArray.forEach(t => {
          if (t && String(t).trim()) topics.add(String(t).trim())
        })
      }
    })
    return Array.from(topics).sort()
  }, [startups])

  const uniqueTechs = useMemo(() => {
    const techs = new Set<string>()
    startups.forEach(s => {
      const techArray = parseArray(s.tech)
      if (Array.isArray(techArray)) {
        techArray.forEach(t => {
          if (t && String(t).trim()) techs.add(String(t).trim())
        })
      }
    })
    return Array.from(techs).sort()
  }, [startups])

  const parseFunding = (funding: string | number | undefined): number => {
    if (!funding) return 0
    if (typeof funding === 'number') return funding
    const match = String(funding).match(/\d+\.?\d*/);
    return match ? parseFloat(match[0]) : 0
  }

  const startupsWithVotes = useMemo(() => {
    let filtered = startups

    // Apply search filter
    if (searchQuery.trim().length >= 3) {
      const query = searchQuery.toLowerCase().trim()
      filtered = filtered.filter(s => {
        const name = (s.name || s["Company Name"] || '').toLowerCase()
        return name.includes(query)
      })
    }

    // Apply stage filter
    if (selectedStages.size > 0) {
      filtered = filtered.filter(s => {
        const stage = s.Stage || s.currentInvestmentStage || s.maturity
        return stage && selectedStages.has(stage)
      })
    }

    // Apply topics filter
    if (selectedTopics.size > 0) {
      filtered = filtered.filter(s => {
        const topicArray = parseArray(s.topics)
        return topicArray.some(t => selectedTopics.has(t))
      })
    }

    // Apply tech filter
    if (selectedTechs.size > 0) {
      filtered = filtered.filter(s => {
        const techArray = parseArray(s.tech)
        return techArray.some(t => selectedTechs.has(t))
      })
    }

    // Apply use cases filter (only if a topic is selected)
    if (selectedUseCases.size > 0 && selectedTopics.size > 0) {
      filtered = filtered.filter(s => {
        const useCasesArray = parseArray(s.axa_use_cases)
        return useCasesArray.some(u => selectedUseCases.has(u))
      })
    }

    // Apply grade filter
    if (selectedGrades.size > 0) {
      filtered = filtered.filter(s => {
        const grade = s.axa_grade || s.axaGrade
        return grade && selectedGrades.has(grade)
      })
    }

    const result: StartupWithVotes[] = filtered.map(startup => {
      const scheduledEvent = (events || []).find(e => e.startupId === startup.id && e.confirmed)
      const ratings = startupRatings?.[startup.id] || {}
      const ratingValues = Object.values(ratings).filter(r => r > 0)
      const averageRating = ratingValues.length > 0 
        ? ratingValues.reduce((sum, rating) => sum + rating, 0) / ratingValues.length 
        : 0
      
      return {
        ...startup,
        interestedVotes: localVotes.filter(v => String(v.startupId) === String(startup.id) && v.interested),
        passedVotes: localVotes.filter(v => String(v.startupId) === String(startup.id) && !v.interested),
        scheduledEvent,
        averageRating,
        totalRatings: ratingValues.length
      }
    })

    // Sort based on sortBy setting
    let sorted: StartupWithVotes[]
    if (sortBy === 'funding') {
      sorted = result.sort((a, b) => {
        const fundingA = parseFunding(a.totalFunding || a["Funding"])
        const fundingB = parseFunding(b.totalFunding || b["Funding"])
        return fundingB - fundingA // Descending order
      })
    } else if (sortBy === 'grade') {
      const gradeOrder = { 'A+': 7, 'A': 6, 'B+': 5, 'B': 4, 'C+': 3, 'C': 2, 'F': 1 }
      sorted = result.sort((a, b) => {
        const gradeA = gradeOrder[(a.axa_grade || a.axaGrade) as keyof typeof gradeOrder] || 0
        const gradeB = gradeOrder[(b.axa_grade || b.axaGrade) as keyof typeof gradeOrder] || 0
        return gradeB - gradeA // Descending order (A+ first)
      })
    } else {
      // Sort by interested votes
      sorted = result.sort((a, b) => b.interestedVotes.length - a.interestedVotes.length)
    }
    
    // Limit to 100 startups if no search query
    if (searchQuery.trim().length < 3 && selectedStages.size === 0 && selectedTopics.size === 0 && selectedTechs.size === 0) {
      return sorted.slice(0, 100)
    }
    
    return sorted
  }, [startups, localVotes, events, searchQuery, startupRatings, sortBy, selectedStages, selectedTopics, selectedTechs, selectedUseCases])

  const highPriority = startupsWithVotes.filter(s => s.interestedVotes.length >= 3)
  const mediumPriority = startupsWithVotes.filter(s => s.interestedVotes.length > 0 && s.interestedVotes.length < 3)
  const noPriority = startupsWithVotes.filter(s => s.interestedVotes.length === 0)

  const getInitials = (name: string) => {
    return name
      .split(' ')
      .map(n => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2)
  }

  const handleRating = (startupId: string, rating: number) => {
    setStartupRatings((current) => {
      const updated = { ...(current || {}) }
      if (!updated[startupId]) {
        updated[startupId] = {}
      }
      updated[startupId][currentUserId] = rating
      return updated
    })
    toast.success(`Rated ${rating} rocket${rating !== 1 ? 's' : ''}!`)
  }

  const RocketRating = ({ startupId, currentRating, averageRating, totalRatings }: { 
    startupId: string
    currentRating: number
    averageRating: number
    totalRatings: number 
  }) => {
    const [hoveredRating, setHoveredRating] = useState(0)
    
    return (
      <div className="flex flex-col gap-1.5">
        <div className="flex items-center gap-1">
          {[1, 2, 3, 4, 5].map((rating) => {
            const isActive = hoveredRating > 0 ? rating <= hoveredRating : rating <= currentRating
            return (
              <button
                key={rating}
                onClick={() => handleRating(startupId, rating)}
                onMouseEnter={() => setHoveredRating(rating)}
                onMouseLeave={() => setHoveredRating(0)}
                className="transition-all hover:scale-110 active:scale-95 cursor-pointer"
                aria-label={`Rate ${rating} rockets`}
              >
                <Rocket 
                  size={18}
                  weight={isActive ? 'fill' : 'regular'}
                  className={`${
                    isActive 
                      ? 'text-primary' 
                      : 'text-muted-foreground/30'
                  } transition-colors md:w-5 md:h-5`}
                />
              </button>
            )
          })}
        </div>
        {totalRatings > 0 && (
          <div className="flex items-center gap-1.5 text-[10px] md:text-xs text-muted-foreground">
            <span className="font-semibold text-primary">{averageRating.toFixed(1)}</span>
            <span>avg ({totalRatings} rating{totalRatings !== 1 ? 's' : ''})</span>
          </div>
        )}
      </div>
    )
  }

  const handleHeartToggle = async (startup: StartupWithVotes) => {
    const voteExists = localVotes.some(v => String(v.startupId) === String(startup.id) && v.userId === currentUserId && v.interested)
    
    try {
      if (voteExists) {
        // Remove vote optimistically from UI first
        setLocalVotes(prev => prev.filter(v => !(String(v.startupId) === String(startup.id) && v.userId === currentUserId)))
        
        // Then remove from database
        try {
          await api.deleteVote(String(startup.id), currentUserId)
          toast.success('Removed from favorites')
        } catch (deleteError) {
          // If delete fails, restore the vote in UI
          console.error('Delete failed:', deleteError)
          setLocalVotes(prev => [...prev, {
            startupId: String(startup.id),
            userId: currentUserId,
            userName: 'User',
            interested: true,
            timestamp: new Date().toISOString(),
          }])
          toast.error('Failed to remove vote')
        }
      } else {
        // Add vote optimistically to UI first
        const newVote = {
          startupId: String(startup.id),
          userId: currentUserId,
          userName: 'User',
          interested: true,
          timestamp: new Date().toISOString(),
        }
        setLocalVotes(prev => [...prev, newVote])
        
        // Then add to database
        try {
          await api.createVote(newVote)
          toast.success('Added to favorites')
        } catch (createError) {
          // If create fails, remove from UI
          console.error('Create failed:', createError)
          setLocalVotes(prev => prev.filter(v => !(String(v.startupId) === String(startup.id) && v.userId === currentUserId)))
          toast.error('Failed to add vote')
        }
      }
    } catch (error) {
      console.error('Error toggling vote:', error)
      toast.error('Failed to update favorite status')
    }
  }

  const renderStartupCard = (startup: StartupWithVotes) => {
    const userRating = startupRatings?.[startup.id]?.[currentUserId] || 0
    const displayName = startup.name || startup["Company Name"] || 'Unknown Startup'
    const displayUSP = startup.shortDescription || startup["USP"] || ''
    const displayLogo = startup.logoUrl || startup.logo
    const displayWebsite = startup.website || startup["URL"]
    const displayLocation = startup.billingCity && startup.billingCountry 
      ? `${startup.billingCity}, ${startup.billingCountry}` 
      : (startup.billingCountry || startup["Headquarter Country"] || 'Unknown')
    const displayFunding = startup.totalFunding 
      ? `$${startup.totalFunding}M` 
      : (startup["Funding"] || 'Undisclosed')
    const displayEmployees = startup.employees || 'Undisclosed'
    const displayStage = startup.Stage || startup.currentInvestmentStage || startup.maturity || 'Unknown'
    
    return (
      <Card key={startup.id} className="p-4 md:p-6 hover:shadow-md transition-shadow">
        <div className="flex flex-col sm:flex-row items-start gap-3 md:gap-4">
          {displayLogo && (
            <div className="w-16 h-16 md:w-20 md:h-20 rounded-lg bg-background flex items-center justify-center overflow-hidden flex-shrink-0 border border-border/50 shadow-sm">
              <img src={displayLogo} alt={displayName} className="w-full h-full object-contain p-1" />
            </div>
          )}
          
          <div className="flex-1 min-w-0 w-full">
            <div className="flex flex-col sm:flex-row items-start sm:justify-between gap-2 sm:gap-3 md:gap-4 mb-2">
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1.5">
                  <h3 className="text-lg md:text-xl font-semibold leading-tight tracking-tight">{displayName}</h3>
                </div>
                <div className="flex flex-wrap gap-x-2 md:gap-x-3 gap-y-1.5 md:gap-y-2 mb-2">
                  {(() => {
                    const topicArray = parseArray(startup.topics)
                    return Array.isArray(topicArray) && topicArray.length > 0 && (
                      <div className="flex flex-col gap-0.5">
                        <span className="text-[9px] md:text-[10px] text-muted-foreground uppercase tracking-wider font-medium">Topics</span>
                        <div className="flex flex-wrap gap-1">
                          {topicArray.slice(0, 2).map((topic, i) => {
                            const colors = getTopicColor(topic)
                            return (
                              <Badge 
                                key={i} 
                                variant="outline" 
                                className={cn("text-[10px] md:text-xs font-medium border", colors.bg, colors.text, colors.border)}
                              >
                                {topic}
                              </Badge>
                            )
                          })}
                        </div>
                      </div>
                    )
                  })()}
                  {startup.maturity && (
                    <div className="flex flex-col gap-0.5">
                      <span className="text-[9px] md:text-[10px] text-muted-foreground uppercase tracking-wider font-medium">Maturity</span>
                      {(() => {
                        const colors = getMaturityColor(startup.maturity)
                        return (
                          <Badge 
                            variant="outline" 
                            className={cn("text-[10px] md:text-xs font-medium border", colors.bg, colors.text, colors.border)}
                          >
                            {startup.maturity}
                          </Badge>
                        )
                      })()}
                    </div>
                  )}

                  {startup.scheduledEvent && (
                    <div className="flex flex-col gap-0.5">
                      <span className="text-[9px] md:text-[10px] text-transparent uppercase tracking-wider font-medium select-none">_</span>
                      <Badge variant="default" className="text-[10px] md:text-xs gap-0.5 md:gap-1">
                        <Check size={10} className="md:w-3 md:h-3" weight="bold" />
                        Scheduled
                      </Badge>
                    </div>
                  )}
                </div>
              </div>
              
              <div className="flex flex-wrap items-center gap-2 flex-shrink-0">
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => {
                    setSelectedStartup(startup)
                    setShowInsightsAI(true)
                  }}
                  className="text-xs"
                >
                  💡 Insights AI
                </Button>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => {
                    setSelectedStartup(startup)
                    setShowMeetingAI(true)
                  }}
                  className="text-xs"
                >
                  💼 Meeting AI
                </Button>
              </div>
            </div>

            {/* Venture Clienting Analysis */}
            {(startup.axa_overall_score !== undefined || startup.axaOverallScore !== undefined) && (
              <div className="mb-4">
                <div className="flex items-center gap-2 mb-3">
                  <Target size={16} className="text-blue-600 dark:text-blue-400" weight="duotone" />
                  <h3 className="text-xs text-muted-foreground uppercase tracking-wide font-medium">Venture Clienting Analysis</h3>
                </div>
                
                <div className="grid grid-cols-2 gap-3 bg-blue-500/5 p-3 rounded-lg border border-blue-200 dark:border-blue-900/30">
                  {/* Left Column: Score & Provider Status */}
                  <div className="space-y-3">
                    {/* Grade Section */}
                    <div>
                      <p className="text-xs text-muted-foreground uppercase tracking-wide font-medium mb-1">AXA Grade</p>
                      <div className="flex items-end gap-2">
                        <span className={cn(
                          'text-2xl md:text-3xl font-bold',
                          startup.axa_grade === 'A+' || startup.axaGrade === 'A+' ? 'text-yellow-500 dark:text-yellow-400' :
                          startup.axa_grade === 'A' || startup.axaGrade === 'A' ? 'text-emerald-600 dark:text-emerald-400' :
                          startup.axa_grade === 'B+' || startup.axaGrade === 'B+' ? 'text-cyan-600 dark:text-cyan-400' :
                          startup.axa_grade === 'B' || startup.axaGrade === 'B' ? 'text-blue-600 dark:text-blue-400' :
                          startup.axa_grade === 'C+' || startup.axaGrade === 'C+' ? 'text-amber-600 dark:text-amber-400' :
                          startup.axa_grade === 'C' || startup.axaGrade === 'C' ? 'text-orange-600 dark:text-orange-400' :
                          'text-slate-400 dark:text-slate-600'
                        )}>
                          {startup.axa_grade || startup.axaGrade || 'N/A'}
                        </span>
                      </div>
                    </div>

                    {/* Grade Explanation */}
                    {(startup.axa_grade !== undefined || startup.axaGrade !== undefined) && (
                      <div className="flex items-start gap-2">
                        <Sparkle 
                          size={14} 
                          weight="fill"
                          className={cn(
                            'flex-shrink-0 mt-0.5',
                            startup.axa_grade === 'A+' || startup.axaGrade === 'A+' ? 'text-yellow-500 dark:text-yellow-400' :
                            startup.axa_grade === 'A' || startup.axaGrade === 'A' ? 'text-emerald-600 dark:text-emerald-400' :
                            startup.axa_grade === 'B+' || startup.axaGrade === 'B+' ? 'text-cyan-600 dark:text-cyan-400' :
                            startup.axa_grade === 'B' || startup.axaGrade === 'B' ? 'text-blue-600 dark:text-blue-400' :
                            startup.axa_grade === 'C+' || startup.axaGrade === 'C+' ? 'text-amber-600 dark:text-amber-400' :
                            startup.axa_grade === 'C' || startup.axaGrade === 'C' ? 'text-orange-600 dark:text-orange-400' :
                            'text-slate-400 dark:text-slate-600'
                          )} 
                        />
                        <span className="text-xs text-muted-foreground leading-snug">
                          {startup.axa_grade_explanation || startup.axaGradeExplanation || 'Assessment pending'}
                        </span>
                      </div>
                    )}
                  </div>

                  {/* Right Column: Use Cases */}
                  {(() => {
                    const useCases = startup.axa_use_cases || startup.axaUseCases
                    const useCaseArray = parseArray(useCases)

                    return useCaseArray.length > 0 && (
                      <div className="pt-2">
                        <p className="text-[9px] md:text-[10px] text-muted-foreground uppercase tracking-wide font-medium mb-1">Use Cases</p>
                        <div className="flex flex-wrap gap-1">
                          {useCaseArray.map((useCase: string, idx: number) => (
                            <div key={idx} className="flex items-center gap-1 bg-green-500/90 px-1.5 py-0.5 rounded border border-green-600/80">
                              <CheckCircle size={9} weight="bold" className="text-white flex-shrink-0" />
                              <span className="text-[9px] md:text-[10px] text-white font-medium">
                                {useCase}
                              </span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )
                  })()}
                </div>
              </div>
            )}

            {/* Value Proposition */}
            {(startup.value_proposition || startup.shortDescription) && (
              <div className="mb-4">
                <div className="flex items-center gap-2 mb-2">
                  <Star size={16} className="text-pink-600 dark:text-pink-400" weight="duotone" />
                  <h3 className="text-xs text-pink-700 dark:text-pink-300 uppercase tracking-wide font-medium">Value Proposition</h3>
                </div>
                <div className="text-sm leading-relaxed text-foreground bg-pink-500/5 p-3 rounded-lg border border-pink-200 dark:border-pink-900/30">
                  <p>{startup.value_proposition || startup.shortDescription}</p>
                </div>
              </div>
            )}

            {displayUSP && (
              <>
                <Separator className="mb-3 md:mb-4" />
              </>
            )}

            <div className="grid grid-cols-2 md:grid-cols-4 gap-2 md:gap-3 mb-3 md:mb-4">
              <div className="flex items-start gap-1.5 md:gap-2">
                <MapPin size={14} className="text-muted-foreground mt-0.5 flex-shrink-0 md:w-4 md:h-4" weight="duotone" />
                <div className="min-w-0 flex-1">
                  <p className="text-[10px] md:text-xs text-muted-foreground uppercase tracking-wide mb-0.5">Location</p>
                  <Badge 
                    variant="outline" 
                    className={cn("text-[10px] md:text-xs font-medium border h-auto py-0.5", getLocationColor(displayLocation).bg, getLocationColor(displayLocation).text, getLocationColor(displayLocation).border)}
                  >
                    {displayLocation}
                  </Badge>
                </div>
              </div>
              
              <div className="flex items-start gap-1.5 md:gap-2">
                <Users size={14} className="text-muted-foreground mt-0.5 flex-shrink-0 md:w-4 md:h-4" weight="duotone" />
                <div>
                  <p className="text-[10px] md:text-xs text-muted-foreground uppercase tracking-wide mb-0.5">Team Size</p>
                  <p className="text-xs md:text-sm font-medium">{displayEmployees}</p>
                </div>
              </div>

              <div className="flex items-start gap-1.5 md:gap-2">
                <CurrencyDollar size={14} className="text-muted-foreground mt-0.5 flex-shrink-0 md:w-4 md:h-4" weight="duotone" />
                <div>
                  <p className="text-[10px] md:text-xs text-muted-foreground uppercase tracking-wide mb-0.5">Funding</p>
                  <p className="text-xs md:text-sm font-medium">{displayFunding}</p>
                </div>
              </div>

              <div className="flex items-start gap-1.5 md:gap-2">
                <TrendUp size={14} className="text-muted-foreground mt-0.5 flex-shrink-0 md:w-4 md:h-4" weight="duotone" />
                <div>
                  <p className="text-[10px] md:text-xs text-muted-foreground uppercase tracking-wide mb-0.5">Stage</p>
                  <p className="text-xs md:text-sm font-medium">{displayStage}</p>
                </div>
              </div>

              {startup.dateFounded && (
                <div className="flex items-start gap-1.5 md:gap-2">
                  <Calendar size={14} className="text-muted-foreground mt-0.5 flex-shrink-0 md:w-4 md:h-4" weight="duotone" />
                  <div>
                    <p className="text-[10px] md:text-xs text-muted-foreground uppercase tracking-wide mb-0.5">Founded</p>
                    <p className="text-xs md:text-sm font-medium">{new Date(startup.dateFounded).getFullYear()}</p>
                  </div>
                </div>
              )}

              {displayWebsite && (
                <div className="flex items-start gap-1.5 md:gap-2 md:col-span-3">
                  <GlobeHemisphereWest size={14} className="text-muted-foreground mt-0.5 flex-shrink-0 md:w-4 md:h-4" weight="duotone" />
                  <div className="min-w-0 flex-1">
                    <p className="text-[10px] md:text-xs text-muted-foreground uppercase tracking-wide mb-0.5">Website</p>
                    <a 
                      href={displayWebsite.startsWith('http') ? displayWebsite : `https://${displayWebsite}`} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="text-xs md:text-sm font-medium text-accent hover:underline break-all"
                      onClick={(e) => e.stopPropagation()}
                    >
                      {displayWebsite.replace(/^https?:\/\//, '').replace(/^www\./, '')}
                    </a>
                  </div>
                </div>
              )}
            </div>

            {startup.interestedVotes.length > 0 && (
              <div className="flex items-center gap-1.5 md:gap-2">
                <Users size={14} className="text-muted-foreground md:w-4 md:h-4" />
                <div className="flex -space-x-1.5 md:-space-x-2">
                  {startup.interestedVotes.map((vote, idx) => (
                    <Avatar key={idx} className="w-6 h-6 md:w-8 md:h-8 border-2 border-background">
                      <AvatarFallback className="bg-primary text-primary-foreground text-[10px] md:text-xs">
                        {getInitials(vote.userName)}
                      </AvatarFallback>
                    </Avatar>
                  ))}
                </div>
                <span className="text-[10px] md:text-xs text-muted-foreground ml-0.5 md:ml-1 hidden md:inline">
                  {startup.interestedVotes.map(v => v.userName).join(', ')}
                </span>
              </div>
            )}

            {/* Bottom Action Bar with Heart and Rocket */}
            <div className="flex items-center justify-end gap-2 mt-4 pt-4 border-t">
              <button
                onClick={(e) => {
                  e.stopPropagation()
                  handleHeartToggle(startup)
                }}
                className="flex items-center gap-1.5 px-3 py-2 rounded-lg bg-white/90 backdrop-blur-sm shadow-sm hover:shadow-md transition-all duration-200 group hover:scale-105 active:scale-95 flex-shrink-0"
                title={localVotes.some(v => String(v.startupId) === String(startup.id) && v.userId === currentUserId && v.interested) ? 'Unlike this startup' : 'Like this startup'}
              >
                <Heart 
                  size={16} 
                  weight={localVotes.some(v => String(v.startupId) === String(startup.id) && v.userId === currentUserId && v.interested) ? "fill" : "regular"}
                  className={cn(
                    "transition-all duration-200",
                    localVotes.some(v => String(v.startupId) === String(startup.id) && v.userId === currentUserId && v.interested) ? "text-pink-500" : "text-gray-400 group-hover:text-pink-400"
                  )}
                />
                <span className="font-semibold text-sm">
                  {localVotes.filter(v => String(v.startupId) === String(startup.id) && v.interested).length}
                </span>
              </button>

              <RocketRating 
                startupId={String(startup.id)}
                currentRating={userRating}
                averageRating={startup.averageRating || 0}
                totalRatings={startup.totalRatings || 0}
              />
            </div>
          </div>
        </div>
      </Card>
    )
  }

  return (
    <>
      <div className="h-full">
        <div className="max-w-7xl mx-auto p-3 md:p-6 space-y-4 md:space-y-6">
          {/* New Responsive Filters Panel */}
          <StartupFiltersPanel
            searchQuery={searchQuery}
            onSearchChange={setSearchQuery}
            sortBy={sortBy}
            onSortChange={(value) => setSortBy(value as 'votes' | 'funding' | 'grade')}
            selectedStages={selectedStages}
            onStageChange={(stage, selected) => {
              const newStages = new Set(selectedStages)
              if (selected) newStages.add(stage)
              else newStages.delete(stage)
              setSelectedStages(newStages)
            }}
            selectedTopics={selectedTopics}
            onTopicChange={(topic, selected) => {
              const newTopics = new Set(selectedTopics)
              if (selected) newTopics.add(topic)
              else newTopics.delete(topic)
              setSelectedTopics(newTopics)
            }}
            selectedTechs={selectedTechs}
            onTechChange={(tech, selected) => {
              const newTechs = new Set(selectedTechs)
              if (selected) newTechs.add(tech)
              else newTechs.delete(tech)
              setSelectedTechs(newTechs)
            }}
            selectedUseCases={selectedUseCases}
            onUseCaseChange={(useCase, selected) => {
              const newUseCases = new Set(selectedUseCases)
              if (selected) newUseCases.add(useCase)
              else newUseCases.delete(useCase)
              setSelectedUseCases(newUseCases)
            }}
            selectedGrades={selectedGrades}
            onGradeChange={(grade, selected) => {
              const newGrades = new Set(selectedGrades)
              if (selected) newGrades.add(grade)
              else newGrades.delete(grade)
              setSelectedGrades(newGrades)
            }}
            availableStages={uniqueStages}
            availableTopics={uniqueTopics}
            availableTechs={uniqueTechs}
            availableUseCases={topicHierarchy.find(t => t.name === Array.from(selectedTopics)[0])?.use_cases.map(uc => uc.name) || []}
          />
          {highPriority.length > 0 && (
            <div>
              <div className="flex items-center gap-2 md:gap-3 mb-3 md:mb-4">
                <div className="w-1 h-6 md:h-8 bg-accent rounded-full" />
                <div>
                  <h2 className="text-xl md:text-2xl font-semibold">High Priority</h2>
                  <p className="text-xs md:text-sm text-muted-foreground">3+ team members interested</p>
                </div>
              </div>
              <div className="space-y-3 md:space-y-4">
                {highPriority.map(renderStartupCard)}
              </div>
            </div>
          )}

          {mediumPriority.length > 0 && (
            <div>
              <div className="flex items-center gap-2 md:gap-3 mb-3 md:mb-4">
                <div className="w-1 h-6 md:h-8 bg-primary rounded-full" />
                <div>
                  <h2 className="text-xl md:text-2xl font-semibold">Medium Priority</h2>
                  <p className="text-xs md:text-sm text-muted-foreground">1-2 team members interested</p>
                </div>
              </div>
              <div className="space-y-3 md:space-y-4">
                {mediumPriority.map(renderStartupCard)}
              </div>
            </div>
          )}

          {noPriority.length > 0 && (
            <div>
              <div className="flex items-center gap-2 md:gap-3 mb-3 md:mb-4">
                <div className="w-1 h-6 md:h-8 bg-muted rounded-full" />
                <div>
                  <h2 className="text-xl md:text-2xl font-semibold">No Interest Yet</h2>
                  <p className="text-xs md:text-sm text-muted-foreground">No team members interested</p>
                </div>
              </div>
              <div className="space-y-3 md:space-y-4">
                {noPriority.map(renderStartupCard)}
              </div>
            </div>
          )}

          {startupsWithVotes.length === 0 && (
            <div className="text-center py-12 md:py-16">
              <Users size={48} className="md:w-16 md:h-16 text-muted-foreground mx-auto mb-3 md:mb-4" />
              <h2 className="text-xl md:text-2xl font-semibold mb-2">No Startups Found</h2>
              <p className="text-sm md:text-base text-muted-foreground">
                {searchQuery.trim().length >= 3
                  ? 'No startups match your search. Try a different search term.'
                  : 'Add some startups to get started with team coordination.'}
              </p>
            </div>
          )}
        </div>
      </div>

      <Dialog open={isScheduleDialogOpen} onOpenChange={setIsScheduleDialogOpen}>
        <DialogContent className="sm:max-w-[500px]">
          <DialogHeader>
            <DialogTitle>Schedule Meeting with {selectedStartup?.["Company Name"]}</DialogTitle>
            <DialogDescription>
              This will create a confirmed meeting and automatically add all interested team members.
            </DialogDescription>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            <AITimeSlotSuggester
              events={events}
              onSelectTimeSlot={(start, end) => {
                setFormData({
                  ...formData,
                  startTime: start.slice(0, 16),
                  endTime: end.slice(0, 16)
                })
              }}
            />
            <div className="grid grid-cols-2 gap-4">
              <div className="grid gap-2">
                <Label htmlFor="start">Start Time *</Label>
                <Input
                  id="start"
                  type="datetime-local"
                  value={formData.startTime}
                  onChange={(e) => setFormData({ ...formData, startTime: e.target.value })}
                />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="end">End Time *</Label>
                <Input
                  id="end"
                  type="datetime-local"
                  value={formData.endTime}
                  onChange={(e) => setFormData({ ...formData, endTime: e.target.value })}
                />
              </div>
            </div>
            <div className="grid gap-2">
              <Label htmlFor="location">Location</Label>
              <Input
                id="location"
                placeholder="Hall 3, Booth A42"
                value={formData.location}
                onChange={(e) => setFormData({ ...formData, location: e.target.value })}
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="description">Notes</Label>
              <Textarea
                id="description"
                placeholder="Add meeting notes..."
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                rows={3}
              />
            </div>
            {selectedStartup && selectedStartup.interestedVotes.length > 0 && (
              <div className="bg-muted/50 p-3 rounded-lg">
                <p className="text-sm font-medium mb-2">Attendees ({selectedStartup.interestedVotes.length})</p>
                <div className="flex flex-wrap gap-2">
                  {selectedStartup.interestedVotes.map((vote, idx) => (
                    <Badge key={idx} variant="secondary">
                      {vote.userName}
                    </Badge>
                  ))}
                </div>
              </div>
            )}
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsScheduleDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={() => {
              if (!selectedStartup || !formData.startTime || !formData.endTime) {
                toast.error('Please fill in all required fields')
                return
              }
              onScheduleMeeting(String(selectedStartup.id), {
                title: `Meeting: ${selectedStartup.name || selectedStartup["Company Name"]}`,
                description: formData.description,
                startTime: new Date(formData.startTime),
                endTime: new Date(formData.endTime),
                location: formData.location,
                type: 'meeting',
                confirmed: true
              })
              setFormData({ startTime: '', endTime: '', location: '', description: '' })
              setIsScheduleDialogOpen(false)
              setSelectedStartup(null)
              toast.success(`Meeting scheduled with ${selectedStartup["Company Name"]}!`)
            }}>Schedule Meeting</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Insights AI Modal */}
      {selectedStartup && (
        <>
          <FeedbackChatModal
            isOpen={showInsightsAI}
            onClose={() => setShowInsightsAI(false)}
            startupId={selectedStartup?.id}
            startupName={selectedStartup?.name || selectedStartup?.["Company Name"] || 'Unknown'}
            startupDescription={selectedStartup?.description || selectedStartup?.shortDescription || ''}
            userId={currentUserId}
          />

          <MeetingAIModal
            isOpen={showMeetingAI}
            onClose={() => setShowMeetingAI(false)}
            startup={selectedStartup}
            userId={currentUserId}
          />
        </>
      )}
    </>
  )
}
