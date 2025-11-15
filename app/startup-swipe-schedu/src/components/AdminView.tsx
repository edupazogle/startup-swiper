import { useMemo } from 'react'
import { Startup, Vote, CalendarEvent } from '@/lib/types'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { ScrollArea } from '@/components/ui/scroll-area'
import { 
  ChartBar, 
  ThumbsUp, 
  ThumbsDown, 
  Users, 
  TrendUp,
  CalendarBlank,
  Clock,
  Briefcase,
  Sparkle
} from '@phosphor-icons/react'

interface AdminViewProps {
  startups: Startup[]
  votes: Vote[]
  events: CalendarEvent[]
  currentUserId: string
}

export function AdminView({ startups, votes, events, currentUserId }: AdminViewProps) {
  const stats = useMemo(() => {
    const uniqueUsers = new Set(votes.map(v => v.userId))
    const interestedVotes = votes.filter(v => v.interested)
    const passedVotes = votes.filter(v => !v.interested)
    
    const userActivity = Array.from(uniqueUsers).map(userId => {
      const userVotes = votes.filter(v => v.userId === userId)
      const userName = userVotes[0]?.userName || 'Unknown'
      const interested = userVotes.filter(v => v.interested).length
      const passed = userVotes.filter(v => !v.interested).length
      const lastActivity = Math.max(...userVotes.map(v => v.timestamp))
      
      return {
        userId,
        userName,
        interested,
        passed,
        total: userVotes.length,
        lastActivity,
        interestRate: userVotes.length > 0 ? (interested / userVotes.length) * 100 : 0
      }
    })
    
    const startupStats = startups.map(startup => {
      const startupVotes = votes.filter(v => v.startupId === startup.id)
      const interested = startupVotes.filter(v => v.interested).length
      const passed = startupVotes.filter(v => !v.interested).length
      const scheduledMeeting = events.find(e => e.startupId === startup.id && e.confirmed)
      
      return {
        startup,
        interested,
        passed,
        total: startupVotes.length,
        interestRate: startupVotes.length > 0 ? (interested / startupVotes.length) * 100 : 0,
        hasScheduledMeeting: !!scheduledMeeting,
        meetingTime: scheduledMeeting?.startTime
      }
    })
    
    const recentActivity = [...votes]
      .sort((a, b) => b.timestamp - a.timestamp)
      .slice(0, 20)
      .map(vote => ({
        ...vote,
        startup: startups.find(s => s.id === vote.startupId)
      }))
    
    return {
      totalUsers: uniqueUsers.size,
      totalVotes: votes.length,
      totalInterested: interestedVotes.length,
      totalPassed: passedVotes.length,
      totalMeetings: events.filter(e => e.confirmed && e.startupId).length,
      overallInterestRate: votes.length > 0 ? (interestedVotes.length / votes.length) * 100 : 0,
      userActivity: userActivity.sort((a, b) => b.total - a.total),
      startupStats: startupStats.sort((a, b) => b.interested - a.interested),
      recentActivity
    }
  }, [startups, votes, events])

  const formatTimestamp = (timestamp: number) => {
    const date = new Date(timestamp)
    const now = new Date()
    const diff = now.getTime() - date.getTime()
    const minutes = Math.floor(diff / 60000)
    const hours = Math.floor(diff / 3600000)
    const days = Math.floor(diff / 86400000)
    
    if (minutes < 1) return 'Just now'
    if (minutes < 60) return `${minutes}m ago`
    if (hours < 24) return `${hours}h ago`
    return `${days}d ago`
  }

  const getInitials = (name: string) => {
    return name
      .split(' ')
      .map(n => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2)
  }

  return (
    <div className="h-full bg-background overflow-y-auto">
      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="mb-8">
          <h2 className="text-3xl font-bold mb-2 flex items-center gap-3">
            <ChartBar size={32} weight="duotone" className="text-primary" />
            Admin Dashboard
          </h2>
          <p className="text-muted-foreground">
            Overview of all user activity and swipe statistics
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Active Users
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center">
                  <Users size={24} weight="duotone" className="text-primary" />
                </div>
                <div>
                  <div className="text-3xl font-bold">{stats.totalUsers}</div>
                  <p className="text-xs text-muted-foreground">Team members</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Total Swipes
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 rounded-xl bg-accent/10 flex items-center justify-center">
                  <Sparkle size={24} weight="duotone" className="text-accent" />
                </div>
                <div>
                  <div className="text-3xl font-bold">{stats.totalVotes}</div>
                  <p className="text-xs text-muted-foreground">All interactions</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Interest Rate
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 rounded-xl bg-secondary/10 flex items-center justify-center">
                  <TrendUp size={24} weight="duotone" className="text-secondary" />
                </div>
                <div>
                  <div className="text-3xl font-bold">{stats.overallInterestRate.toFixed(0)}%</div>
                  <p className="text-xs text-muted-foreground">
                    {stats.totalInterested} interested
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Meetings Scheduled
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center">
                  <CalendarBlank size={24} weight="duotone" className="text-primary" />
                </div>
                <div>
                  <div className="text-3xl font-bold">{stats.totalMeetings}</div>
                  <p className="text-xs text-muted-foreground">Confirmed events</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Users size={20} weight="duotone" />
                User Activity
              </CardTitle>
              <CardDescription>
                Swipe statistics per team member
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ScrollArea className="h-[400px] pr-4">
                <div className="space-y-4">
                  {stats.userActivity.map((user) => (
                    <div key={user.userId} className="space-y-2">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <Avatar className="w-10 h-10 bg-primary/10">
                            <AvatarFallback className="bg-primary/10 text-primary font-semibold">
                              {getInitials(user.userName)}
                            </AvatarFallback>
                          </Avatar>
                          <div>
                            <div className="font-semibold">
                              {user.userName}
                              {user.userId === currentUserId && (
                                <Badge variant="outline" className="ml-2 text-xs">
                                  You
                                </Badge>
                              )}
                            </div>
                            <div className="text-xs text-muted-foreground flex items-center gap-1">
                              <Clock size={12} weight="duotone" />
                              {formatTimestamp(user.lastActivity)}
                            </div>
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="text-sm font-semibold text-primary">
                            {user.interestRate.toFixed(0)}% interest
                          </div>
                          <div className="text-xs text-muted-foreground">
                            {user.total} total
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <div className="flex-1 h-2 bg-muted rounded-full overflow-hidden">
                          <div 
                            className="h-full bg-primary rounded-full transition-all"
                            style={{ width: `${user.interestRate}%` }}
                          />
                        </div>
                        <div className="flex items-center gap-3 text-xs">
                          <div className="flex items-center gap-1 text-green-600">
                            <ThumbsUp size={14} weight="fill" />
                            {user.interested}
                          </div>
                          <div className="flex items-center gap-1 text-muted-foreground">
                            <ThumbsDown size={14} weight="fill" />
                            {user.passed}
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </ScrollArea>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Briefcase size={20} weight="duotone" />
                Startup Performance
              </CardTitle>
              <CardDescription>
                Interest levels for each startup
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ScrollArea className="h-[400px] pr-4">
                <div className="space-y-4">
                  {stats.startupStats.map(({ startup, interested, passed, total, interestRate, hasScheduledMeeting, meetingTime }) => (
                    <div key={startup.id} className="space-y-2">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="font-semibold flex items-center gap-2">
                            {startup["Company Name"]}
                            {hasScheduledMeeting && (
                              <Badge className="text-xs gap-1">
                                <CalendarBlank size={12} weight="fill" />
                                Scheduled
                              </Badge>
                            )}
                          </div>
                          <div className="text-xs text-muted-foreground mt-1">
                            {startup["Category"]} • {startup["Stage"]}
                          </div>
                          {meetingTime && (
                            <div className="text-xs text-primary mt-1 flex items-center gap-1">
                              <Clock size={12} weight="duotone" />
                              {new Date(meetingTime).toLocaleDateString('en-US', { 
                                month: 'short', 
                                day: 'numeric',
                                hour: 'numeric',
                                minute: '2-digit'
                              })}
                            </div>
                          )}
                        </div>
                        <div className="text-right">
                          <div className="text-sm font-semibold text-primary">
                            {total > 0 ? `${interestRate.toFixed(0)}%` : 'No votes'}
                          </div>
                          <div className="text-xs text-muted-foreground">
                            {total} {total === 1 ? 'vote' : 'votes'}
                          </div>
                        </div>
                      </div>
                      {total > 0 && (
                        <div className="flex items-center gap-2">
                          <div className="flex-1 h-2 bg-muted rounded-full overflow-hidden">
                            <div 
                              className="h-full bg-gradient-to-r from-primary to-secondary rounded-full transition-all"
                              style={{ width: `${interestRate}%` }}
                            />
                          </div>
                          <div className="flex items-center gap-3 text-xs">
                            <div className="flex items-center gap-1 text-green-600">
                              <ThumbsUp size={14} weight="fill" />
                              {interested}
                            </div>
                            <div className="flex items-center gap-1 text-muted-foreground">
                              <ThumbsDown size={14} weight="fill" />
                              {passed}
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </ScrollArea>
            </CardContent>
          </Card>
        </div>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Clock size={20} weight="duotone" />
              Recent Activity
            </CardTitle>
            <CardDescription>
              Live feed of all swipe activity
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ScrollArea className="h-[300px] pr-4">
              <div className="space-y-3">
                {stats.recentActivity.map((activity, index) => (
                  <div key={`${activity.startupId}-${activity.userId}-${activity.timestamp}`}>
                    <div className="flex items-start gap-3">
                      <Avatar className="w-8 h-8 bg-muted">
                        <AvatarFallback className="bg-muted text-muted-foreground text-xs">
                          {getInitials(activity.userName)}
                        </AvatarFallback>
                      </Avatar>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 flex-wrap">
                          <span className="font-medium">{activity.userName}</span>
                          {activity.interested ? (
                            <>
                              <ThumbsUp size={14} weight="fill" className="text-green-600 shrink-0" />
                              <span className="text-sm text-muted-foreground">interested in</span>
                            </>
                          ) : (
                            <>
                              <ThumbsDown size={14} weight="fill" className="text-muted-foreground shrink-0" />
                              <span className="text-sm text-muted-foreground">passed on</span>
                            </>
                          )}
                          <span className="font-medium text-primary">
                            {activity.startup?.["Company Name"] || 'Unknown Startup'}
                          </span>
                        </div>
                        <div className="text-xs text-muted-foreground mt-1">
                          {formatTimestamp(activity.timestamp)}
                        </div>
                      </div>
                    </div>
                    {index < stats.recentActivity.length - 1 && (
                      <Separator className="mt-3" />
                    )}
                  </div>
                ))}
                {stats.recentActivity.length === 0 && (
                  <div className="text-center py-8 text-muted-foreground">
                    No activity yet
                  </div>
                )}
              </div>
            </ScrollArea>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
