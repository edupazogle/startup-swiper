import { useState, useRef } from 'react'
import { motion, useMotionValue, useTransform, PanInfo } from 'framer-motion'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs'
import { Startup } from '@/lib/types'
import { MapPin, Users, CurrencyDollar, Sparkle, GlobeHemisphereWest, Calendar, TrendUp, Newspaper, ArrowUpRight } from '@phosphor-icons/react'
import { getTopicColor, getTechColor, getMaturityColor, getLocationColor } from '@/lib/badgeColors'
import { cn } from '@/lib/utils'

interface Article {
  title: string
  description: string
  imageUrl: string
  link: string
  source: string
  date: string
}

interface SwipeableCardProps {
  startup: Startup
  onSwipe: (interested: boolean) => void
  isProcessing?: boolean
}

export function SwipeableCard({ startup, onSwipe, isProcessing = false }: SwipeableCardProps) {
  const [hasVoted, setHasVoted] = useState(false)
  const x = useMotionValue(0)
  const rotate = useTransform(x, [-200, 0, 200], [-25, 0, 25])
  const opacity = useTransform(x, [-200, 0, 200], [0.5, 1, 0.5])

  const handleDragEnd = (_: any, info: PanInfo) => {
    if (hasVoted) return
    
    const threshold = 100
    if (Math.abs(info.offset.x) > threshold) {
      setHasVoted(true)
      onSwipe(info.offset.x > 0)
    }
  }

  const leftOverlayOpacity = useTransform(x, [-200, 0], [1, 0])
  const rightOverlayOpacity = useTransform(x, [0, 200], [0, 1])

  const displayName = startup.name || startup["Company Name"] || 'Unknown Startup'
  const displayDescription = startup.description || startup["Company Description"] || startup.shortDescription || 'No description available'
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
  const displayStage = startup.currentInvestmentStage || startup["Stage"] || 'Unknown'

  const mockArticles: Article[] = [
    {
      title: `${displayName} Raises New Funding Round`,
      description: `The innovative startup secures significant investment to accelerate growth and expand market presence.`,
      imageUrl: 'https://images.unsplash.com/photo-1579532537598-459ecdaf39cc?w=400&h=250&fit=crop',
      link: '#',
      source: 'TechCrunch',
      date: '2 days ago'
    },
    {
      title: `Industry Leaders Partner with ${displayName}`,
      description: `Strategic partnership aims to revolutionize the sector and bring cutting-edge solutions to market.`,
      imageUrl: 'https://images.unsplash.com/photo-1557804506-669a67965ba0?w=400&h=250&fit=crop',
      link: '#',
      source: 'VentureBeat',
      date: '5 days ago'
    },
    {
      title: `${displayName} Expands to New Markets`,
      description: `Ambitious expansion plans unveiled as company scales operations internationally with new product line.`,
      imageUrl: 'https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=400&h=250&fit=crop',
      link: '#',
      source: 'Forbes',
      date: '1 week ago'
    }
  ]

  return (
    <motion.div
      style={{ x, rotate, opacity }}
      drag="x"
      dragConstraints={{ left: 0, right: 0 }}
      dragElastic={0.2}
      onDragEnd={handleDragEnd}
      className="absolute"
    >
      <Card className="w-[min(90vw,440px)] h-[min(70vh,640px)] p-0 relative overflow-hidden shadow-2xl">
        <motion.div
          className="absolute inset-0 bg-destructive/20 flex items-center justify-center backdrop-blur-sm z-20 pointer-events-none"
          style={{ opacity: leftOverlayOpacity }}
        >
          <div className="text-4xl md:text-6xl font-bold text-destructive rotate-[-25deg]">
            PASS
          </div>
        </motion.div>

        <motion.div
          className="absolute inset-0 bg-accent/20 flex items-center justify-center backdrop-blur-sm z-20 pointer-events-none"
          style={{ opacity: rightOverlayOpacity }}
        >
          <div className="text-4xl md:text-6xl font-bold text-accent rotate-[25deg]">
            INTERESTED
          </div>
        </motion.div>

        <div className="relative z-10 h-full flex flex-col">
          <div className="p-4 md:p-6 pb-3 md:pb-4 bg-gradient-to-b from-card to-card/80">
            <div className="flex gap-3 md:gap-4 items-start">
              {displayLogo && (
                <div className="w-16 h-16 md:w-20 md:h-20 rounded-lg bg-background flex items-center justify-center overflow-hidden flex-shrink-0 border border-border/50 shadow-sm">
                  <img src={displayLogo} alt={displayName} className="w-full h-full object-contain p-1" />
                </div>
              )}
              <div className="flex-1 min-w-0">
                <h1 className="text-xl md:text-2xl font-bold leading-tight tracking-tight mb-2">
                  {displayName}
                </h1>
                <div className="flex flex-wrap gap-x-3 gap-y-2">
                  {startup.topics && startup.topics.length > 0 && (
                    <div className="flex flex-col gap-0.5">
                      <span className="text-[9px] md:text-[10px] text-muted-foreground uppercase tracking-wider font-medium">Topics</span>
                      <div className="flex flex-wrap gap-1">
                        {startup.topics.slice(0, 2).map((topic, i) => {
                          const colors = getTopicColor(topic)
                          return (
                            <Badge 
                              key={i} 
                              variant="outline" 
                              className={cn("text-xs font-medium border", colors.bg, colors.text, colors.border)}
                            >
                              {topic}
                            </Badge>
                          )
                        })}
                      </div>
                    </div>
                  )}
                  {startup.tech && startup.tech.length > 0 && (
                    <div className="flex flex-col gap-0.5">
                      <span className="text-[9px] md:text-[10px] text-muted-foreground uppercase tracking-wider font-medium">Tech</span>
                      <div className="flex flex-wrap gap-1">
                        {startup.tech.slice(0, 2).map((t, i) => {
                          const colors = getTechColor(t)
                          return (
                            <Badge 
                              key={i} 
                              variant="outline" 
                              className={cn("text-xs font-medium border", colors.bg, colors.text, colors.border)}
                            >
                              {t}
                            </Badge>
                          )
                        })}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>

          <Separator />

          <Tabs defaultValue="info" className="flex-1 flex flex-col min-h-0">
            <TabsList className="w-full rounded-none bg-muted/30 border-b">
              <TabsTrigger value="info" className="flex-1">Startup Info</TabsTrigger>
              <TabsTrigger value="news" className="flex-1 gap-2">
                <Newspaper size={16} weight="duotone" />
                News
              </TabsTrigger>
            </TabsList>

            <TabsContent value="info" className="flex-1 overflow-y-auto px-4 md:px-6 py-3 md:py-4 space-y-3 md:space-y-4 m-0 overscroll-contain">
              {displayUSP && (
                <div>
                  <div className="flex items-center gap-2 mb-2">
                    <Sparkle size={16} className="text-accent" weight="duotone" />
                    <h3 className="text-xs text-muted-foreground uppercase tracking-wide font-medium">Value Proposition</h3>
                  </div>
                  <p className="text-sm leading-relaxed text-accent-foreground bg-accent/5 p-3 rounded-md border border-accent/20">
                    {displayUSP}
                  </p>
                </div>
              )}

              <Separator />
              
              <div>
                <p className="text-sm leading-relaxed text-foreground/90">
                  {displayDescription}
                </p>
              </div>

              <Separator />
              
              <div className="grid grid-cols-2 gap-3">
                <div className="flex items-start gap-2">
                  <MapPin size={16} className="text-muted-foreground mt-0.5 flex-shrink-0" weight="duotone" />
                  <div className="min-w-0 flex-1">
                    <p className="text-xs text-muted-foreground uppercase tracking-wide">Location</p>
                    <Badge 
                      variant="outline" 
                      className={cn("text-xs font-medium border mt-1", getLocationColor(displayLocation).bg, getLocationColor(displayLocation).text, getLocationColor(displayLocation).border)}
                    >
                      {displayLocation}
                    </Badge>
                  </div>
                </div>
                
                <div className="flex items-start gap-2">
                  <Users size={16} className="text-muted-foreground mt-0.5 flex-shrink-0" weight="duotone" />
                  <div>
                    <p className="text-xs text-muted-foreground uppercase tracking-wide">Team Size</p>
                    <p className="text-sm font-medium">{displayEmployees}</p>
                  </div>
                </div>

                <div className="flex items-start gap-2">
                  <CurrencyDollar size={16} className="text-muted-foreground mt-0.5 flex-shrink-0" weight="duotone" />
                  <div>
                    <p className="text-xs text-muted-foreground uppercase tracking-wide">Funding</p>
                    <p className="text-sm font-medium">{displayFunding}</p>
                  </div>
                </div>

                <div className="flex items-start gap-2">
                  <TrendUp size={16} className="text-muted-foreground mt-0.5 flex-shrink-0" weight="duotone" />
                  <div>
                    <p className="text-xs text-muted-foreground uppercase tracking-wide">Stage</p>
                    <p className="text-sm font-medium">{displayStage}</p>
                  </div>
                </div>

                {startup.dateFounded && (
                  <div className="flex items-start gap-2">
                    <Calendar size={16} className="text-muted-foreground mt-0.5 flex-shrink-0" weight="duotone" />
                    <div>
                      <p className="text-xs text-muted-foreground uppercase tracking-wide">Founded</p>
                      <p className="text-sm font-medium">{new Date(startup.dateFounded).getFullYear()}</p>
                    </div>
                  </div>
                )}

                {displayWebsite && (
                  <div className="col-span-2 flex items-start gap-2">
                    <GlobeHemisphereWest size={16} className="text-muted-foreground mt-0.5 flex-shrink-0" weight="duotone" />
                    <div className="min-w-0 flex-1">
                      <p className="text-xs text-muted-foreground uppercase tracking-wide">Website</p>
                      <a 
                        href={displayWebsite.startsWith('http') ? displayWebsite : `https://${displayWebsite}`} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="text-sm font-medium text-accent hover:underline break-all"
                        onClick={(e) => e.stopPropagation()}
                      >
                        {displayWebsite.replace(/^https?:\/\//, '').replace(/^www\./, '')}
                      </a>
                    </div>
                  </div>
                )}
              </div>
            </TabsContent>

            <TabsContent value="news" className="flex-1 overflow-y-auto px-4 md:px-6 py-3 md:py-4 m-0 overscroll-contain">
              <div className="space-y-3">
                {mockArticles.map((article, idx) => (
                  <a
                    key={idx}
                    href={article.link}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="block group"
                    onClick={(e) => e.stopPropagation()}
                  >
                    <Card className="overflow-hidden hover:shadow-lg transition-all duration-300 border-border/50 hover:border-accent/50">
                      <div className="relative h-32 overflow-hidden bg-muted">
                        <img 
                          src={article.imageUrl} 
                          alt={article.title}
                          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                        />
                        <div className="absolute top-2 right-2 w-7 h-7 bg-white/90 backdrop-blur-sm rounded-md flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                          <ArrowUpRight size={14} weight="bold" className="text-foreground" />
                        </div>
                      </div>
                      
                      <div className="p-3">
                        <h4 className="text-sm font-semibold text-foreground mb-1.5 line-clamp-2 group-hover:text-accent transition-colors">
                          {article.title}
                        </h4>
                        <p className="text-xs text-muted-foreground mb-2 line-clamp-2 leading-relaxed">
                          {article.description}
                        </p>
                        <div className="flex items-center justify-between text-xs">
                          <span className="text-muted-foreground font-medium">
                            {article.source}
                          </span>
                          <span className="text-muted-foreground">
                            {article.date}
                          </span>
                        </div>
                      </div>
                    </Card>
                  </a>
                ))}
              </div>
            </TabsContent>
          </Tabs>
        </div>
      </Card>
    </motion.div>
  )
}
