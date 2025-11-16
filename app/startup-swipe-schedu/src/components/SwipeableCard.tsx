import { useState, useRef } from 'react'
import { motion, useMotionValue, useTransform, PanInfo } from 'framer-motion'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs'
import { Separator } from '@/components/ui/separator'
import { Startup } from '@/lib/types'
import { MapPin, Users, CurrencyDollar, Sparkle, GlobeHemisphereWest, Calendar, TrendUp, Newspaper, ArrowUpRight, CheckCircle, Target, Briefcase, Check, X } from '@phosphor-icons/react'
import { getTopicColor, getTechColor, getMaturityColor, getLocationColor } from '@/lib/badgeColors'
import { cn } from '@/lib/utils'

// Category name mapping for cleaner display
const CATEGORY_NAME_MAP: Record<string, {name: string, rule: string}> = {
  'F1.1_observability_monitoring': { name: 'Observability & Monitoring', rule: 'Agentic Platform Enablers' },
  'F1.2_agent_orchestration': { name: 'Agent Orchestration', rule: 'Agentic Platform Enablers' },
  'F1.3_llm_operations': { name: 'LLM Operations', rule: 'Agentic Platform Enablers' },
  'F1.4_agent_frameworks': { name: 'Agent Frameworks', rule: 'Agentic Platform Enablers' },
  'F1.5_data_infrastructure': { name: 'Data Infrastructure', rule: 'Agentic Platform Enablers' },
  'F1.6_agent_testing': { name: 'Agent Testing', rule: 'Agentic Platform Enablers' },
  'F2.1_marketing_automation': { name: 'Marketing Automation', rule: 'Agentic Service Providers' },
  'F2.2_sales_enablement': { name: 'Sales Enablement', rule: 'Agentic Service Providers' },
  'F2.3_customer_support': { name: 'Customer Support', rule: 'Agentic Service Providers' },
  'F2.4_hr_recruiting': { name: 'HR & Recruiting', rule: 'Agentic Service Providers' },
  'F2.5_finance_procurement': { name: 'Finance & Procurement', rule: 'Agentic Service Providers' },
  'F2.6_data_analytics': { name: 'Data Analytics', rule: 'Agentic Service Providers' },
  'F2.7_workflow_automation': { name: 'Workflow Automation', rule: 'Agentic Service Providers' },
  'F3.1_claims_management': { name: 'Claims Management', rule: 'Insurance Solutions' },
  'F3.2_underwriting': { name: 'Underwriting', rule: 'Insurance Solutions' },
  'F3.3_policy_administration': { name: 'Policy Administration', rule: 'Insurance Solutions' },
  'F3.4_distribution_agency': { name: 'Distribution & Agency', rule: 'Insurance Solutions' },
  'F3.5_customer_experience': { name: 'Customer Experience', rule: 'Insurance Solutions' },
  'F3.6_compliance_regulatory': { name: 'Compliance & Regulatory', rule: 'Insurance Solutions' },
  'F4.1_health_analytics': { name: 'Health Analytics', rule: 'Health Innovations' },
  'F4.2_wellness_prevention': { name: 'Wellness & Prevention', rule: 'Health Innovations' },
  'F4.3_remote_monitoring': { name: 'Remote Monitoring', rule: 'Health Innovations' },
  'F4.4_telemedicine': { name: 'Telemedicine', rule: 'Health Innovations' },
  'F4.5_healthcare_fraud': { name: 'Healthcare Fraud', rule: 'Health Innovations' },
  'F5.1_code_development': { name: 'Code Development', rule: 'Development & IT' },
  'F5.2_automated_testing': { name: 'Automated Testing', rule: 'Development & IT' },
  'F5.3_legacy_migration': { name: 'Legacy Migration', rule: 'Development & IT' },
  'F5.4_system_integration': { name: 'System Integration', rule: 'Development & IT' },
  'F5.5_code_intelligence': { name: 'Code Intelligence', rule: 'Development & IT' },
  'F5.6_devops_ci_cd': { name: 'DevOps & CI/CD', rule: 'Development & IT' },
}

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

  // Helper to safely parse array fields (topics, tech, etc.)
  const parseArray = (value: any): string[] => {
    if (!value) return []
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

  // Helper to parse and format competitors data from extracted_competitors JSON
  const parseCompetitorsData = (value: any): {competitors: string[], advantages: string[], position: string} => {
    const result = {
      competitors: [] as string[],
      advantages: [] as string[],
      position: ''
    }
    
    if (!value) return result
    
    try {
      let data = value
      if (typeof value === 'string') {
        data = JSON.parse(value)
      }
      
      // Extract relevant information
      result.competitors = data.mentioned_competitors || []
      result.advantages = data.competitive_advantages || []
      result.position = data.market_position || ''
      
    } catch {
      // If parsing fails, just return empty result
    }
    
    return result
  }

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
  
  // Safe array parsing
  const topicsArray = parseArray(startup.topics)
  const techArray = parseArray(startup.tech)
  const displayLocation = startup.billingCity && startup.billingCountry 
    ? `${startup.billingCity}, ${startup.billingCountry}` 
    : (startup.billingCountry || startup["Headquarter Country"] || 'Unknown')
  
  // Format funding display - prioritize total_funding (from DB)
  const formatFunding = (amount: number | string | null | undefined): string => {
    if (!amount) return 'Undisclosed'
    const num = typeof amount === 'string' ? parseFloat(amount) : amount
    if (isNaN(num)) return 'Undisclosed'
    if (num === 0) return 'Undisclosed'
    if (num < 1) return `$${(num * 1000).toFixed(0)}K`
    if (num < 1000) return `$${num.toFixed(1)}M`
    return `$${(num / 1000).toFixed(1)}B`
  }
  
  const displayFunding = formatFunding(
    startup.total_funding || startup.totalFunding || startup["Funding"] || null
  )
  const displayEmployees = startup.employees || 'Undisclosed'
  const displayStage = startup.currentInvestmentStage || startup.funding_stage || startup["Stage"] || 'Unknown'

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
      style={{ x, rotate, opacity, borderRadius: '0.75rem' }}
      drag="x"
      dragConstraints={{ left: 0, right: 0 }}
      dragElastic={0.2}
      onDragEnd={handleDragEnd}
      className="absolute rounded-lg"
    >
      <Card style={{ borderRadius: '0.75rem' }} className="w-full h-full max-h-[calc(100vh-180px)] sm:max-h-[calc(100vh-200px)] md:max-h-none min-h-[350px] xs:min-h-[400px] sm:min-h-[450px] md:h-[clamp(500px,70vh,640px)] p-0 relative shadow-2xl flex flex-col overflow-hidden">
        {/* Action Buttons - Top Right */}
        <div className="absolute top-3 right-3 z-30 flex gap-1.5">
          <motion.button
            onClick={(e) => {
              e.stopPropagation()
              setHasVoted(true)
              onSwipe(false)
            }}
            disabled={isProcessing}
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.95 }}
            className="w-10 h-10 rounded-full bg-transparent border-2 border-red-500 hover:border-red-600 hover:bg-red-500/10 text-red-500 shadow-md flex items-center justify-center disabled:opacity-50"
          >
            <X size={20} weight="bold" />
          </motion.button>
          
          <motion.button
            onClick={(e) => {
              e.stopPropagation()
              setHasVoted(true)
              onSwipe(true)
            }}
            disabled={isProcessing}
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.95 }}
            className="w-10 h-10 rounded-full bg-red-500/80 hover:bg-red-500/90 text-white shadow-md flex items-center justify-center disabled:opacity-50"
          >
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z" />
            </svg>
          </motion.button>
        </div>

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
                  {topicsArray && topicsArray.length > 0 && (
                    <div className="flex flex-col gap-0.5">
                      <span className="text-[9px] md:text-[10px] text-muted-foreground uppercase tracking-wider font-medium">Topics</span>
                      <div className="flex flex-wrap gap-1">
                        {topicsArray.slice(0, 2).map((topic, i) => {
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
                  {startup.maturity && (
                    <div className="flex flex-col gap-0.5">
                      <span className="text-[9px] md:text-[10px] text-muted-foreground uppercase tracking-wider font-medium">Maturity</span>
                      <div className="flex flex-wrap gap-1">
                        <Badge 
                          variant="outline" 
                          className={cn("text-xs font-medium border", getMaturityColor(startup.maturity).bg, getMaturityColor(startup.maturity).text, getMaturityColor(startup.maturity).border)}
                        >
                          {startup.maturity}
                        </Badge>
                      </div>
                    </div>
                  )}
                  {techArray && techArray.length > 0 && (
                    <div className="flex flex-col gap-0.5">
                      <span className="text-[9px] md:text-[10px] text-muted-foreground uppercase tracking-wider font-medium">Tech</span>
                      <div className="flex flex-wrap gap-1">
                        {techArray.slice(0, 2).map((t, i) => {
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

          <Tabs defaultValue="info" className="flex-1 flex flex-col min-h-0">
            <TabsList className="w-full rounded-none bg-muted/30 border-b">
              <TabsTrigger value="info" className="flex-1">Startup Info</TabsTrigger>
              <TabsTrigger value="news" className="flex-1 gap-2">
                <Newspaper size={16} weight="duotone" />
                News
              </TabsTrigger>
            </TabsList>

            <TabsContent value="info" className="flex-1 overflow-y-auto px-4 md:px-6 py-3 md:py-4 space-y-3 md:space-y-4 m-0 overscroll-contain">
              {/* Venture Clienting Analysis - TOP SECTION */}
              {(startup.axa_overall_score !== undefined || startup.axaOverallScore !== undefined) && (
                <>
                  <Separator className="my-4" />
                  <div>
                    <div className="flex items-center gap-2 mb-3">
                      <Target size={16} className="text-blue-600 dark:text-blue-400" weight="duotone" />
                      <h3 className="text-xs text-muted-foreground uppercase tracking-wide font-medium">Venture Clienting Analysis</h3>
                    </div>
                    
                    <div className="grid grid-cols-2 gap-3 bg-blue-500/5 p-3 rounded-lg border border-blue-200 dark:border-blue-900/30">
                      {/* Left Column: Score & Provider Status */}
                      <div className="space-y-3">
                        {/* Score Section */}
                        <div>
                          <p className="text-xs text-muted-foreground uppercase tracking-wide font-medium mb-1">Rise Score</p>
                          <div className="flex items-end gap-2">
                            <span className="text-2xl md:text-3xl font-bold text-blue-600 dark:text-blue-400">
                              {(startup.axa_overall_score || startup.axaOverallScore)?.toFixed(0)}%
                            </span>
                          </div>
                        </div>

                        {/* Provider Status */}
                        {(startup.axa_can_use_as_provider !== undefined || startup.axaCanUseAsProvider !== undefined) && (
                          <div className="flex items-center gap-2">
                            <CheckCircle 
                              size={14} 
                              weight="fill"
                              className={cn(
                                (startup.axa_can_use_as_provider || startup.axaCanUseAsProvider) 
                                  ? 'text-green-600 dark:text-green-400' 
                                  : 'text-slate-400 dark:text-slate-600'
                              )} 
                            />
                            <span className="text-xs text-muted-foreground">
                              {(startup.axa_can_use_as_provider || startup.axaCanUseAsProvider) 
                                ? 'Can be used as provider'
                                : 'Research opportunity'}
                            </span>
                          </div>
                        )}
                      </div>

                      {/* Right Column: Use Cases */}
                      {(() => {
                        const useCases = startup.axa_use_cases || startup.axaUseCases
                        let useCaseArray: string[] = []
                        
                        try {
                          if (Array.isArray(useCases)) {
                            useCaseArray = useCases
                          } else if (typeof useCases === 'string') {
                            let parsed = JSON.parse(useCases)
                            if (typeof parsed === 'string') {
                              parsed = JSON.parse(parsed)
                            }
                            useCaseArray = Array.isArray(parsed) ? parsed : []
                          } else {
                            useCaseArray = []
                          }
                        } catch (e) {
                          useCaseArray = []
                        }

                        if (!Array.isArray(useCaseArray)) {
                          useCaseArray = []
                        }

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
                </>
              )}

              {/* Value Proposition - Always show in consistent box format */}
              {(startup.value_proposition || startup.shortDescription) && (
                <>
                  <Separator className="my-4" />
                  <div>
                  <div className="flex items-center gap-2 mb-2">
                    <Sparkle size={16} className="text-pink-600 dark:text-pink-400" weight="duotone" />
                    <h3 className="text-xs text-pink-700 dark:text-pink-300 uppercase tracking-wide font-medium">Value Proposition</h3>
                  </div>
                  <div className="text-sm leading-relaxed text-foreground bg-pink-500/5 p-3 rounded-lg border border-pink-200 dark:border-pink-900/30">
                    <p>{startup.value_proposition || startup.shortDescription}</p>
                  </div>
                </div>
                </>
              )}

              {/* Product Information */}
              {(startup.core_product || startup.extracted_product) && (
                <div>
                  <div className="flex items-center gap-2 mb-2">
                    <Briefcase size={16} className="text-blue-600 dark:text-blue-400" weight="duotone" />
                    <h3 className="text-xs text-blue-700 dark:text-blue-300 uppercase tracking-wide font-medium">Product</h3>
                  </div>
                  <div className="text-sm leading-relaxed text-foreground bg-blue-500/5 p-3 rounded-lg border border-blue-200 dark:border-blue-900/30">
                    <p>{startup.core_product || startup.extracted_product}</p>
                  </div>
                </div>
              )}

              {/* Market Information */}
              {(startup.target_customers || startup.extracted_market) && (
                <div>
                  <div className="flex items-center gap-2 mb-2">
                    <Target size={16} className="text-purple-600 dark:text-purple-400" weight="duotone" />
                    <h3 className="text-xs text-purple-700 dark:text-purple-300 uppercase tracking-wide font-medium">Target Market</h3>
                  </div>
                  <div className="text-sm leading-relaxed text-foreground bg-purple-500/5 p-3 rounded-lg border border-purple-200 dark:border-purple-900/30">
                    <p>{startup.target_customers || startup.extracted_market}</p>
                  </div>
                </div>
              )}

              {/* Problem Solved */}
              {startup.problem_solved && (
                <div>
                  <div className="flex items-center gap-2 mb-2">
                    <Target size={16} className="text-orange-600 dark:text-orange-400" weight="duotone" />
                    <h3 className="text-xs text-orange-700 dark:text-orange-300 uppercase tracking-wide font-medium">Problem Solved</h3>
                  </div>
                  <div className="text-sm leading-relaxed text-foreground bg-orange-500/5 p-3 rounded-lg border border-orange-200 dark:border-orange-900/30">
                    <p>{startup.problem_solved}</p>
                  </div>
                </div>
              )}

              {/* Competitors Section */}
              {startup.vp_competitors && (
                <div>
                  <div className="flex items-center gap-2 mb-2">
                    <Briefcase size={16} className="text-slate-600 dark:text-slate-400" weight="duotone" />
                    <h3 className="text-xs text-slate-700 dark:text-slate-300 uppercase tracking-wide font-medium">Competitors</h3>
                  </div>
                  <div className="text-sm leading-relaxed text-foreground bg-slate-500/5 p-3 rounded-lg border border-slate-200 dark:border-slate-900/30">
                    <p>{startup.vp_competitors}</p>
                  </div>
                </div>
              )}

              {/* Business Opportunity */}
              {(startup.axa_business_leverage || startup.axaBusinessLeverage) && (
                <>
                  <div>
                    <div className="flex items-center gap-2 mb-2">
                      <Briefcase size={16} className="text-green-600 dark:text-green-400" weight="duotone" />
                      <h3 className="text-xs text-green-700 dark:text-green-300 uppercase tracking-wide font-medium">Business Opportunity</h3>
                    </div>
                    <div className="text-sm leading-relaxed text-foreground bg-green-500/5 p-3 rounded-lg border border-green-200 dark:border-green-900/30">
                      <p>{startup.axa_business_leverage || startup.axaBusinessLeverage}</p>
                    </div>
                  </div>
                </>
              )}

              <Separator className="my-4" />

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

                {(startup.dateFounded || startup.founding_year) && (
                  <div className="flex items-start gap-2">
                    <Calendar size={16} className="text-muted-foreground mt-0.5 flex-shrink-0" weight="duotone" />
                    <div>
                      <p className="text-xs text-muted-foreground uppercase tracking-wide">Founded</p>
                      <p className="text-sm font-medium">
                        {startup.founding_year || (startup.dateFounded ? new Date(startup.dateFounded).getFullYear() : 'Unknown')}
                      </p>
                    </div>
                  </div>
                )}

                {startup.maturity && (
                  <div className="flex items-start gap-2">
                    <TrendUp size={16} className="text-muted-foreground mt-0.5 flex-shrink-0" weight="duotone" />
                    <div>
                      <p className="text-xs text-muted-foreground uppercase tracking-wide">Maturity</p>
                      <Badge 
                        variant="outline"
                        className={cn("text-xs font-medium border mt-1", getMaturityColor(startup.maturity).bg, getMaturityColor(startup.maturity).text, getMaturityColor(startup.maturity).border)}
                      >
                        {startup.maturity}
                      </Badge>
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
