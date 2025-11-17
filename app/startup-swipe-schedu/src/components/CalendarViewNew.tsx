import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { MapPin, Clock, Funnel, X } from '@phosphor-icons/react'
import { format } from 'date-fns'
import { CalendarEvent, EventLocation, EventCategory } from '@/lib/types'
import { Checkbox } from '@/components/ui/checkbox'

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
  { date: new Date(2025, 10, 19), label: 'Wed, Nov 19' },
  { date: new Date(2025, 10, 20), label: 'Thu, Nov 20' }
]

const LOCATION_COLORS: Record<EventLocation, { bg: string; text: string; dot: string; border: string }> = {
  'Founder stage': { bg: 'bg-purple-900/20 dark:bg-purple-900/40', text: 'text-purple-300', dot: 'bg-purple-500', border: 'border-purple-700/50' },
  'Impact stage': { bg: 'bg-emerald-900/20 dark:bg-emerald-900/40', text: 'text-emerald-300', dot: 'bg-emerald-500', border: 'border-emerald-700/50' },
  'Builder stage': { bg: 'bg-blue-900/20 dark:bg-blue-900/40', text: 'text-blue-300', dot: 'bg-blue-500', border: 'border-blue-700/50' },
  'Startup stage': { bg: 'bg-orange-900/20 dark:bg-orange-900/40', text: 'text-orange-300', dot: 'bg-orange-500', border: 'border-orange-700/50' },
  'Meeting': { bg: 'bg-slate-800/50 dark:bg-slate-800/70', text: 'text-slate-300', dot: 'bg-slate-500', border: 'border-slate-700/50' },
  'Venture clienting': { bg: 'bg-pink-900/20 dark:bg-pink-900/40', text: 'text-pink-300', dot: 'bg-pink-500', border: 'border-pink-700/50' }
}

const CATEGORY_COLORS: Record<EventCategory, string> = {
  'Agentic AI': 'bg-violet-900/30 text-violet-300 border-violet-700/50',
  'Agentic': 'bg-violet-900/30 text-violet-300 border-violet-700/50',
  'AI': 'bg-cyan-900/30 text-cyan-300 border-cyan-700/50',
  'Great speakers': 'bg-amber-900/30 text-amber-300 border-amber-700/50',
  'Venture': 'bg-green-900/30 text-green-300 border-green-700/50',
  'Health': 'bg-rose-900/30 text-rose-300 border-rose-700/50',
  'Software development': 'bg-sky-900/30 text-sky-300 border-sky-700/50',
  'DeepTech computing': 'bg-indigo-900/30 text-indigo-300 border-indigo-700/50',
  'Slush 100': 'bg-yellow-900/30 text-yellow-300 border-yellow-700/50'
}

