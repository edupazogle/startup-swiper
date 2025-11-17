import { useMemo, useState, useEffect, useRef, useCallback, memo } from 'react'
import { useVirtualizer } from '@tanstack/react-virtual'
import { useDebounceValue } from 'usehooks-ts'
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
import { AdvancedFilterDropdown } from '@/components/AdvancedFilterDropdown'
import { Startup, Vote, CalendarEvent } from '@/lib/types'
import { UsersGroup, Heart, Check, Rocket, MapPin, Dollar, Globe, CalendarMonth, ChartLineUp, Search, Close, CirclePlus, CheckCircle, Star, WandMagicSparkles, Briefcase, Award, Users, Building } from 'flowbite-react-icons/outline'
import { toast } from 'sonner'
// Removed @github/spark dependency
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
  onOpenInsightsModal?: (startup: Startup) => void
  onOpenMeetingModal?: (startup: Startup) => void
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

function DashboardViewComponent({ startups, votes, events, currentUserId, onScheduleMeeting, onOpenInsightsModal, onOpenMeetingModal }: DashboardViewProps) {
  const [selectedStartup, setSelectedStartup] = useState<StartupWithVotes | null>(null)
  const [isScheduleDialogOpen, setIsScheduleDialogOpen] = useState(false)
  const [searchQuery, setSearchQuery] = useState<string>('')
  const [debouncedSearch] = useDebounceValue(searchQuery, 300)
  const [sortBy, setSortBy] = useState<'votes' | 'funding' | 'grade'>('votes')
  const [isSortDropdownOpen, setIsSortDropdownOpen] = useState(false)
  const [selectedStages, setSelectedStages] = useState<Set<string>>(new Set())

  // Optimized modal handlers - call parent handlers
  const handleOpenInsightsAI = useCallback((startup: StartupWithVotes) => {
    // Immediate feedback - defer actual work
    requestAnimationFrame(() => {
      onOpenInsightsModal?.(startup)
    })
  }, [onOpenInsightsModal])

  const handleOpenMeetingAI = useCallback((startup: StartupWithVotes) => {
    // Immediate feedback - defer actual work
    requestAnimationFrame(() => {
      onOpenMeetingModal?.(startup)
    })
  }, [onOpenMeetingModal])
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
  // Replace useKV with useState + localStorage
  const [startupRatings, setStartupRatingsState] = useState<Record<string, Record<string, number>>>(() => {
    try {
      const stored = localStorage.getItem('startup-ratings')
      return stored ? JSON.parse(stored) : {}
    } catch {
      return {}
    }
  })
  
  const setStartupRatings = useCallback((value: Record<string, Record<string, number>> | ((prev: Record<string, Record<string, number>>) => Record<string, Record<string, number>>)) => {
    setStartupRatingsState(prev => {
      const newValue = typeof value === 'function' ? value(prev) : value
      try {
        localStorage.setItem('startup-ratings', JSON.stringify(newValue))
      } catch (error) {
        console.warn('Failed to save ratings to localStorage:', error)
      }
      return newValue
    })
  }, [])

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

  // Get unique use cases - filtered by selected topics if any
  const uniqueUseCases = useMemo(() => {
    const useCases = new Set<string>()
    const relevantStartups = selectedTopics.size > 0
      ? startups.filter(s => {
          const topicArray = parseArray(s.topics)
          return topicArray.some(t => selectedTopics.has(t))
        })
      : startups

    relevantStartups.forEach(s => {
      const useCaseArray = parseArray(s.axa_use_cases || s.axaUseCases)
      if (Array.isArray(useCaseArray)) {
        useCaseArray.forEach(uc => {
          if (uc && String(uc).trim()) useCases.add(String(uc).trim())
        })
      }
    })
    return Array.from(useCases).sort()
  }, [startups, selectedTopics])

  // Count startups for each filter option
  const filterCounts = useMemo(() => {
    const grades = new Map<string, number>()
    const stages = new Map<string, number>()
    const topics = new Map<string, number>()
    const techs = new Map<string, number>()
    const useCases = new Map<string, number>()

    startups.forEach(startup => {
      // Count grades
      const grade = startup.axa_grade || startup.axaGrade
      if (grade) grades.set(grade, (grades.get(grade) || 0) + 1)

      // Count stages
      const stage = startup.Stage || startup.currentInvestmentStage || startup.maturity
      if (stage) stages.set(String(stage), (stages.get(String(stage)) || 0) + 1)

      // Count topics
      const topicArray = parseArray(startup.topics)
      topicArray.forEach(topic => {
        if (topic) topics.set(topic, (topics.get(topic) || 0) + 1)
      })

      // Count technologies
      const techArray = parseArray(startup.tech)
      techArray.forEach(tech => {
        if (tech) techs.set(tech, (techs.get(tech) || 0) + 1)
      })

      // Count use cases
      const useCaseArray = parseArray(startup.axa_use_cases || startup.axaUseCases)
      useCaseArray.forEach(useCase => {
        if (useCase) useCases.set(useCase, (useCases.get(useCase) || 0) + 1)
      })
    })

    return { grades, stages, topics, techs, useCases }
  }, [startups])

  // Build filter sections for AdvancedFilterDropdown - Topics separate
  const topicsFilterSections = useMemo(() => [
    {
      id: 'topics',
      title: 'Topics',
      options: uniqueTopics.map(topic => ({
        id: topic,
        label: topic,
        count: filterCounts.topics.get(topic) || 0,
        checked: selectedTopics.has(topic)
      }))
    }
  ], [filterCounts.topics, selectedTopics, uniqueTopics])

  // Use Cases filter - only when topics are selected
  const useCasesFilterSections = useMemo(() => [
    {
      id: 'useCases',
      title: 'Use Cases',
      options: uniqueUseCases.map(useCase => ({
        id: useCase,
        label: useCase,
        count: filterCounts.useCases.get(useCase) || 0,
        checked: selectedUseCases.has(useCase)
      }))
    }
  ], [filterCounts.useCases, selectedUseCases, uniqueUseCases])

  const otherFilterSections = useMemo(() => [
    {
      id: 'grades',
      title: 'Grade',
      options: ['A+', 'A', 'B+', 'B', 'C+', 'C', 'F'].map(grade => ({
        id: grade,
        label: grade,
        count: filterCounts.grades.get(grade) || 0,
        checked: selectedGrades.has(grade)
      }))
    },
    {
      id: 'stages',
      title: 'Stage',
      options: uniqueStages.map(stage => ({
        id: stage,
        label: stage,
        count: filterCounts.stages.get(stage) || 0,
        checked: selectedStages.has(stage)
      }))
    },
    {
      id: 'technologies',
      title: 'Technologies',
      options: uniqueTechs.map(tech => ({
        id: tech,
        label: tech,
        count: filterCounts.techs.get(tech) || 0,
        checked: selectedTechs.has(tech)
      }))
    }
  ], [filterCounts, selectedGrades, selectedStages, selectedTechs, uniqueStages, uniqueTechs])

  // Handle filter changes
  const handleFilterChange = (sectionId: string, optionId: string, checked: boolean) => {
    switch (sectionId) {
      case 'grades':
        setSelectedGrades(prev => {
          const newSet = new Set(prev)
          checked ? newSet.add(optionId) : newSet.delete(optionId)
          return newSet
        })
        break
      case 'stages':
        setSelectedStages(prev => {
          const newSet = new Set(prev)
          checked ? newSet.add(optionId) : newSet.delete(optionId)
          return newSet
        })
        break
      case 'topics':
        setSelectedTopics(prev => {
          const newSet = new Set(prev)
          checked ? newSet.add(optionId) : newSet.delete(optionId)
          // Clear use cases when topics change
          if (!checked) {
            setSelectedUseCases(new Set())
          }
          return newSet
        })
        break
      case 'technologies':
        setSelectedTechs(prev => {
          const newSet = new Set(prev)
          checked ? newSet.add(optionId) : newSet.delete(optionId)
          return newSet
        })
        break
      case 'useCases':
        setSelectedUseCases(prev => {
          const newSet = new Set(prev)
          checked ? newSet.add(optionId) : newSet.delete(optionId)
          return newSet
        })
        break
    }
  }

  // Clear all filters
  const handleClearAllFilters = () => {
    setSelectedGrades(new Set())
    setSelectedStages(new Set())
    setSelectedTopics(new Set())
    setSelectedTechs(new Set())
    setSelectedUseCases(new Set())
    setSearchQuery('')
  }

  // Calculate active filter count
  const activeFilterCount = selectedGrades.size + selectedStages.size + selectedTopics.size + selectedTechs.size + selectedUseCases.size

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
    if (debouncedSearch.trim().length < 3 && selectedStages.size === 0 && selectedTopics.size === 0 && selectedTechs.size === 0) {
      return sorted.slice(0, 100)
    }
    
    return sorted
  }, [startups, localVotes, events, debouncedSearch, startupRatings, sortBy, selectedStages, selectedTopics, selectedTechs, selectedUseCases, selectedGrades])

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

  // Memoize render function for performance
  const renderStartupCard = useCallback((startup: StartupWithVotes) => {
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
      <Card key={startup.id} className="group p-3 md:p-5 hover:shadow-xl transition-all duration-300 border-2 border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 shadow-lg hover:border-gray-300 dark:hover:border-gray-600">
        <div className="flex flex-col sm:flex-row items-start gap-5 md:gap-6">
          {displayLogo && (
            <div className="w-20 h-20 md:w-28 md:h-28 rounded-xl bg-gray-50 dark:bg-gray-900 flex items-center justify-center overflow-hidden flex-shrink-0 border-2 border-gray-200 dark:border-gray-700 shadow-lg group-hover:shadow-xl transition-all">
              <img src={displayLogo} alt={displayName} className="w-full h-full object-contain p-2.5" />
            </div>
          )}
          
          <div className="flex-1 min-w-0 w-full">
            <div className="flex flex-col sm:flex-row items-start sm:justify-between gap-4 sm:gap-5 mb-4">
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-3">
                  <h3 className="text-xl md:text-2xl lg:text-3xl font-extrabold leading-tight tracking-tight text-gray-900 dark:text-white">{displayName}</h3>
                </div>
                <div className="flex flex-wrap gap-x-4 md:gap-x-5 gap-y-2.5 mb-4">
                  {(() => {
                    const topicArray = parseArray(startup.topics)
                    return Array.isArray(topicArray) && topicArray.length > 0 && (
                      <div className="flex flex-col gap-1.5">
                        <span className="text-[9px] md:text-[10px] text-gray-600 dark:text-gray-400 uppercase tracking-wider font-extrabold">Topics</span>
                        <div className="flex flex-wrap gap-1.5">
                          {topicArray.slice(0, 2).map((topic, i) => {
                            const colors = getTopicColor(topic)
                            return (
                              <Badge 
                                key={i} 
                                variant="outline" 
                                className={cn("text-[10px] md:text-xs font-semibold border-2 px-2 py-0.5", colors.bg, colors.text, colors.border)}
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
                    <div className="flex flex-col gap-1.5">
                      <span className="text-[9px] md:text-[10px] text-gray-600 dark:text-gray-400 uppercase tracking-wider font-extrabold">Maturity</span>
                      {(() => {
                        const colors = getMaturityColor(startup.maturity)
                        return (
                          <Badge 
                            variant="outline" 
                            className={cn("text-[10px] md:text-xs font-semibold border-2 px-2 py-0.5", colors.bg, colors.text, colors.border)}
                          >
                            {startup.maturity}
                          </Badge>
                        )
                      })()}
                    </div>
                  )}

                  {startup.scheduledEvent && (
                    <div className="flex flex-col gap-1.5">
                      <span className="text-[9px] md:text-[10px] text-transparent uppercase tracking-wider font-medium select-none">_</span>
                      <Badge variant="default" className="text-[10px] md:text-xs font-bold gap-1 bg-gradient-to-r from-green-500 to-emerald-600 border-none shadow-md px-2 py-0.5">
                        <Check className="w-4 h-4"  />
                        Scheduled
                      </Badge>
                    </div>
                  )}
                </div>
              </div>
              
              {/* AI Actions - Full width on mobile, side by side */}
              <div className="grid grid-cols-2 gap-2.5 w-full md:flex md:flex-wrap md:gap-3 md:w-auto">
                <Button
                  size="sm"
                  onClick={() => handleOpenInsightsAI(startup)}
                  className="gap-2 w-full md:w-auto font-bold bg-gradient-to-r from-yellow-400 to-amber-500 hover:from-yellow-500 hover:to-amber-600 text-white border-0 shadow-md hover:shadow-xl transition-all px-4 py-3 text-sm touch-manipulation"
                  style={{ touchAction: 'manipulation' }}
                >
                  <Star className="text-white w-5 h-5"  />
                  <span className="hidden sm:inline">Insights AI</span>
                  <span className="sm:hidden">Insights</span>
                </Button>
                <Button
                  size="sm"
                  onClick={() => handleOpenMeetingAI(startup)}
                  className="gap-2 w-full md:w-auto font-bold bg-gradient-to-r from-blue-500 to-indigo-600 hover:from-blue-600 hover:to-indigo-700 text-white border-0 shadow-md hover:shadow-xl transition-all px-4 py-3 text-sm touch-manipulation"
                  style={{ touchAction: 'manipulation' }}
                >
                  <CalendarMonth className="text-white w-5 h-5"  />
                  <span className="hidden sm:inline">Meeting AI</span>
                  <span className="sm:hidden">Meeting</span>
                </Button>
              </div>
            </div>

            {/* Venture Clienting Analysis */}
            {(startup.axa_overall_score !== undefined || startup.axaOverallScore !== undefined) && (
              <div className="mb-6">
                <Separator className="mb-5" />
                <div className="flex items-center gap-2 mb-3">
                  <Award className="text-blue-600 dark:text-blue-400 w-5 h-5"   />
                  <h3 className="text-xs md:text-sm font-extrabold text-blue-700 dark:text-blue-300 uppercase tracking-wider">Venture Clienting Analysis</h3>
                </div>
                
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 md:gap-4 bg-gradient-to-br from-blue-50 via-indigo-50 to-blue-50 dark:from-blue-950/40 dark:via-indigo-950/40 dark:to-blue-950/40 p-3 md:p-4 rounded-xl border-2 border-blue-300/60 dark:border-blue-700/60 shadow-lg">
                  {/* Left Column: Score & Provider Status */}
                  <div className="space-y-5">
                    {/* Grade Section */}
                    <div>
                      <p className="text-xs md:text-sm text-blue-800 dark:text-blue-200 uppercase tracking-wider font-extrabold mb-3">Rise Score</p>
                      <div className="flex items-start gap-4">
                        <span className={cn(
                          'text-4xl md:text-5xl font-black tabular-nums drop-shadow-sm leading-none',
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
                        
                        {/* Grade Explanation - Right of Grade */}
                        {(startup.axa_grade !== undefined || startup.axaGrade !== undefined) && (
                          <div className="flex-1 bg-white dark:bg-gray-800 p-3 md:p-4 rounded-xl shadow-lg border-2 border-blue-200/50 dark:border-blue-800/50">
                            <div className="flex items-start gap-2">
                              <CheckCircle
                                className={cn(
                                  'flex-shrink-0 mt-0.5 w-4 h-4',
                              startup.axa_grade === 'A+' || startup.axaGrade === 'A+' ? 'text-yellow-500 dark:text-yellow-400' :
                              startup.axa_grade === 'A' || startup.axaGrade === 'A' ? 'text-emerald-600 dark:text-emerald-400' :
                              startup.axa_grade === 'B+' || startup.axaGrade === 'B+' ? 'text-cyan-600 dark:text-cyan-400' :
                              startup.axa_grade === 'B' || startup.axaGrade === 'B' ? 'text-blue-600 dark:text-blue-400' :
                              startup.axa_grade === 'C+' || startup.axaGrade === 'C+' ? 'text-amber-600 dark:text-amber-400' :
                              startup.axa_grade === 'C' || startup.axaGrade === 'C' ? 'text-orange-600 dark:text-orange-400' :
                              'text-slate-400 dark:text-slate-600'
                            )} 
                           />
                          <span className="text-xs md:text-sm text-gray-800 dark:text-gray-200 leading-relaxed font-semibold">
                            {startup.axa_grade_explanation || startup.axaGradeExplanation || 'Assessment pending'}
                          </span>
                        </div>
                      </div>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Right Column: Use Cases */}
                  {(() => {
                    const useCases = startup.axa_use_cases || startup.axaUseCases
                    const useCaseArray = parseArray(useCases)

                    return useCaseArray.length > 0 && (
                      <div className="space-y-3">
                        <p className="text-xs md:text-sm text-blue-800 dark:text-blue-200 uppercase tracking-wider font-extrabold">Use Cases</p>
                        <div className="flex flex-wrap gap-1.5">
                          {useCaseArray.map((useCase: string, idx: number) => (
                            <div key={idx} className="flex items-center gap-1.5 bg-gradient-to-r from-green-500 to-emerald-600 px-2.5 py-1 rounded-lg border border-green-600/80 shadow-md">
                              <CheckCircle className="text-white flex-shrink-0 w-4 h-4"   />
                              <span className="text-[10px] md:text-xs text-white font-semibold">
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
              <div className="mb-5">
                <Separator className="mb-5" />
                <div className="bg-gradient-to-br from-pink-50 via-rose-50 to-pink-50 dark:from-pink-950/30 dark:via-rose-950/30 dark:to-pink-950/30 p-3 md:p-4 rounded-lg border-2 border-pink-200/60 dark:border-pink-800/50 shadow-lg">
                  <div className="flex items-start gap-3">
                    <Star 
                      className="text-pink-600 dark:text-pink-400 flex-shrink-0 mt-1 w-5 h-5" 
                     />
                    <div className="min-w-0">
                      <p className="text-xs md:text-sm text-pink-800 dark:text-pink-300 uppercase tracking-wider font-extrabold mb-3">
                        Value Proposition
                      </p>
                      <p className="text-xs md:text-sm text-gray-800 dark:text-gray-200 leading-relaxed font-medium">
                        {startup.value_proposition || startup.shortDescription}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            )}

            <Separator className="mb-5" />

            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-5">
              <div className="flex items-start gap-2.5">
                <Building size={16} className="text-blue-600 dark:text-blue-400 mt-1 flex-shrink-0"  />
                <div className="min-w-0 flex-1">
                  <p className="text-[10px] md:text-xs text-gray-600 dark:text-gray-400 uppercase tracking-wider font-extrabold mb-2">Location</p>
                  <Badge 
                    variant="outline" 
                    className={cn("text-[10px] md:text-xs font-semibold border-2 h-auto py-1 px-3", getLocationColor(displayLocation).bg, getLocationColor(displayLocation).text, getLocationColor(displayLocation).border)}
                  >
                    {displayLocation}
                  </Badge>
                </div>
              </div>
              
              <div className="flex items-start gap-2.5">
                <Users className="text-purple-600 dark:text-purple-400 mt-1 flex-shrink-0 w-4 h-4"   />
                <div>
                  <p className="text-[10px] md:text-xs text-gray-600 dark:text-gray-400 uppercase tracking-wider font-extrabold mb-2">Team Size</p>
                  <p className="text-xs md:text-sm text-gray-900 dark:text-gray-100 font-bold">{displayEmployees}</p>
                </div>
              </div>

              <div className="flex items-start gap-2.5">
                <Dollar size={16} className="text-emerald-600 dark:text-emerald-400 mt-1 flex-shrink-0"  />
                <div>
                  <p className="text-[10px] md:text-xs text-gray-600 dark:text-gray-400 uppercase tracking-wider font-extrabold mb-2">Funding</p>
                  <p className="text-xs md:text-sm text-gray-900 dark:text-gray-100 font-bold">{displayFunding}</p>
                </div>
              </div>

              <div className="flex items-start gap-2.5">
                <ChartLineUp size={16} className="text-orange-600 dark:text-orange-400 mt-1 flex-shrink-0"  />
                <div>
                  <p className="text-[10px] md:text-xs text-gray-600 dark:text-gray-400 uppercase tracking-wider font-extrabold mb-2">Stage</p>
                  <p className="text-xs md:text-sm text-gray-900 dark:text-gray-100 font-bold">{displayStage}</p>
                </div>
              </div>

              {startup.dateFounded && (
                <div className="flex items-start gap-2.5">
                  <CalendarMonth size={16} className="text-cyan-600 dark:text-cyan-400 mt-1 flex-shrink-0"  />
                  <div>
                    <p className="text-[10px] md:text-xs text-gray-600 dark:text-gray-400 uppercase tracking-wider font-extrabold mb-2">Founded</p>
                    <p className="text-xs md:text-sm text-gray-900 dark:text-gray-100 font-bold">{new Date(startup.dateFounded).getFullYear()}</p>
                  </div>
                </div>
              )}

              {displayWebsite && (
                <div className="flex items-start gap-2.5 md:col-span-3">
                  <Globe size={16} className="text-indigo-600 dark:text-indigo-400 mt-1 flex-shrink-0"  />
                  <div className="min-w-0 flex-1">
                    <p className="text-[10px] md:text-xs text-gray-600 dark:text-gray-400 uppercase tracking-wider font-extrabold mb-2">Website</p>
                    <a 
                      href={displayWebsite.startsWith('http') ? displayWebsite : `https://${displayWebsite}`} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="text-xs md:text-sm text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 hover:underline break-all font-semibold transition-colors"
                      onClick={(e) => e.stopPropagation()}
                    >
                      {displayWebsite.replace(/^https?:\/\//, '').replace(/^www\./, '')}
                    </a>
                  </div>
                </div>
              )}
            </div>

            {startup.interestedVotes.length > 0 && (
              <>
                <Separator className="mb-4" />
                <div className="flex items-center gap-3 py-3 px-5 bg-gradient-to-r from-purple-50 to-pink-50 dark:from-purple-950/30 dark:to-pink-950/30 rounded-lg border-2 border-purple-200/60 dark:border-purple-800/50 shadow-md mb-5">
                  <UsersGroup className="text-purple-600 dark:text-purple-400 flex-shrink-0 w-5 h-5"   />
                  <div className="flex -space-x-2">
                    {startup.interestedVotes.map((vote, idx) => (
                      <Avatar key={idx} className="w-9 h-9 border-2 border-white dark:border-gray-800 shadow-sm">
                        <AvatarFallback className="bg-gradient-to-br from-purple-500 to-pink-500 text-white text-xs font-bold">
                          {getInitials(vote.userName)}
                        </AvatarFallback>
                      </Avatar>
                    ))}
                  </div>
                  <span className="text-xs md:text-sm text-gray-700 dark:text-gray-300 font-semibold ml-1 hidden md:inline">
                    {startup.interestedVotes.map(v => v.userName).join(', ')}
                  </span>
                </div>
              </>
            )}

            {/* Bottom Action Bar with Heart and Rocket */}
            <div className="flex items-center justify-end gap-3 pt-5 border-t-2 border-gray-200 dark:border-gray-700">
              <button
                onClick={(e) => {
                  e.stopPropagation()
                  handleHeartToggle(startup)
                }}
                className="flex items-center gap-2.5 px-5 py-3 rounded-xl bg-gradient-to-br from-white to-pink-50/30 dark:from-gray-800 dark:to-pink-950/30 shadow-md hover:shadow-xl transition-all duration-200 group hover:scale-105 active:scale-95 flex-shrink-0 border-2 border-pink-200/50 dark:border-pink-800/50"
                title={localVotes.some(v => String(v.startupId) === String(startup.id) && v.userId === currentUserId && v.interested) ? 'Unlike this startup' : 'Like this startup'}
              >
                <Heart 
                  size={20} 
                  weight={localVotes.some(v => String(v.startupId) === String(startup.id) && v.userId === currentUserId && v.interested) ? "fill" : "regular"}
                  className={cn(
                    "transition-all duration-200",
                    localVotes.some(v => String(v.startupId) === String(startup.id) && v.userId === currentUserId && v.interested) ? "text-pink-500" : "text-gray-400 group-hover:text-pink-400"
                  )}
                />
                <span className="font-bold text-sm md:text-base text-gray-700 dark:text-gray-300">
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
  }, [localVotes, currentUserId, startupRatings, setSelectedStartup, setIsScheduleDialogOpen])

  return (
    <div className="flex flex-col h-full overflow-hidden">
      <div className="flex-1 overflow-y-auto">
        <div className="max-w-7xl mx-auto p-3 md:p-6 space-y-4 md:space-y-6 pb-6">
          {/* Faceted Search (Topbar) - Redesigned Single Row */}
          <div className="bg-white dark:bg-gray-800 rounded-xl border-2 border-gray-200 dark:border-gray-700 shadow-lg p-4">
            <div className="flex flex-wrap items-center gap-3">
              {/* Search Bar */}
              <div className="flex-1 min-w-[250px]">
                <label htmlFor="simple-search" className="sr-only">Search</label>
                <div className="relative">
                  <div className="absolute inset-y-0 start-0 flex items-center ps-3.5 pointer-events-none">
                    <svg className="w-5 h-5 text-gray-500 dark:text-gray-400" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 20 20">
                      <path stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="m19 19-4-4m0-7A7 7 0 1 1 1 8a7 7 0 0 1 14 0Z"/>
                    </svg>
                  </div>
                  <input 
                    type="search"
                    id="simple-search"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="bg-gray-50 dark:bg-gray-900 border-2 border-gray-300 dark:border-gray-600 text-gray-900 dark:text-gray-100 text-sm rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 block w-full ps-11 p-2.5 placeholder:text-gray-500 dark:placeholder:text-gray-400 font-medium transition-all"
                    placeholder="Search startups by name, description..."
                  />
                </div>
              </div>

              {/* Divider */}
              <div className="hidden sm:block w-px h-10 bg-gray-300 dark:bg-gray-600" />

              {/* Sort By Dropdown */}
              <div className="relative">
                <button
                  type="button"
                  onClick={() => setIsSortDropdownOpen(!isSortDropdownOpen)}
                  className="inline-flex items-center gap-2 text-gray-700 dark:text-gray-200 bg-gray-100 dark:bg-gray-700 border-2 border-gray-300 dark:border-gray-600 hover:bg-gray-200 dark:hover:bg-gray-600 focus:ring-2 focus:outline-none focus:ring-blue-500 font-semibold rounded-lg text-sm px-4 py-2.5 transition-all"
                >
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4h13M3 8h9m-9 4h6m4 0l4-4m0 0l4 4m-4-4v12" />
                  </svg>
                  <span className="whitespace-nowrap">
                    {sortBy === 'votes' ? 'Most Voted' : sortBy === 'funding' ? 'Funding' : 'Grade'}
                  </span>
                  <svg className="w-3 h-3" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 10 6">
                    <path stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="m1 1 4 4 4-4"/>
                  </svg>
                </button>
                
                {isSortDropdownOpen && (
                  <>
                    <div className="fixed inset-0 z-40" onClick={() => setIsSortDropdownOpen(false)} />
                    <div className="absolute z-50 mt-2 bg-white dark:bg-gray-800 border-2 border-gray-200 dark:border-gray-700 rounded-lg shadow-xl w-44 overflow-hidden">
                      <ul className="py-1 text-sm">
                        <li>
                          <button
                            type="button"
                            onClick={() => { setSortBy('votes'); setIsSortDropdownOpen(false) }}
                            className={cn(
                              "block w-full text-left px-4 py-2.5 font-semibold transition-colors",
                              sortBy === 'votes' 
                                ? "bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300" 
                                : "text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700"
                            )}
                          >
                            Most Voted
                          </button>
                        </li>
                        <li>
                          <button
                            type="button"
                            onClick={() => { setSortBy('funding'); setIsSortDropdownOpen(false) }}
                            className={cn(
                              "block w-full text-left px-4 py-2.5 font-semibold transition-colors",
                              sortBy === 'funding' 
                                ? "bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300" 
                                : "text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700"
                            )}
                          >
                            Funding
                          </button>
                        </li>
                        <li>
                          <button
                            type="button"
                            onClick={() => { setSortBy('grade'); setIsSortDropdownOpen(false) }}
                            className={cn(
                              "block w-full text-left px-4 py-2.5 font-semibold transition-colors",
                              sortBy === 'grade' 
                                ? "bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300" 
                                : "text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700"
                            )}
                          >
                            Grade
                          </button>
                        </li>
                      </ul>
                    </div>
                  </>
                )}
              </div>

              {/* Topics Filter - Separate */}
              <AdvancedFilterDropdown
                sections={topicsFilterSections}
                onFilterChange={handleFilterChange}
                onClearAll={() => {
                  setSelectedTopics(new Set())
                  setSelectedUseCases(new Set())
                }}
                activeCount={selectedTopics.size}
                buttonLabel="Topics"
              />

              {/* Use Cases Filter - Only visible when topics are selected */}
              {selectedTopics.size > 0 && uniqueUseCases.length > 0 && (
                <AdvancedFilterDropdown
                  sections={useCasesFilterSections}
                  onFilterChange={handleFilterChange}
                  onClearAll={() => setSelectedUseCases(new Set())}
                  activeCount={selectedUseCases.size}
                  buttonLabel="Use Cases"
                />
              )}

              {/* Other Filters Dropdown */}
              <AdvancedFilterDropdown
                sections={otherFilterSections}
                onFilterChange={handleFilterChange}
                onClearAll={() => {
                  setSelectedGrades(new Set())
                  setSelectedStages(new Set())
                  setSelectedTechs(new Set())
                }}
                activeCount={selectedGrades.size + selectedStages.size + selectedTechs.size}
                buttonLabel="More Filters"
              />

              {/* Active Filter Count Badge & Results */}
              {activeFilterCount > 0 && (
                <div className="flex items-center gap-2">
                  <div className="flex items-center gap-1.5 bg-blue-100 dark:bg-blue-900/30 border-2 border-blue-300 dark:border-blue-700 text-blue-700 dark:text-blue-300 px-3 py-2 rounded-lg font-bold text-sm">
                    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M3 3a1 1 0 011-1h12a1 1 0 011 1v3a1 1 0 01-.293.707L12 11.414V15a1 1 0 01-.293.707l-2 2A1 1 0 018 17v-5.586L3.293 6.707A1 1 0 013 6V3z" clipRule="evenodd" />
                    </svg>
                    <span>{activeFilterCount}</span>
                  </div>
                  <span className="text-sm font-semibold text-gray-600 dark:text-gray-400">
                    {startupsWithVotes.length} results
                  </span>
                </div>
              )}

              {/* Clear All Filters */}
              {activeFilterCount > 0 && (
                <button
                  onClick={handleClearAllFilters}
                  className="inline-flex items-center gap-1.5 text-red-600 dark:text-red-400 hover:text-red-700 dark:hover:text-red-300 font-semibold text-sm transition-colors"
                >
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                  Clear all
                </button>
              )}
            </div>
          </div>

          {/* Results Count - Only show when filters active */}
          {(activeFilterCount > 0 || searchQuery) && startupsWithVotes.length === 0 && (
            <div className="bg-yellow-50 dark:bg-yellow-900/20 border-2 border-yellow-200 dark:border-yellow-800 rounded-xl p-4 text-center">
              <p className="text-sm font-semibold text-yellow-800 dark:text-yellow-200">
                No startups match your search criteria. Try adjusting your filters.
              </p>
            </div>
          )}

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
              <UsersGroup className="md:w-16 md:h-16 text-muted-foreground mx-auto mb-3 md:mb-4 w-12 h-12"  />
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

      {/* Modals - Fixed positioning, won't affect layout */}
      <Dialog open={isScheduleDialogOpen} onOpenChange={setIsScheduleDialogOpen}>
        <DialogContent className="sm:max-w-[500px]" aria-describedby="schedule-dialog-description">
          <DialogHeader>
            <DialogTitle id="schedule-dialog-title">Schedule Meeting with {selectedStartup?.["Company Name"]}</DialogTitle>
            <DialogDescription id="schedule-dialog-description">
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

    </div>
  )
}

// Memoize to prevent re-renders when votes haven't changed
export const DashboardView = memo(DashboardViewComponent)
