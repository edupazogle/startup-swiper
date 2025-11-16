import { useState, useEffect } from 'react'
import { useIsMobile } from '@/hooks/use-mobile'
import { LoginView } from '@/components/LoginView'
import { AuroralBackground } from '@/components/AuroralBackground'
import { SwipeView } from '@/components/SwipeView'
import { DashboardView } from '@/components/DashboardView'
import { InsightsView } from '@/components/InsightsView'
import { CalendarView } from '@/components/CalendarViewNew'
import { AIAssistantView } from '@/components/AIAssistantView'
import { AdminView } from '@/components/AdminView'
import { AddStartupDialog } from '@/components/AddStartupDialog'
import { AddIdeaDialog } from '@/components/AddIdeaDialog'
import { PWAUpdatePrompt } from '@/components/PWAUpdatePrompt'
import { Button } from '@/components/ui/button'
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Startup, Vote, CalendarEvent, Idea } from '@/lib/types'
import { initialStartups } from '@/lib/initialStartups'
import { InsightsAPI } from '@/lib/notificationManager'
import { api } from '@/lib/api'
import { Swatches, Rocket, Lightbulb, CalendarBlank, UserGear, Plus, Robot, Bell, BellSlash, SignOut } from '@phosphor-icons/react'
import { Toaster } from '@/components/ui/sonner'
import { toast } from 'sonner'
import logoVC from '@/assets/images/logo_vc.png'
import logoMain from '@/assets/images/f8cba53d-0d66-4aab-b97c-8fa66871fa8b.png'