export function CalendarView({ events, currentUserName, onToggleAttendance, onDeleteEvent }: CalendarViewProps) {
  const [selectedLocations, setSelectedLocations] = useState<Set<string>>(new Set())
  const [selectedCategories, setSelectedCategories] = useState<Set<string>>(new Set())
  const [showFilters, setShowFilters] = useState(false)
  const [selectedEvent, setSelectedEvent] = useState<CalendarEvent | null>(null)

  // Filter events for current day
  const getEventsForDay = (date: Date) => {
    return events.filter(event => {
      const eventDate = event.startTime instanceof Date ? event.startTime : new Date(event.startTime)
      return eventDate.getDate() === date.getDate() &&
             eventDate.getMonth() === date.getMonth() &&
             eventDate.getFullYear() === date.getFullYear()
    })
  }

  // Apply filters to events for a specific day
  const getFilteredEventsForDay = (date: Date) => {
    let filtered = getEventsForDay(date)
    
    if (selectedLocations.size > 0) {
      filtered = filtered.filter(e => e.location && selectedLocations.has(e.location))
    }
    
    if (selectedCategories.size > 0) {
      filtered = filtered.filter(e => e.category && selectedCategories.has(e.category))
    }
    
    // Sort by start time
    return filtered.sort((a, b) => {
      const aTime = a.startTime instanceof Date ? a.startTime.getTime() : new Date(a.startTime).getTime()
      const bTime = b.startTime instanceof Date ? b.startTime.getTime() : new Date(b.startTime).getTime()
      return aTime - bTime
    })
  }

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

  const clearFilters = () => {
    setSelectedLocations(new Set())
    setSelectedCategories(new Set())
  }

  const getLocationColor = (location?: string) => {
    return LOCATION_COLORS[location as EventLocation] || LOCATION_COLORS['Meeting']
  }

  const formatTime = (date: Date | string | number) => {
    const d = date instanceof Date ? date : new Date(date)
    return format(d, 'HH:mm')
  }

  const formatTimeRange = (start: Date | string | number, end: Date | string | number) => {
    return `${formatTime(start)} - ${formatTime(end)}`
  }

  return (
    <div className="h-full w-full overflow-hidden flex flex-col bg-gradient-to-br from-slate-50 to-slate-100">
      {/* Header */}
      <div className="flex-shrink-0 border-b bg-white/80 backdrop-blur-sm shadow-sm">
        <div className="max-w-full mx-auto px-4 py-4">
          <h1 className="text-2xl font-bold text-slate-900 mb-4">Event Schedule - Nov 19-20, 2025</h1>

          {/* Filter Bar */}
          <div className="flex items-center gap-2 flex-wrap">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowFilters(!showFilters)}
              className="gap-2"
            >
              <Funnel size={16} />
              Filters
              {(selectedLocations.size + selectedCategories.size) > 0 && (
                <Badge variant="secondary" className="ml-1">
                  {selectedLocations.size + selectedCategories.size}
                </Badge>
              )}
            </Button>
            
            {(selectedLocations.size + selectedCategories.size) > 0 && (
              <Button
                variant="ghost"
                size="sm"
                onClick={clearFilters}
                className="gap-1"
              >
                <X size={14} />
                Clear all
              </Button>
            )}
          </div>

          {/* Filter Panel */}
          {showFilters && (
            <Card className="mt-4">
              <CardContent className="pt-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Location Filters */}
                  <div>
                    <h3 className="font-semibold text-sm mb-3 text-slate-700">Stages</h3>
                    <div className="space-y-2">
                      {uniqueLocations.map(location => {
                        const colors = getLocationColor(location)
                        return (
                          <label key={location} className="flex items-center gap-2 cursor-pointer hover:bg-slate-50 p-2 rounded">
                            <Checkbox
                              checked={selectedLocations.has(location)}
                              onCheckedChange={() => toggleLocation(location)}
                            />
                            <div className={`w-3 h-3 rounded-full ${colors.dot}`} />
                            <span className="text-sm">{location}</span>
                          </label>
                        )
                      })}
                    </div>
                  </div>

                  {/* Category Filters */}
                  <div>
                    <h3 className="font-semibold text-sm mb-3 text-slate-700">Categories</h3>
                    <div className="space-y-2">
                      {uniqueCategories.map(category => (
                        <label key={category} className="flex items-center gap-2 cursor-pointer hover:bg-slate-50 p-2 rounded">
                          <Checkbox
                            checked={selectedCategories.has(category)}
                            onCheckedChange={() => toggleCategory(category)}
                          />
                          <span className="text-sm">{category}</span>
                        </label>
                      ))}
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>

      {/* Two-Day Event Grid */}
      <div className="flex-1 overflow-y-auto">
        <div className="max-w-full mx-auto px-4 py-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {SLUSH_DATES.map((dateInfo, dayIndex) => {
              const dayEvents = getFilteredEventsForDay(dateInfo.date)
              
              return (
                <div key={dayIndex} className="flex flex-col">
                  {/* Day Header */}
                  <div className="sticky top-0 z-10 bg-white rounded-t-lg border border-b-2 border-slate-200 px-6 py-4 mb-3 shadow-sm">
                    <h2 className="text-xl font-bold text-slate-900">{dateInfo.label}</h2>
                    <p className="text-sm text-slate-600">{dayEvents.length} events</p>
                  </div>
                  
                  {/* Day Events */}
                  <div className="space-y-3 flex-1">
                    {dayEvents.length === 0 ? (
                      <Card>
                        <CardContent className="py-12 text-center">
                          <p className="text-slate-500">
                            {selectedLocations.size + selectedCategories.size > 0 
                              ? 'No events match your filters'
                              : 'No events scheduled'}
                          </p>
                        </CardContent>
                      </Card>
                    ) : (
                      dayEvents.map(event => {
                        const colors = getLocationColor(event.location)
                        const isAttending = event.attendees?.includes(currentUserName)
                        
                        return (
                          <Card 
                            key={event.id}
                            className="hover:shadow-md transition-shadow cursor-pointer"
                            onClick={() => setSelectedEvent(event)}
                          >
                            <CardContent className="p-4">
                              <div className="flex items-start gap-3">
                                {/* Time */}
                                <div className="flex-shrink-0 w-16">
                                  <div className="flex items-center gap-1 text-sm font-semibold text-slate-900">
                                    <Clock size={14} className="text-slate-500" />
                                    {formatTime(event.startTime)}
                                  </div>
                                  <div className="text-xs text-slate-500 mt-0.5">
                                    {(() => {
                                      const start = event.startTime instanceof Date ? event.startTime : new Date(event.startTime)
                                      const end = event.endTime instanceof Date ? event.endTime : new Date(event.endTime)
                                      const duration = Math.round((end.getTime() - start.getTime()) / 60000)
                                      return `${duration} min`
                                    })()}
                                  </div>
                                </div>

                                {/* Stage Indicator */}
                                <div className="flex-shrink-0">
                                  <div className={`w-1 h-14 rounded-full ${colors.dot}`} />
                                </div>

                                {/* Content */}
                                <div className="flex-1 min-w-0">
                                  <h3 className="font-semibold text-slate-900 leading-tight mb-1 text-sm">
                                    {event.title}
                                  </h3>
                                  
                                  <div className="flex items-center gap-2 flex-wrap text-xs text-slate-600 mb-1">
                                    {event.location && (
                                      <div className="flex items-center gap-1">
                                        <MapPin size={12} className="text-slate-400" />
                                        <span className="truncate">{event.location}</span>
                                      </div>
                                    )}
                                    
                                    {event.category && (
                                      <Badge variant="outline" className={`text-xs ${CATEGORY_COLORS[event.category]}`}>
                                        {event.category}
                                      </Badge>
                                    )}
                                  </div>

                                  {event.description && (
                                    <p className="text-xs text-slate-600 line-clamp-1">
                                      {event.description}
                                    </p>
                                  )}
                                  
                                  {isAttending && (
                                    <Badge variant="default" className="mt-2 text-xs">
                                      Attending
                                    </Badge>
                                  )}
                                </div>
                              </div>
                            </CardContent>
                          </Card>
                        )
                      })
                    )}
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      </div>

      {/* Event Detail Modal */}
      {selectedEvent && (
        <div 
          className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
          onClick={() => setSelectedEvent(null)}
        >
          <Card 
            className="max-w-2xl w-full max-h-[90vh] overflow-y-auto"
            onClick={(e) => e.stopPropagation()}
          >
            <CardHeader>
              <CardTitle>{selectedEvent.title}</CardTitle>
              <div className="flex items-center gap-2 text-sm text-slate-600">
                <Clock size={16} />
                {formatTimeRange(selectedEvent.startTime, selectedEvent.endTime)}
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              {selectedEvent.description && (
                <p className="text-slate-700">{selectedEvent.description}</p>
              )}
              
              <div className="flex flex-wrap gap-2">
                {selectedEvent.location && (
                  <Badge variant="outline" className="gap-1">
                    <MapPin size={14} />
                    {selectedEvent.location}
                  </Badge>
                )}
                {selectedEvent.category && (
                  <Badge className={CATEGORY_COLORS[selectedEvent.category]}>
                    {selectedEvent.category}
                  </Badge>
                )}
              </div>

              {selectedEvent.attendees && selectedEvent.attendees.length > 0 && (
                <div>
                  <h4 className="font-semibold text-sm mb-2">Attendees ({selectedEvent.attendees.length})</h4>
                  <div className="flex flex-wrap gap-2">
                    {selectedEvent.attendees.map((attendee, idx) => (
                      <Badge key={idx} variant="secondary">{attendee}</Badge>
                    ))}
                  </div>
                </div>
              )}

              <div className="flex gap-2 pt-4">
                <Button
                  onClick={() => {
                    onToggleAttendance(selectedEvent.id)
                    setSelectedEvent(null)
                  }}
                  className="flex-1"
                >
                  {selectedEvent.attendees?.includes(currentUserName) ? 'Leave Event' : 'Attend Event'}
                </Button>
                <Button
                  variant="outline"
                  onClick={() => setSelectedEvent(null)}
                >
                  Close
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}
