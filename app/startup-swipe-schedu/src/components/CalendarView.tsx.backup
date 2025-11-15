import { useState, useRef } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Textarea } from '@/components/ui/textarea'
import { Plus, MapPin, Users as UsersIcon, Trash, Check, CaretLeft, CaretRight, Funnel } from '@phosphor-icons/react'
import { format } from 'date-fns'
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { CalendarEvent, EventLocation, EventCategory } from '@/lib/types'
import { toast } from 'sonner'
import { useIsMobile } from '@/hooks/use-mobile'

interface CalendarViewProps {
  currentUserId: string
  currentUserName: string
  events: CalendarEvent[]
  onAddEvent: (event: Omit<CalendarEvent, 'id' | 'attendees'>) => void
  onDeleteEvent: (eventId: string) => void
  onToggleAttendance: (eventId: string) => void
  onNavigateToLinkedIn?: () => void
}

const SLUSH_DATES = [
  { date: new Date(2025, 10, 19), label: 'Wednesday, Nov 19' },
  { date: new Date(2025, 10, 20), label: 'Thursday, Nov 20' }
]

const TIME_SLOTS = Array.from({ length: 14 }, (_, i) => 9 + i)
const TOTAL_HOURS = 14

const LOCATION_COLORS: Record<EventLocation, { bg: string; border: string; text: string; dot: string; legend: string }> = {
  'Founder stage': { 
    bg: 'bg-purple-100/80 backdrop-blur-sm', 
    border: 'border-l-[6px] border-l-purple-600', 
    text: 'text-purple-950',
    dot: 'bg-purple-600',
    legend: 'Founder stage'
  },
  'Impact stage': { 
    bg: 'bg-emerald-100/80 backdrop-blur-sm', 
    border: 'border-l-[6px] border-l-emerald-600', 
    text: 'text-emerald-950',
    dot: 'bg-emerald-600',
    legend: 'Impact stage'
  },
  'Builder stage': { 
    bg: 'bg-blue-100/80 backdrop-blur-sm', 
    border: 'border-l-[6px] border-l-blue-600', 
    text: 'text-blue-950',
    dot: 'bg-blue-600',
    legend: 'Builder stage'
  },
  'Startup stage': { 
    bg: 'bg-orange-100/80 backdrop-blur-sm', 
    border: 'border-l-[6px] border-l-orange-600', 
    text: 'text-orange-950',
    dot: 'bg-orange-600',
    legend: 'Startup stage'
  },
  'Meeting': { 
    bg: 'bg-slate-100/80 backdrop-blur-sm', 
    border: 'border-l-[6px] border-l-slate-600', 
    text: 'text-slate-950',
    dot: 'bg-slate-600',
    legend: 'Meeting'
  },
  'Venture clienting': { 
    bg: 'bg-pink-100/80 backdrop-blur-sm', 
    border: 'border-l-[6px] border-l-pink-600', 
    text: 'text-pink-950',
    dot: 'bg-pink-600',
    legend: 'Venture clienting'
  }
}

const CATEGORY_COLORS: Record<EventCategory, string> = {
  'Agentic AI': 'bg-violet-200/90 text-violet-950 border-violet-300',
  'Agentic': 'bg-violet-200/90 text-violet-950 border-violet-300',
  'AI': 'bg-cyan-200/90 text-cyan-950 border-cyan-300',
  'Great speakers': 'bg-amber-200/90 text-amber-950 border-amber-300',
  'Venture': 'bg-green-200/90 text-green-950 border-green-300',
  'Health': 'bg-rose-200/90 text-rose-950 border-rose-300',
  'Software development': 'bg-sky-200/90 text-sky-950 border-sky-300',
  'DeepTech computing': 'bg-indigo-200/90 text-indigo-950 border-indigo-300',
  'Slush 100': 'bg-yellow-200/90 text-yellow-950 border-yellow-300'
}

const getLocationColor = (location?: string) => {
  return LOCATION_COLORS[location as EventLocation] || LOCATION_COLORS['Meeting']
}

const getInitials = (name: string) => {
  const parts = name.split(' ')
  return parts.length > 1 ? `${parts[0][0]}${parts[1][0]}` : parts[0][0]
}