function App() {
  const isMobile = useIsMobile()
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false)
  const [currentUserId, setCurrentUserId] = useState<string>('')
  const [currentUserName, setCurrentUserName] = useState<string>('')
  const [notificationManager, setNotificationManager] = useState<null>(null)
  const [notificationsEnabled, setNotificationsEnabled] = useState(false)
  const [showNotificationSetup, setShowNotificationSetup] = useState(false)
  
  // Load calendar events from API
  const [fixedEvents, setFixedEvents] = useState<CalendarEvent[]>([])
  const [isLoadingEvents, setIsLoadingEvents] = useState(true)

  useEffect(() => {
    const fetchEvents = async () => {
      try {
        setIsLoadingEvents(true)
        const events = await api.getCalendarEvents(0, 200)
        
        const transformedEvents: CalendarEvent[] = events.map(event => ({
          id: event.id,
          title: event.title,
          startTime: new Date(event.start_time),
          endTime: new Date(event.end_time),
          type: event.type,
          attendees: event.attendees || [],
          location: event.stage as any, // Map 'stage' from DB to 'location' in frontend
          category: event.category as any,
          link: event.link,
          isFixed: event.is_fixed !== false,
          highlight: event.highlight
        }))
        
        setFixedEvents(transformedEvents)
        console.log(`✓ Loaded ${transformedEvents.length} events from API`)
      } catch (error) {
        console.error('Failed to fetch events from API:', error)
        // Fallback to empty
        setFixedEvents([])
      } finally {
        setIsLoadingEvents(false)
      }
    }
    
    fetchEvents()
  }, [])
  
  useEffect(() => {
    const initializeUser = async () => {
      try {
        // First, check if user is already stored in localStorage (persistent session)
        // NOTE: localStorage is per-browser/device, so each user on their own computer
        // will have their own separate session stored. No cross-user conflicts.
        const savedSession = localStorage.getItem('startup_swiper_session')
        if (savedSession) {
          try {
            const session = JSON.parse(savedSession)
            if (session.userId && session.userName) {
              setCurrentUserId(session.userId)
              setCurrentUserName(session.userName)
              setIsAuthenticated(true)
              console.log('✓ Restored session from localStorage:', session.userId)
              return
            }
          } catch (e) {
            console.warn('Failed to parse saved session:', e)
            localStorage.removeItem('startup_swiper_session')
          }
        }

        // If a hosted SSO/Spark provider is available, use it to sign users in.
        if (typeof window !== 'undefined' && (window as any).spark && typeof (window as any).spark.user === 'function') {
          const user = await (window as any).spark.user()
          if (user && user.id) {
            const userId = String(user.id)
            setCurrentUserId(userId)
            if (user.login) setCurrentUserName(user.login)
            setIsAuthenticated(true)
            // Save to localStorage for persistence (isolated to this browser/device)
            localStorage.setItem('startup_swiper_session', JSON.stringify({
              userId,
              userName: user.login || 'User'
            }))
            console.log('✓ Signed in via Spark provider:', userId)
            return
          }
        }

        // No external provider: remain signed out until user logs in via the app
        console.log('No external SSO available; user must log in')
      } catch (error) {
        console.warn('Failed to initialize external user provider:', error)
      }
    }
    initializeUser()
  }, [])

  // Initialize notification system
  useEffect(() => {
    // Notifications disabled: rely on database only
    setNotificationsEnabled(false)
    setShowNotificationSetup(false)
    return
  }, [currentUserId])

  // Load startups from backend API with prioritization
  const [startups, setStartups] = useState<Startup[]>([])
  const [allStartups, setAllStartups] = useState<Startup[]>([])
  const [isLoadingStartups, setIsLoadingStartups] = useState(true)
  const [votes, setVotes] = useState<Vote[]>([])
  
  // Fetch AXA-filtered startups for swiper and all startups for dashboard
  // We require an authenticated user; `safeUserId` is the authenticated id.
  const safeUserId = currentUserId

  // Fetch votes from API on app load and refresh them
  useEffect(() => {
    const fetchVotes = async () => {
      try {
        const apiVotes = await api.getVotes(0, 10000)
        if (apiVotes && Array.isArray(apiVotes)) {
          // Convert API votes to frontend format
          const convertedVotes: Vote[] = apiVotes.map(v => ({
            startupId: v.startupId,
            userId: v.userId,
            userName: v.userName || 'Unknown',
            interested: v.interested,
            timestamp: typeof v.timestamp === 'string' ? new Date(v.timestamp).getTime() : v.timestamp,
            meetingScheduled: v.meetingScheduled || false
          }))
          
          setVotes(convertedVotes)
          console.log(`✓ Loaded ${convertedVotes.length} votes from API`)
        }
      } catch (error) {
        console.error('Failed to fetch votes from API:', error)
        setVotes([])
      }
    }
    
    fetchVotes()
    // Refresh votes every 5 seconds to stay in sync with API
    const interval = setInterval(fetchVotes, 5000)
    return () => clearInterval(interval)
  }, [])

  useEffect(() => {
    const fetchStartups = async () => {
      try {
        setIsLoadingStartups(true)
        
        // Fetch Phase 1 startups (top 20 funded with topic variety)
        let swiperData
        try {
          swiperData = await api.getPhase1Startups(safeUserId)
          console.log('✓ Loaded Phase 1 startups (20 top-funded with category variety)')
        } catch (error) {
          console.warn('Phase 1 endpoint not available, falling back to AXA filtering:', error)
          // Fallback to AXA-filtered if phase endpoint fails
          try {
            swiperData = await api.getAxaFilteredStartups(300, 25)
            console.log('✓ Loaded AXA-filtered startups for swiper (NVIDIA NIM enhanced)')
          } catch (fallbackError) {
            console.warn('AXA filtered endpoint not available, falling back to standard prioritization:', fallbackError)
            // Final fallback to standard prioritized startups if AXA endpoint fails
            swiperData = await api.getPrioritizedStartups(safeUserId, 300, 30)
          }
        }
        
        if (swiperData.startups && Array.isArray(swiperData.startups)) {
          // Transform to match frontend format
          // Helper function to parse topics/tech from various formats
          const parseArray = (value: any): string[] => {
            if (Array.isArray(value)) return value
            if (typeof value === 'string') {
              try {
                const parsed = JSON.parse(value)
                return Array.isArray(parsed) ? parsed : []
              } catch {
                return value.split(',').map((v: string) => v.trim()).filter((v: string) => v)
              }
            }
            return []
          }

          const transformedSwiperStartups = swiperData.startups.map((s: any, i: number) => ({
            id: s.id || `startup-${i}`,
            name: s.name || s.company_name || "Unknown",
            description: s.description || s.company_description || "",
            shortDescription: s.shortDescription || "",
            website: s.website || "",
            topics: parseArray(s.topics || s.Topics),
            tech: parseArray(s.tech || s.Tech || s.technologies),
            maturity: s.maturity || "Undisclosed",
            employees: s.employees,
            billingCity: s.billingCity,
            billingCountry: s.billingCountry,
            maturity_score: s.maturity_score,
            logoUrl: s.logoUrl,
            total_funding: s.total_funding,
            last_funding_date: s.last_funding_date,
            valuation: s.valuation,
            funding_stage: s.funding_stage,
            currentInvestmentStage: s.currentInvestmentStage,
            dateFounded: s.dateFounded,
            // Legacy fields
            "Company Name": s.company_name || s.name || "Unknown",
            "Company Description": s.company_description || s.description || "",
            "Category": s.primary_industry || s.category || "General",
            "Stage": s.currentInvestmentStage || s.funding_stage || s.stage || "Unknown",
            "Website": s.website || "",
            ...s // Include all other fields
          }))
          setStartups(transformedSwiperStartups)
          
          // Log filtering info if available
          if ((swiperData as any).source === 'axa_enhanced_filter') {
            console.log(`✓ Loaded ${transformedSwiperStartups.length} AXA-filtered startups for swiper (${(swiperData as any).processing.method})`)
            console.log(`  Tier breakdown:`, (swiperData as any).tier_breakdown)
          } else {
            console.log(`✓ Loaded ${transformedSwiperStartups.length} prioritized startups for swiper`)
          }
        } else {
          console.error('Invalid swiper startup data format:', swiperData)
          // Fallback to local data if API fails
          setStartups(initialStartups.map((s, i) => ({ ...s, id: `startup-${i + 1}` })))
        }
        
        // Fetch all startups from database for dashboard view
        try {
          const allStartupsData = await api.getAllStartups(0, 10000)
          if (allStartupsData.startups && Array.isArray(allStartupsData.startups)) {
            const transformedAllStartups = allStartupsData.startups.map((s: any, i: number) => {
              // Helper function to parse topics/tech from various formats
              const parseArray = (value: any): string[] => {
                if (Array.isArray(value)) return value
                if (typeof value === 'string') {
                  try {
                    const parsed = JSON.parse(value)
                    return Array.isArray(parsed) ? parsed : []
                  } catch {
                    return value.split(',').map((v: string) => v.trim()).filter((v: string) => v)
                  }
                }
                return []
              }

              return {
                id: s.id || `startup-${i}`,
                name: s.name || s.company_name || "Unknown",
                description: s.description || s.company_description || "",
                shortDescription: s.shortDescription || "",
                website: s.website || "",
                topics: parseArray(s.topics),
                tech: parseArray(s.tech),
                maturity: s.maturity || "Undisclosed",
                employees: s.employees,
                billingCity: s.billingCity,
                billingCountry: s.billingCountry,
                maturity_score: s.maturity_score,
                logoUrl: s.logoUrl,
                total_funding: s.total_funding,
                last_funding_date: s.last_funding_date,
                valuation: s.valuation,
                funding_stage: s.funding_stage,
                currentInvestmentStage: s.currentInvestmentStage,
                dateFounded: s.dateFounded,
                // Legacy fields
                "Company Name": s.company_name || s.name || "Unknown",
                "Company Description": s.description || s.company_description || "",
                "Category": s.primary_industry || s.category || "General",
                "Stage": s.currentInvestmentStage || s.funding_stage || s.stage || "Unknown",
                "Website": s.website || "",
                ...s // Include all other fields
              }
            })
            setAllStartups(transformedAllStartups)
            console.log(`✓ Loaded ${transformedAllStartups.length} total startups for dashboard`)
            console.log('Sample startup topics/tech:', transformedAllStartups[0]?.topics, transformedAllStartups[0]?.tech)
          }
        } catch (error) {
          console.warn('Failed to load all startups for dashboard:', error)
          // Fallback: use swiper startups for dashboard too
          setAllStartups(startups)
        }
      } catch (error) {
        console.error('Failed to fetch startups:', error)
        // Fallback to local data if API fails
        const fallbackStartups = initialStartups.map((s, i) => ({ ...s, id: `startup-${i + 1}` }))
        setStartups(fallbackStartups)
        setAllStartups(fallbackStartups)
      } finally {
        setIsLoadingStartups(false)
      }
    }

    if (safeUserId) {
      fetchStartups()
    }
  }, [safeUserId])
  
  // Load Phase 2 startups when user completes Phase 1 (20+ swipes)
  const [phase2Loaded, setPhase2Loaded] = useState(false)
  useEffect(() => {
    const loadPhase2IfNeeded = async () => {
      try {
        // Count votes
        const userVotes = votes.filter(v => v.userId === currentUserId)
        const swipeCount = userVotes.length
        
        // If user has 20+ swipes and Phase 2 not yet loaded, load it
        if (swipeCount >= 20 && !phase2Loaded) {
          console.log('🎯 Phase 1 complete! Loading Phase 2 startups...')
          const phase2Data = await api.getPhase2Startups(safeUserId)
          
          if (phase2Data && phase2Data.startups) {
            // Transform Phase 2 startups the same way as Phase 1
            const parseArray = (value: any): string[] => {
              if (Array.isArray(value)) return value
              if (typeof value === 'string') {
                try {
                  const parsed = JSON.parse(value)
                  return Array.isArray(parsed) ? parsed : []
                } catch {
                  return value.split(',').map((v: string) => v.trim()).filter((v: string) => v)
                }
              }
              return []
            }
            
            const transformedPhase2 = phase2Data.startups.map((s: any, i: number) => ({
              id: s.id || `startup-${i}`,
              name: s.name || s.company_name || "Unknown",
              description: s.description || s.company_description || "",
              shortDescription: s.shortDescription || "",
              website: s.website || "",
              topics: parseArray(s.topics || s.Topics),
              tech: parseArray(s.tech || s.Tech || s.technologies),
              maturity: s.maturity || "Undisclosed",
              employees: s.employees,
              billingCity: s.billingCity,
              billingCountry: s.billingCountry,
              maturity_score: s.maturity_score,
              logoUrl: s.logoUrl,
              total_funding: s.total_funding,
              axa_overall_score: s.axa_overall_score,
              axaOverallScore: s.axa_overall_score,
              axa_priority_tier: s.axa_priority_tier,
              axaPriorityTier: s.axa_priority_tier,
              axa_use_cases: parseArray(s.axa_use_cases),
              axaUseCases: parseArray(s.axa_use_cases),
            }))
            
            // Append Phase 2 startups to existing pool
            setStartups(prev => [...prev, ...transformedPhase2])
            setPhase2Loaded(true)
            console.log(`✓ Loaded ${phase2Data.startups.length} Phase 2 startups (tier: ${phase2Data.tier_used})`)
          }
        }
      } catch (error) {
        console.error('Failed to load Phase 2 startups:', error)
      }
    }
    
    if (safeUserId && votes.length > 0) {
      loadPhase2IfNeeded()
    }
  }, [votes.length, safeUserId, phase2Loaded])

  // User-generated data (not synced to API)
  const [userEvents, setUserEvents] = useState<CalendarEvent[]>([])
  const [ideas, setIdeas] = useState<Idea[]>([])
  const [currentView, setCurrentView] = useState<'swipe' | 'dashboard' | 'insights' | 'calendar' | 'ai' | 'admin'>('swipe')
  const [isAddStartupDialogOpen, setIsAddStartupDialogOpen] = useState(false)
  const [isAddIdeaDialogOpen, setIsAddIdeaDialogOpen] = useState(false)

  // Load categorized insights and merge with ideas
  const fetchCategorizedInsights = async () => {
    try {
      // Fetch categorized insights from all categories
      const response = await fetch(`${import.meta.env.VITE_API_URL}/insights/categorized/all`)
      if (response.ok) {
        const byCategory = await response.json()
        
        // Flatten into array of ideas
        const allCategorizedInsights: Idea[] = []
        for (const category in byCategory) {
          allCategorizedInsights.push(...byCategory[category])
        }
        
        // Replace all ideas with the fetched ones
        setIdeas(allCategorizedInsights)
        
        const categoriesWithInsights = Object.keys(byCategory).filter(k => byCategory[k].length > 0)
        console.log(`✓ Loaded ${allCategorizedInsights.length} categorized insights across ${categoriesWithInsights.length} categories`)
        console.log(`  Categories populated: ${categoriesWithInsights.join(', ')}`)
      }
    } catch (error) {
      console.warn('Failed to load categorized insights:', error)
    }
  }

  useEffect(() => {
    fetchCategorizedInsights()
  }, []) // Run once on mount

  // Combine fixed events from DB with user events
  const safeVotes = votes ?? []
  const allEvents = [...fixedEvents, ...(userEvents ?? [])]
  const safeEvents = allEvents.map(event => {
    let startTime: Date
    let endTime: Date
    
    if (event.startTime instanceof Date) {
      startTime = event.startTime
    } else if (typeof event.startTime === 'string' || typeof event.startTime === 'number') {
      startTime = new Date(event.startTime)
    } else {
      startTime = new Date()
    }
    
    if (event.endTime instanceof Date) {
      endTime = event.endTime
    } else if (typeof event.endTime === 'string' || typeof event.endTime === 'number') {
      endTime = new Date(event.endTime)
    } else {
      endTime = new Date()
    }
    
    return {
      ...event,
      startTime,
      endTime
    }
  })
  const safeIdeas = ideas ?? []

  const handleVote = async (startupId: string, interested: boolean) => {
    // Create vote object
    const vote = {
      startupId,
      userId: safeUserId,
      userName: currentUserName,
      interested,
      timestamp: Date.now(),
      meetingScheduled: false
    }

    // Save to backend using API service
    try {
      await api.createVote({
        startupId,
        userId: safeUserId,
        userName: currentUserName,
        interested,
        timestamp: new Date().toISOString(),
        meetingScheduled: false
      })
    } catch (error) {
      console.error('Failed to save vote to database:', error)
      // Continue anyway to update local state
    }

    // Update local state
    setVotes((currentVotes) => [...(currentVotes ?? []), vote])
    
    const startup = startups.find((s) => s.id === startupId)
    if (startup) {
      toast.success(interested ? `Added ${startup["Company Name"]} to interested list` : `Passed on ${startup["Company Name"]}`)
    }

    // After 10 votes, notify user that personalization is active
    const voteCount = (votes ?? []).filter(v => v.userId === safeUserId).length + 1
    if (voteCount === 10) {
      toast.info('🎯 Learning your preferences! Recommendations will now be personalized.')
    }
  }

  const handleChangeVote = (startupId: string, interested: boolean) => {
    setVotes((currentVotes) => {
      const filtered = (currentVotes ?? []).filter(
        (v) => !(v.startupId === startupId && v.userId === safeUserId)
      )
      return [
        ...filtered,
        {
          startupId,
          userId: safeUserId,
          userName: currentUserName,
          interested,
          timestamp: Date.now(),
          meetingScheduled: false
        }
      ]
    })
    
    const startup = startups.find((s) => s.id === startupId)
    if (startup) {
      toast.success(interested ? `Changed to interested in ${startup["Company Name"]}` : `Changed to passed on ${startup["Company Name"]}`)
    }
  }

  const handleScheduleMeeting = async (startupId: string, eventData: Omit<CalendarEvent, 'id' | 'attendees' | 'startupId' | 'startupName'>) => {
    const startup = startups.find((s) => s.id === startupId)
    if (!startup) return

    const newEvent: CalendarEvent = {
      ...eventData,
      id: `event-${Date.now()}`,
      attendees: [currentUserName],
      startupId,
      startupName: startup["Company Name"],
      confirmed: eventData.confirmed ?? false,
      startTime: new Date(eventData.startTime),
      endTime: new Date(eventData.endTime)
    }

    setUserEvents((currentEvents) => [...(currentEvents ?? []), newEvent])
    
    setVotes((currentVotes) =>
      (currentVotes ?? []).map((v) =>
        v.startupId === startupId && v.userId === safeUserId
          ? { ...v, meetingScheduled: true }
          : v
      )
    )

    toast.success(`Meeting scheduled with ${startup["Company Name"]}`)

    // Schedule notification for insight 5 minutes after meeting
    try {
      await InsightsAPI.scheduleNotification(
        newEvent.id,
        safeUserId,
        new Date(newEvent.endTime).toISOString()
      )
      console.log('Notification scheduled for meeting:', newEvent.id)
    } catch (error) {
      console.error('Failed to schedule notification:', error)
    }
  }

  const handleAddEvent = async (event: Omit<CalendarEvent, 'id' | 'attendees'>) => {
    const newEvent: CalendarEvent = {
      ...event,
      id: `event-${Date.now()}`,
      attendees: [currentUserName],
      startTime: new Date(event.startTime),
      endTime: new Date(event.endTime)
    }
    setUserEvents((currentEvents) => [...(currentEvents ?? []), newEvent])
    toast.success('Event added to calendar')

    // Schedule notification for meetings
    if (newEvent.type === 'meeting') {
      try {
        await InsightsAPI.scheduleNotification(
          newEvent.id,
          safeUserId,
          new Date(newEvent.endTime).toISOString()
        )
        console.log('Notification scheduled for event:', newEvent.id)
      } catch (error) {
        console.error('Failed to schedule notification:', error)
      }
    }
  }

  const handleEnableNotifications = async () => {
    if (!notificationManager) return

    try {
      const permission = await notificationManager.requestPermission()
      
      if (permission === 'granted') {
        setNotificationsEnabled(true)
        setShowNotificationSetup(false)
        toast.success('🔔 Notifications enabled! You\'ll get reminders to share insights.')
      } else if (permission === 'denied') {
        toast.error('Notifications blocked. Enable them in your browser settings.')
      }
    } catch (error) {
      console.error('Failed to enable notifications:', error)
      toast.error('Failed to enable notifications')
    }
  }

  const handleDeleteEvent = (eventId: string) => {
    setUserEvents((currentEvents) => (currentEvents ?? []).filter((e) => e.id !== eventId))
    toast.success('Event deleted')
  }

  const handleToggleAttendance = (eventId: string) => {
    setUserEvents((currentEvents) =>
      (currentEvents ?? []).map((e) => {
        if (e.id === eventId) {
          const attendees = e.attendees.includes(currentUserName)
            ? e.attendees.filter((a) => a !== currentUserName)
            : [...e.attendees, currentUserName]
          return { ...e, attendees }
        }
        return e
      })
    )
    toast.success('Attendance updated')
  }

  const handleAddStartup = (newStartup: Omit<Startup, 'id'>) => {
    const startup: Startup = {
      ...newStartup,
      id: `startup-${Date.now()}`
    }
    setStartups((currentStartups) => [...currentStartups, startup])
    setIsAddStartupDialogOpen(false)
    toast.success(`Added ${startup["Company Name"]}`)
  }

  const handleDeleteStartup = (startupId: string) => {
    setStartups((currentStartups) => currentStartups.filter((s) => s.id !== startupId))
    setVotes((currentVotes) => (currentVotes ?? []).filter((v) => v.startupId !== startupId))
    setUserEvents((currentEvents) => (currentEvents ?? []).filter((e) => e.startupId !== startupId))
    toast.success('Startup deleted')
  }

  const handleAddIdea = (newIdea: Omit<Idea, 'id' | 'timestamp'>) => {
    const idea: Idea = {
      ...newIdea,
      id: `idea-${Date.now()}`,
      timestamp: Date.now()
    }
    setIdeas((currentIdeas) => [...(currentIdeas ?? []), idea])
    toast.success('Idea submitted successfully!')
  }

  // Show login view if not authenticated (before loading startups)
  if (!isAuthenticated) {
    return (
      <LoginView
        onLogin={(email, name) => {
          setCurrentUserId(email)
          setCurrentUserName(name)
          setIsAuthenticated(true)
          // Save session to localStorage for persistence
          localStorage.setItem('startup_swiper_session', JSON.stringify({
            userId: email,
            userName: name
          }))
          toast.success(`Welcome, ${name}!`)
        }}
      />
    )
  }

  // Show loading state while fetching startups (only after authentication)
  if (isLoadingStartups) {
    return (
      <AuroralBackground>
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
            <p className="text-muted-foreground">Loading prioritized startups...</p>
          </div>
        </div>
      </AuroralBackground>
    )
  }

  return (
    <AuroralBackground>
      <div className="flex flex-col h-dvh overflow-hidden" style={{ paddingTop: 'var(--safe-top)' }}>
        {(currentView !== 'ai' || !isMobile) && (
          <header className={`border-b border-white/20 bg-white/20 backdrop-blur-md flex-shrink-0 py-2 sm:py-3 md:py-4 px-3 sm:px-4`}>
          <div className="container mx-auto px-4 py-3 md:py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-start gap-2 md:gap-3 flex-shrink-0" style={{ width: isMobile ? 'auto' : '200px' }}>
                <img src={logoMain} alt="Logo" className="h-[1.2rem] md:h-[2rem] w-auto mt-1.5 md:mt-2" />
                <div className="flex flex-col">
                  <h1 className="font-black text-white text-2xl md:text-4xl whitespace-nowrap">Startup Rise</h1>
                  <span className="text-xs md:text-sm text-white mt-1 font-light">@Slush2025</span>
                </div>
              </div>
              
              {!isMobile && (
                <div className="flex-shrink-0">
                  <Tabs value={currentView} onValueChange={(v) => setCurrentView(v as any)}>
                    <TabsList className="bg-transparent border-none flex-wrap h-auto p-1.5">
                      <TabsTrigger value="swipe" className="data-[state=active]:bg-white/70 !text-gray-900 h-14 px-8 text-xl font-bold [&_svg]:!text-gray-900">
                        <Swatches className="mr-3" size={32} weight="bold" />
                        Swipe
                      </TabsTrigger>
                      <TabsTrigger value="dashboard" className="data-[state=active]:bg-white/70 !text-gray-900 h-14 px-8 text-xl font-bold [&_svg]:!text-gray-900">
                        <Rocket className="mr-3" size={32} weight="bold" />
                        Startups
                      </TabsTrigger>
                      <TabsTrigger value="insights" className="data-[state=active]:bg-white/70 !text-gray-900 h-14 px-8 text-xl font-bold [&_svg]:!text-gray-900">
                        <Lightbulb className="mr-3" size={32} weight="bold" />
                        Insights
                      </TabsTrigger>
                      <TabsTrigger value="calendar" className="data-[state=active]:bg-white/70 !text-gray-900 h-14 px-8 text-xl font-bold [&_svg]:!text-gray-900">
                        <CalendarBlank className="mr-3" size={32} weight="bold" />
                        Calendar
                      </TabsTrigger>
                      <TabsTrigger value="ai" className="data-[state=active]:bg-white/70 !text-gray-900 h-14 px-8 text-xl font-bold [&_svg]:!text-gray-900">
                        <Robot className="mr-3" size={32} weight="bold" />
                        Concierge
                      </TabsTrigger>
                    </TabsList>
                  </Tabs>
                </div>
              )}
              
              <div className="flex-shrink-0" style={{ width: isMobile ? 'auto' : '200px', display: 'flex', justifyContent: 'flex-end' }}>
                <div className="flex gap-2">
                  {notificationManager && (
                    <Button
                      onClick={handleEnableNotifications}
                      variant="ghost"
                      size={isMobile ? 'sm' : 'default'}
                      className={`h-10 sm:h-12 md:h-14 ${
                        notificationsEnabled
                          ? 'text-green-400 hover:text-green-300'
                          : 'text-white/60 hover:text-white'
                      }`}
                      title={notificationsEnabled ? 'Notifications enabled' : 'Enable notifications'}
                    >
                      {notificationsEnabled ? (
                        <Bell size={isMobile ? 20 : 24} weight="fill" />
                      ) : (
                        <BellSlash size={isMobile ? 20 : 24} />
                      )}
                    </Button>
                  )}
                  <Button
                    onClick={() => setCurrentView('admin')}
                    variant="ghost"
                    className={`${
                      currentView === 'admin' 
                        ? 'bg-white/90 text-gray-900' 
                        : 'text-white hover:bg-white/30 hover:text-white'
                    } h-10 sm:h-12 md:h-14 ${isMobile ? 'px-3' : 'px-6'} font-bold text-lg sm:text-xl`}
                  >
                    <UserGear size={28} className={isMobile ? '' : 'mr-3'} weight="bold" />
                    {!isMobile && 'Admin'}
                  </Button>
                  <Button
                    onClick={() => {
                      setIsAuthenticated(false)
                      setCurrentUserId('')
                      setCurrentUserName('')
                      // Clear session from localStorage
                      localStorage.removeItem('startup_swiper_session')
                      toast('Signed out')
                    }}
                    variant="ghost"
                    className={`text-white hover:bg-white/10 h-10 sm:h-12 md:h-14 ${isMobile ? 'px-3' : 'px-6'} font-bold text-base sm:text-lg`}
                  >
                    <SignOut size={24} className={isMobile ? '' : 'mr-2'} />
                    {!isMobile && 'Sign out'}
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </header>
        )}

        {/* Notification Setup Prompt */}
        {showNotificationSetup && !notificationsEnabled && (
          <div className="fixed top-4 right-4 z-40 max-w-sm">
            <div className="bg-gradient-to-br from-indigo-500 to-purple-600 rounded-lg shadow-2xl p-6 text-white">
              <div className="flex items-start gap-3">
                <Bell size={32} weight="fill" className="flex-shrink-0 mt-1" />
                <div className="flex-1">
                  <h3 className="font-bold text-lg mb-2">
                    Enable Insight Reminders
                  </h3>
                  <p className="text-sm text-white/90 mb-4">
                    Get notified 5 minutes after each meeting to share your insights and learnings.
                  </p>
                  <div className="flex gap-2">
                    <Button
                      size="sm"
                      onClick={handleEnableNotifications}
                      className="bg-white text-indigo-600 hover:bg-gray-100"
                    >
                      Enable
                    </Button>
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => setShowNotificationSetup(false)}
                      className="text-white hover:bg-white/20"
                    >
                      Later
                    </Button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        <main className={`flex-1 min-h-0 overflow-y-auto overflow-x-hidden flex flex-col ${isMobile ? 'pb-[calc(var(--nav-height-mobile)+env(safe-area-inset-bottom)+8px)]' : ''}`}>
          {currentView === 'swipe' && (
            <SwipeView
              startups={startups}
              votes={safeVotes}
              currentUserId={safeUserId}
              currentUserName={currentUserName}
              onVote={handleVote}
            />
          )}
          
          {currentView === 'dashboard' && (
            <DashboardView
              startups={allStartups}
              votes={safeVotes}
              events={safeEvents}
              currentUserId={safeUserId}
              onScheduleMeeting={handleScheduleMeeting}
              onVoteChange={handleChangeVote}
            />
          )}
          
          {currentView === 'insights' && (
            <InsightsView
              ideas={safeIdeas}
              onIdeaUpdated={fetchCategorizedInsights}
            />
          )}
          
          {currentView === 'calendar' && (
            <CalendarView
              currentUserId={safeUserId}
              currentUserName={currentUserName}
              events={safeEvents}
              onAddEvent={handleAddEvent}
              onDeleteEvent={handleDeleteEvent}
              onToggleAttendance={handleToggleAttendance}
              onNavigateToLinkedIn={() => setCurrentView('ai')}
            />
          )}
          
          {currentView === 'ai' && (
            <AIAssistantView />
          )}
          
          {currentView === 'admin' && (
            <AdminView
              startups={startups}
              votes={safeVotes}
              events={safeEvents}
              currentUserId={safeUserId}
            />
          )}
        </main>

        {isMobile && (
          <>
            <nav className="fixed bottom-0 left-0 right-0 bg-black/30 backdrop-blur-md border-t border-white/10 z-[51]" style={{ paddingBottom: 'env(safe-area-inset-bottom)' }}>
              <div className="flex items-center justify-around px-2 py-1 sm:py-2">
                  <button
                    onClick={() => setCurrentView('swipe')}
                    className={`flex flex-col items-center justify-center gap-0.5 sm:gap-1 px-2 sm:px-3 py-1.5 sm:py-2 min-h-[48px] text-[10px] xs:text-[11px] sm:text-xs md:text-sm rounded-md transition-colors ${
                      currentView === 'swipe' 
                        ? 'bg-white/20 text-white' 
                        : 'text-white'
                    }`}
                  >
                    <Swatches size={24} weight={currentView === 'swipe' ? 'fill' : 'bold'} />
                    <span className="text-center font-bold">Swipe</span>
                  </button>
                  
                  <button
                    onClick={() => setCurrentView('dashboard')}
                    className={`flex flex-col items-center justify-center gap-0.5 sm:gap-1 px-2 sm:px-3 py-1.5 sm:py-2 min-h-[48px] text-[10px] xs:text-[11px] sm:text-xs md:text-sm rounded-md transition-colors ${
                      currentView === 'dashboard' 
                        ? 'bg-white/20 text-white' 
                        : 'text-white'
                    }`}
                  >
                    <Rocket size={24} weight={currentView === 'dashboard' ? 'fill' : 'bold'} />
                    <span className="text-center font-bold">Startups</span>
                  </button>
                  
                  <button
                    onClick={() => setCurrentView('insights')}
                    className={`flex flex-col items-center justify-center gap-0.5 sm:gap-1 px-2 sm:px-3 py-1.5 sm:py-2 min-h-[48px] text-[10px] xs:text-[11px] sm:text-xs md:text-sm rounded-md transition-colors ${
                      currentView === 'insights' 
                        ? 'bg-white/20 text-white' 
                        : 'text-white'
                    }`}
                  >
                    <Lightbulb size={24} weight={currentView === 'insights' ? 'fill' : 'bold'} />
                    <span className="text-center font-bold">Insights</span>
                  </button>
                  
                  <button
                    onClick={() => setCurrentView('calendar')}
                    className={`flex flex-col items-center justify-center gap-0.5 sm:gap-1 px-2 sm:px-3 py-1.5 sm:py-2 min-h-[48px] text-[10px] xs:text-[11px] sm:text-xs md:text-sm rounded-md transition-colors ${
                      currentView === 'calendar' 
                        ? 'bg-white/20 text-white' 
                        : 'text-white'
                    }`}
                  >
                    <CalendarBlank size={24} weight={currentView === 'calendar' ? 'fill' : 'bold'} />
                    <span className="text-center font-bold">Calendar</span>
                  </button>
                  
                  <button
                    onClick={() => setCurrentView('ai')}
                    className={`flex flex-col items-center justify-center gap-0.5 sm:gap-1 px-2 sm:px-3 py-1.5 sm:py-2 min-h-[48px] text-[10px] xs:text-[11px] sm:text-xs md:text-sm rounded-md transition-colors ${
                      currentView === 'ai' 
                        ? 'bg-white/20 text-white' 
                        : 'text-white'
                    }`}
                  >
                    <Robot size={24} weight={currentView === 'ai' ? 'fill' : 'bold'} />
                    <span className="text-center font-bold">Concierge</span>
                  </button>
              </div>
            </nav>
          </>
        )}

        <AddStartupDialog
          open={isAddStartupDialogOpen}
          onOpenChange={setIsAddStartupDialogOpen}
          onAdd={handleAddStartup}
        />

        <AddIdeaDialog
          open={isAddIdeaDialogOpen}
          onOpenChange={setIsAddIdeaDialogOpen}
          onAdd={handleAddIdea}
        />
        
        {!isMobile && (
          <footer className="border-t border-white/10 bg-black/50 backdrop-blur-sm py-2 flex-shrink-0">
            <div className="container mx-auto px-4 flex items-center justify-between">
              <img src={logoVC} alt="Venture Clienting" className="h-4 opacity-90" />
              <p className="text-white/80 text-xs">AXA Venture Clienting ©</p>
            </div>
          </footer>
        )}
        
        <Toaster />
        <PWAUpdatePrompt />
      </div>
    </AuroralBackground>
  );
}

export default App
