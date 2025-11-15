import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Startup, Vote } from '@/lib/types'
import { Heart, X, ArrowCounterClockwise } from '@phosphor-icons/react'

interface HistoryViewProps {
  startups: Startup[]
  votes: Vote[]
  currentUserId: string
  onChangeVote: (startupId: string, interested: boolean) => void
}

export function HistoryView({ startups, votes, currentUserId, onChangeVote }: HistoryViewProps) {
  const myVotes = votes
    .filter(v => v.userId === currentUserId)
    .sort((a, b) => b.timestamp - a.timestamp)

  const getStartup = (startupId: string) => startups.find(s => s.id === startupId)

  if (myVotes.length === 0) {
    return (
      <div className="h-full flex items-center justify-center p-4 md:p-8">
        <div className="text-center max-w-md">
          <ArrowCounterClockwise size={48} className="md:w-16 md:h-16 text-muted-foreground mx-auto mb-3 md:mb-4" />
          <h2 className="text-xl md:text-2xl font-semibold mb-2 md:mb-3">No History Yet</h2>
          <p className="text-sm md:text-base text-muted-foreground leading-relaxed">
            Start swiping on startups to build your voting history.
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="h-full">
      <div className="max-w-3xl mx-auto p-3 md:p-6">
        <div className="mb-4 md:mb-6">
          <h2 className="text-xl md:text-2xl font-semibold mb-1 md:mb-2">Your Voting History</h2>
          <p className="text-sm md:text-base text-muted-foreground">
            Review and change your votes on startups
          </p>
        </div>

        <div className="space-y-2 md:space-y-3">
            {myVotes.map((vote) => {
              const startup = getStartup(vote.startupId)
              if (!startup) return null

              return (
                <Card key={vote.startupId} className="p-4 md:p-5">
                  <div className="flex items-start gap-3 md:gap-4">
                    {startup.logo && (
                      <div className="w-10 h-10 md:w-12 md:h-12 rounded-lg bg-background flex items-center justify-center overflow-hidden flex-shrink-0">
                        <img src={startup.logo} alt={startup["Company Name"]} className="w-full h-full object-cover" />
                      </div>
                    )}
                    
                    <div className="flex-1 min-w-0">
                      <div className="flex items-start justify-between gap-2 md:gap-3 mb-2">
                        <div className="flex-1 min-w-0">
                          <h3 className="text-base md:text-lg font-semibold mb-1">{startup["Company Name"]}</h3>
                          <div className="flex flex-wrap gap-1 md:gap-2">
                            <Badge variant="secondary" className="text-[10px] md:text-xs">
                              {startup["Category"]}
                            </Badge>
                            <Badge variant="outline" className="text-[10px] md:text-xs">
                              {startup["Stage"]}
                            </Badge>
                          </div>
                        </div>
                        
                        <div className="flex items-center gap-2 flex-shrink-0">
                          {vote.interested ? (
                            <Badge className="bg-accent text-accent-foreground text-[10px] md:text-xs">
                              <Heart weight="fill" size={12} className="mr-0.5 md:mr-1 md:w-3.5 md:h-3.5" />
                              <span className="hidden md:inline">Interested</span>
                              <span className="md:hidden">Yes</span>
                            </Badge>
                          ) : (
                            <Badge variant="outline" className="text-muted-foreground text-[10px] md:text-xs">
                              <X weight="bold" size={12} className="mr-0.5 md:mr-1 md:w-3.5 md:h-3.5" />
                              <span className="hidden md:inline">Passed</span>
                              <span className="md:hidden">No</span>
                            </Badge>
                          )}
                        </div>
                      </div>

                      <p className="text-xs md:text-sm text-foreground/70 mb-2 md:mb-3 line-clamp-2">
                        {startup["Company Description"]}
                      </p>

                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => onChangeVote(String(startup.id), !vote.interested)}
                        className="text-[10px] md:text-xs h-7 md:h-8 px-2 md:px-3"
                      >
                        <ArrowCounterClockwise size={12} className="mr-1 md:w-3.5 md:h-3.5" />
                        Change to {vote.interested ? 'Pass' : 'Interested'}
                      </Button>
                    </div>
                  </div>
                </Card>
              )
            })}
        </div>
      </div>
    </div>
  )
}