export function CalendarView({ currentUserId, currentUserName, events, onAddEvent, onDeleteEvent, onToggleAttendance, onNavigateToLinkedIn }: CalendarViewProps) {
  const isMobile = useIsMobile()
  const [currentDayIndex, setCurrentDayIndex] = useState(0)
  const touchStartX = useRef(0)
  const touchEndX = useRef(0)
  const [selectedLocations, setSelectedLocations] = useState<Set<string>>(new Set())
  const [selectedCategories, setSelectedCategories] = useState<Set<string>>(new Set())
  const [showFilters, setShowFilters] = useState(false)
  const [isDialogOpen, setIsDialogOpen] = useState(false)
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    startTime: '',
    endTime: '',
    location: '' as EventLocation | '',
    category: '' as EventCategory | '',
    type: 'meeting' as 'meeting' | 'presentation'
  })

  const handleTouchStart = (e: React.TouchEvent) => {
    touchStartX.current = e.touches[0].clientX
  }

  const handleTouchMove = (e: React.TouchEvent) => {
    touchEndX.current = e.touches[0].clientX
  }

  const handleTouchEnd = () => {
    const diff = touchStartX.current - touchEndX.current
    const threshold = 50

    if (Math.abs(diff) > threshold) {
      if (diff > 0 && currentDayIndex < SLUSH_DATES.length - 1) {
        setCurrentDayIndex(currentDayIndex + 1)
      } else if (diff < 0 && currentDayIndex > 0) {
        setCurrentDayIndex(currentDayIndex - 1)
      }
    }
  }

  const goToPreviousDay = () => {
    if (currentDayIndex > 0) {
      setCurrentDayIndex(currentDayIndex - 1)
    }
  }

  const goToNextDay = () => {
    if (currentDayIndex < SLUSH_DATES.length - 1) {
      setCurrentDayIndex(currentDayIndex + 1)
    }
  }

  const handleAddEvent = () => {
    if (!formData.title || !formData.startTime || !formData.endTime) {
      toast.error('Please fill in all required fields')
      return
    }

    const startDate = new Date(formData.startTime)
    const endDate = new Date(formData.endTime)
    
    if (isNaN(startDate.getTime()) || isNaN(endDate.getTime())) {
      toast.error('Invalid date format')
      return
    }

    if (endDate <= startDate) {
      toast.error('End time must be after start time')
      return
    }

    onAddEvent({
      title: formData.title,
      description: formData.description,
      startTime: startDate,
      endTime: endDate,
      location: formData.location || undefined,
      category: formData.category || undefined,
      type: formData.type
    })

    setFormData({
      title: '',
      description: '',
      startTime: '',
      endTime: '',
      location: '',
      category: '',
      type: 'meeting'
    })
    setIsDialogOpen(false)
  }

  const handleDeleteEvent = (eventId: string) => {
    const event = (events || []).find(e => e.id === eventId)
    if (event?.isFixed) {
      toast.error('This is a fixed event and cannot be deleted')
      return
    }
    onDeleteEvent(eventId)
    toast.success('Event deleted')
  }

  const handleToggleAttendance = (eventId: string) => {
    const event = (events || []).find(e => e.id === eventId)
    if (event?.isFixed) {
      toast.error('This is a fixed event and cannot be modified')
      return
    }
    const wasAttending = event?.attendees.includes(currentUserName)
    
    onToggleAttendance(eventId)
    toast.success(wasAttending ? 'Removed from calendar' : 'Added to your calendar!')
  }

  const handleEventClick = (event: CalendarEvent) => {
    if (event.link) {
      if (event.link === '/linkedin' && onNavigateToLinkedIn) {
        onNavigateToLinkedIn()
      } else if (event.link.startsWith('http')) {
        window.open(event.link, '_blank')
      }
    }
  }

  const getEventsForDay = (date: Date) => {
    let filteredEvents = (events || []).filter(event => {
      let eventStartTime: Date
      
      if (event.startTime instanceof Date) {
        eventStartTime = event.startTime
      } else if (typeof event.startTime === 'string' || typeof event.startTime === 'number') {
        eventStartTime = new Date(event.startTime)
      } else {
        return false
      }
      
      if (isNaN(eventStartTime.getTime())) {
        return false
      }
      
      const isSameDay = eventStartTime.getFullYear() === date.getFullYear() &&
                        eventStartTime.getMonth() === date.getMonth() &&
                        eventStartTime.getDate() === date.getDate()
      
      return isSameDay
    })

    if (selectedLocations.size > 0) {
      filteredEvents = filteredEvents.filter(e => e.location && selectedLocations.has(e.location))
    }

    if (selectedCategories.size > 0) {
      filteredEvents = filteredEvents.filter(e => e.category && selectedCategories.has(e.category))
    }
    
    return filteredEvents
  }

  const getEventPosition = (event: CalendarEvent, column: number, totalColumns: number) => {
    let startDate: Date
    let endDate: Date
    
    if (event.startTime instanceof Date) {
      startDate = event.startTime
    } else {
      startDate = new Date(event.startTime)
    }
    
    if (event.endTime instanceof Date) {
      endDate = event.endTime
    } else {
      endDate = new Date(event.endTime)
    }
    
    const startHour = startDate.getHours() + startDate.getMinutes() / 60
    const endHour = endDate.getHours() + endDate.getMinutes() / 60
    
    const top = ((startHour - 9) / TOTAL_HOURS) * 100
    const height = ((endHour - startHour) / TOTAL_HOURS) * 100
    
    // Better overlap handling with proper spacing
    // Minimum height should accommodate: title + location + category badge
    const minHeightPercent = isMobile ? 8 : 10 // Larger minimum for readability
    
    if (totalColumns > 1) {
      const columnWidth = 100 / totalColumns
      const gapPercentage = 1.5 // Gap between columns
      const width = columnWidth - gapPercentage
      const left = (column * columnWidth) + (gapPercentage / 2)
      
      return { 
        top: `${top}%`, 
        height: `${Math.max(height, minHeightPercent)}%`,
        width: `${width}%`,
        left: `${left}%`,
        zIndex: 1
      }
    } else {
      return { 
        top: `${top}%`, 
        height: `${Math.max(height, minHeightPercent)}%`,
        width: '99%',
        left: '0.5%',
        zIndex: 1
      }
    }
  }

  const getOverlappingGroups = (dayEvents: CalendarEvent[]) => {
    const sorted = [...dayEvents].sort((a, b) => {
      const aTime = a.startTime instanceof Date ? a.startTime.getTime() : new Date(a.startTime).getTime()
      const bTime = b.startTime instanceof Date ? b.startTime.getTime() : new Date(b.startTime).getTime()
      return aTime - bTime
    })
    
    const columns: CalendarEvent[][] = []
    
    sorted.forEach(event => {
      const eventStart = event.startTime instanceof Date ? event.startTime.getTime() : new Date(event.startTime).getTime()
      const eventEnd = event.endTime instanceof Date ? event.endTime.getTime() : new Date(event.endTime).getTime()
      
      let placed = false
      
      for (let i = 0; i < columns.length; i++) {
        const column = columns[i]
        const lastEventInColumn = column[column.length - 1]
        const lastEventEnd = lastEventInColumn.endTime instanceof Date 
          ? lastEventInColumn.endTime.getTime() 
          : new Date(lastEventInColumn.endTime).getTime()
        
        if (eventStart >= lastEventEnd) {
          column.push(event)
          placed = true
          break
        }
      }
      
      if (!placed) {
        columns.push([event])
      }
    })
    
    const eventColumnMap = new Map<string, { column: number; totalColumns: number }>()
    
    sorted.forEach(event => {
      const eventStart = event.startTime instanceof Date ? event.startTime.getTime() : new Date(event.startTime).getTime()
      const eventEnd = event.endTime instanceof Date ? event.endTime.getTime() : new Date(event.endTime).getTime()
      
      let column = -1
      for (let i = 0; i < columns.length; i++) {
        if (columns[i].includes(event)) {
          column = i
          break
        }
      }
      
      const overlappingEvents = sorted.filter(e => {
        const eStart = e.startTime instanceof Date ? e.startTime.getTime() : new Date(e.startTime).getTime()
        const eEnd = e.endTime instanceof Date ? e.endTime.getTime() : new Date(e.endTime).getTime()
        return (eventStart < eEnd && eventEnd > eStart)
      })
      
      const totalColumns = Math.max(...overlappingEvents.map(e => {
        for (let i = 0; i < columns.length; i++) {
          if (columns[i].includes(e)) return i + 1
        }
        return 1
      }))
      
      eventColumnMap.set(event.id, { column: Math.max(0, column), totalColumns })
    })
    
    return eventColumnMap
  }

  const FilterSection = () => {
    const uniqueLocations = Array.from(new Set(events.map(e => e.location).filter(Boolean))) as string[]
    const uniqueCategories = Array.from(new Set(events.map(e => e.category).filter(Boolean))) as string[]

    const toggleLocation = (location: string) => {
      setSelectedLocations(prev => {
        const newSet = new Set(prev)
        if (newSet.has(location)) {
          newSet.delete(location)
        } else {
          newSet.add(location)
        }
        return newSet
      })
    }

    const toggleCategory = (category: string) => {
      setSelectedCategories(prev => {
        const newSet = new Set(prev)
        if (newSet.has(category)) {
          newSet.delete(category)
        } else {
          newSet.add(category)
        }
        return newSet
      })
    }

    return (
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <span className="text-xs font-semibold text-slate-700">Active Filters</span>
          {(selectedLocations.size > 0 || selectedCategories.size > 0) && (
            <Button
              variant="ghost"
              size="sm"
              onClick={() => {
                setSelectedLocations(new Set())
                setSelectedCategories(new Set())
              }}
              className="h-6 text-xs px-2"
            >
              Clear All
            </Button>
          )}
        </div>
        
        {uniqueLocations.length > 0 && (
          <div>
            <p className="text-xs font-semibold text-slate-600 mb-1.5">Locations</p>
            <div className="flex flex-wrap gap-1.5">
              {uniqueLocations.map(location => (
                <Badge
                  key={location}
                  variant={selectedLocations.has(location) ? 'default' : 'outline'}
                  className="cursor-pointer text-xs"
                  onClick={() => toggleLocation(location)}
                >
                  {location}
                </Badge>
              ))}
            </div>
          </div>
        )}

        {uniqueCategories.length > 0 && (
          <div>
            <p className="text-xs font-semibold text-slate-600 mb-1.5">Categories</p>
            <div className="flex flex-wrap gap-1.5">
              {uniqueCategories.map(category => (
                <Badge
                  key={category}
                  variant={selectedCategories.has(category) ? 'default' : 'outline'}
                  className="cursor-pointer text-xs"
                  onClick={() => toggleCategory(category)}
                >
                  {category}
                </Badge>
              ))}
            </div>
          </div>
        )}
      </div>
    )
  }

  const selectedDate = SLUSH_DATES[currentDayIndex].date

  // Separate predefined events from user meetings
  const getPredefinedEvents = (date: Date) => {
    return getEventsForDay(date).filter(event => event.isFixed)
  }

  const getUserMeetings = (date: Date) => {
    return getEventsForDay(date).filter(event => !event.isFixed)
  }

  const predefinedEvents = getPredefinedEvents(selectedDate)
  const userMeetings = getUserMeetings(selectedDate)

  return (
    <div className="h-full bg-background overflow-y-auto">
      <div className="max-w-[1600px] mx-auto px-3 md:px-6 py-4 md:py-8">
        <div className="flex flex-col gap-4 md:gap-6">
          {/* Header */}
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 md:gap-0">
            <div>
              <h2 className="text-2xl md:text-3xl font-bold">Slush Schedule</h2>
              <p className="text-xs md:text-base text-muted-foreground mt-1">Nov 19-20, 2025 · 9:00 AM - 10:00 PM</p>
            </div>
            <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
              <DialogTrigger asChild>
                <Button className="gap-2 w-full md:w-auto">
                  <Plus size={18} weight="bold" className="md:w-5 md:h-5" />
                  Add Event
                </Button>
              </DialogTrigger>
              <DialogContent className="sm:max-w-[500px]">
                <DialogHeader>
                  <DialogTitle>Add Event</DialogTitle>
                  <DialogDescription>
                    Create a new meeting or presentation for your Slush schedule
                  </DialogDescription>
                </DialogHeader>
                <div className="grid gap-4 py-4">
                  <div className="grid gap-2">
                    <Label htmlFor="title">Title *</Label>
                    <Input
                      id="title"
                      placeholder="Meeting with Startup X"
                      value={formData.title}
                      onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                    />
                  </div>
                  <div className="grid gap-2">
                    <Label htmlFor="type">Type *</Label>
                    <Select
                      value={formData.type}
                      onValueChange={(value: 'meeting' | 'presentation') =>
                        setFormData({ ...formData, type: value })
                      }
                    >
                      <SelectTrigger id="type">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="meeting">Meeting</SelectItem>
                        <SelectItem value="presentation">Presentation</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
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
                    <Select
                      value={formData.location}
                      onValueChange={(value: EventLocation | '') =>
                        setFormData({ ...formData, location: value })
                      }
                    >
                      <SelectTrigger id="location">
                        <SelectValue placeholder="Select location" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="Founder stage">Founder stage</SelectItem>
                        <SelectItem value="Impact stage">Impact stage</SelectItem>
                        <SelectItem value="Builder stage">Builder stage</SelectItem>
                        <SelectItem value="Startup stage">Startup stage</SelectItem>
                        <SelectItem value="Meeting">Meeting</SelectItem>
                        <SelectItem value="Venture clienting">Venture clienting</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="grid gap-2">
                    <Label htmlFor="category">Category</Label>
                    <Select
                      value={formData.category}
                      onValueChange={(value: EventCategory | '') =>
                        setFormData({ ...formData, category: value })
                      }
                    >
                      <SelectTrigger id="category">
                        <SelectValue placeholder="Select category" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="Agentic AI">Agentic AI</SelectItem>
                        <SelectItem value="AI">AI</SelectItem>
                        <SelectItem value="Great speakers">Great speakers</SelectItem>
                        <SelectItem value="Venture">Venture</SelectItem>
                        <SelectItem value="Health">Health</SelectItem>
                        <SelectItem value="Software development">Software development</SelectItem>
                        <SelectItem value="DeepTech computing">DeepTech computing</SelectItem>
                        <SelectItem value="Slush 100">Slush 100</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="grid gap-2">
                    <Label htmlFor="description">Description</Label>
                    <Textarea
                      id="description"
                      placeholder="Add notes about this event..."
                      value={formData.description}
                      onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                      rows={3}
                    />
                  </div>
                </div>
                <DialogFooter>
                  <Button variant="outline" onClick={() => setIsDialogOpen(false)}>
                    Cancel
                  </Button>
                  <Button onClick={handleAddEvent}>Add Event</Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>
          </div>

          {/* Day Selection Tabs */}
          <div className="flex items-center gap-2 border-b-2 border-border">
            {SLUSH_DATES.map((dateInfo, index) => (
              <button
                key={index}
                onClick={() => setCurrentDayIndex(index)}
                className={`px-4 md:px-6 py-3 text-sm md:text-base font-semibold transition-colors relative ${
                  currentDayIndex === index
                    ? 'text-primary'
                    : 'text-muted-foreground hover:text-foreground'
                }`}
              >
                {dateInfo.label}
                {currentDayIndex === index && (
                  <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary" />
                )}
              </button>
            ))}
          </div>

          {/* Minimized Filter Section */}
          <div className="bg-white/80 backdrop-blur-sm rounded-lg border border-border overflow-hidden">
            <button
              onClick={() => setShowFilters(!showFilters)}
              className="w-full flex items-center justify-between p-2.5 hover:bg-slate-50 transition-colors"
            >
              <div className="flex items-center gap-2">
                <Funnel size={16} weight="duotone" className="text-slate-600" />
                <span className="text-xs font-semibold text-slate-700">Filters</span>
                {(selectedLocations.size > 0 || selectedCategories.size > 0) && (
                  <Badge variant="secondary" className="text-xs h-5">
                    {selectedLocations.size + selectedCategories.size}
                  </Badge>
                )}
              </div>
              <CaretRight
                size={14}
                weight="bold"
                className={`text-slate-600 transition-transform ${showFilters ? 'rotate-90' : ''}`}
              />
            </button>
            {showFilters && (
              <div className="p-3 border-t border-border bg-white">
                <FilterSection />
              </div>
            )}
          </div>

          {/* Unified Time-Scale Calendar - Full Width */}
          <div className="bg-white/90 backdrop-blur-sm rounded-lg border-2 border-border overflow-hidden">
            <div className="grid grid-cols-[50px_1fr] md:grid-cols-[70px_1fr]">
              {/* Time Scale */}
              <div className="border-r-2 border-border bg-slate-50/50">
                <div className="h-12 border-b-2 border-border" />
                {TIME_SLOTS.map(hour => (
                  <div key={hour} className="h-20 md:h-24 flex items-start justify-end pr-1.5 md:pr-2 pt-1 text-[9px] md:text-xs font-semibold text-slate-600 border-b-2 border-border">
                    {hour === 12 ? '12p' : hour > 12 ? `${hour - 12}p` : `${hour}a`}
                  </div>
                ))}
              </div>

              {/* Event Agenda Column - Full Width */}
              <div>
                <div className="h-12 border-b-2 border-border bg-purple-50/80 flex items-center justify-center px-2">
                  <div className="text-center">
                    <h3 className="font-bold text-xs md:text-sm text-purple-900">Event Agenda</h3>
                    <p className="text-[9px] md:text-xs text-purple-700">{predefinedEvents.length} events</p>
                  </div>
                </div>
                <div className="relative" style={{ height: `${TOTAL_HOURS * (isMobile ? 80 : 96)}px` }}>
                  {TIME_SLOTS.map(hour => (
                    <div key={hour} className="h-20 md:h-24 border-b-2 border-border" />
                  ))}

                  {predefinedEvents.length === 0 ? (
                    <div className="absolute inset-0 flex items-center justify-center">
                      <p className="text-xs text-muted-foreground text-center px-2">No events</p>
                    </div>
                  ) : (
                    (() => {
                      const overlaps = getOverlappingGroups(predefinedEvents)
                      return predefinedEvents.map(event => {
                        const overlap = overlaps.get(event.id) || { column: 0, totalColumns: 1 }
                        const position = getEventPosition(event, overlap.column, overlap.totalColumns)
                        const locationColors = getLocationColor(event.location)
                        const startTime = event.startTime instanceof Date ? event.startTime : new Date(event.startTime)
                        const endTime = event.endTime instanceof Date ? event.endTime : new Date(event.endTime)

                        return (
                          <Popover key={event.id}>
                            <PopoverTrigger asChild>
                              <div className="absolute cursor-pointer px-0" style={position}>
                                <Card
                                  onClick={() => handleEventClick(event)}
                                  className={`h-full min-h-[60px] md:min-h-[70px] ${locationColors.bg} ${locationColors.border} border-2 hover:shadow-lg hover:z-20 transition-all ${event.highlight ? 'ring-2 ring-yellow-400' : ''}`}
                                >
                                  <CardContent className="p-1.5 md:p-2 h-full flex flex-col justify-between overflow-hidden">
                                    <div className="flex-1 min-h-0">
                                      <p className={`font-bold text-[10px] md:text-xs leading-tight ${locationColors.text} line-clamp-1 mb-0.5`}>
                                        {event.title}
                                      </p>
                                      {event.location && (
                                        <div className="flex items-center gap-0.5">
                                          <MapPin size={8} weight="fill" className={`flex-shrink-0 ${locationColors.text}`} />
                                          <span className={`text-[7px] md:text-[9px] ${locationColors.text} font-medium truncate`}>
                                            {event.location}
                                          </span>
                                        </div>
                                      )}
                                    </div>
                                    {event.category && (
                                      <Badge className={`text-[7px] md:text-[8px] px-1 py-0 h-auto truncate w-fit ${CATEGORY_COLORS[event.category]}`}>
                                        {event.category}
                                      </Badge>
                                    )}
                                  </CardContent>
                                </Card>
                              </div>
                            </PopoverTrigger>
                            <PopoverContent className="w-80" align="start">
                              <div className="space-y-3">
                                <div>
                                  <h4 className="font-bold text-slate-900">{event.title}</h4>
                                  <p className="text-sm text-slate-600 mt-1">
                                    {format(startTime, 'PPp')} - {format(endTime, 'p')}
                                  </p>
                                </div>
                                {event.description && <p className="text-sm text-slate-700">{event.description}</p>}
                                <div className="flex flex-wrap gap-2">
                                  {event.category && (
                                    <Badge className={`${CATEGORY_COLORS[event.category]}`}>{event.category}</Badge>
                                  )}
                                  {event.location && (
                                    <Badge variant="outline" className="gap-1">
                                      <MapPin size={12} weight="fill" />
                                      {event.location}
                                    </Badge>
                                  )}
                                </div>
                              </div>
                            </PopoverContent>
                          </Popover>
                        )
                      })
                    })()
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Location Legend - Below Event Agenda */}
          <div className="bg-white/70 backdrop-blur-sm rounded-lg border border-border overflow-hidden">
            <div className="p-2.5">
              <div className="flex items-center gap-1.5 mb-2">
                <MapPin size={14} weight="duotone" className="text-slate-600" />
                <h4 className="font-semibold text-xs text-slate-700">Location Legend</h4>
              </div>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-1.5">
                {Array.from(new Set(events.map(e => e.location).filter(Boolean))).map(location => {
                  const colors = getLocationColor(location as EventLocation)
                  return (
                    <div key={location} className="flex items-center gap-1.5">
                      <div className={`w-2 h-2 rounded-full ${colors.dot}`} />
                      <span className="text-[10px] font-medium text-slate-600">{location}</span>
                    </div>
                  )
                })}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
