import { useState, useRef } from 'react'
import { motion, useMotionValue, useTransform, PanInfo } from 'framer-motion'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs'
import { Separator } from '@/components/ui/separator'
import { Startup } from '@/lib/types'
import { MapPin, UsersGroup, Dollar, WandMagicSparkles, Globe, CalendarMonth, ChartLineUp, CheckCircle, CirclePlus, Briefcase, Check, Close, ArrowUpRightFromSquare, Award, Building, Star, Fire, Shield, Users } from 'flowbite-react-icons/outline'
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

interface SwipeableCardProps {
  startup: Startup
  onSwipe: (interested: boolean) => void
  isProcessing?: boolean
}

export function SwipeableCard({ startup, onSwipe, isProcessing = false }: SwipeableCardProps) {
  const [exitDirection, setExitDirection] = useState<'left' | 'right' | null>(null)
  const x = useMotionValue(0)
  const y = useMotionValue(0)
  
  // Transform hooks for smooth animations
  const rotate = useTransform(x, [-200, 0, 200], [-25, 0, 25])
  const opacity = useTransform(x, [-200, -100, 0, 100, 200], [0, 1, 1, 1, 0])
  
  // Overlay opacities based on drag distance
  const leftOverlayOpacity = useTransform(x, [-150, -50, 0], [1, 0.5, 0])
  const rightOverlayOpacity = useTransform(x, [0, 50, 150], [0, 0.5, 1])
  
  // Scale for visual feedback
  const scale = useTransform(x, [-200, 0, 200], [1.05, 1, 1.05])

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
    if (isProcessing || exitDirection) return
    
    const swipeThreshold = 100 // Distance threshold
    const velocityThreshold = 300 // Velocity threshold (px/s)
    
    const swipeDistance = info.offset.x
    const swipeVelocity = info.velocity.x
    
    // Determine if swipe should complete based on distance OR velocity
    const shouldSwipeRight = swipeDistance > swipeThreshold || swipeVelocity > velocityThreshold
    const shouldSwipeLeft = swipeDistance < -swipeThreshold || swipeVelocity < -velocityThreshold
    
    if (shouldSwipeRight) {
      // Swipe right - Interested
      setExitDirection('right')
      onSwipe(true)
    } else if (shouldSwipeLeft) {
      // Swipe left - Pass
      setExitDirection('left')
      onSwipe(false)
    }
    // If neither threshold met, card will spring back to center automatically
  }
  
  const handleButtonClick = (interested: boolean) => {
    if (isProcessing || exitDirection) return
    setExitDirection(interested ? 'right' : 'left')
    onSwipe(interested)
  }

  const displayName = startup.name || startup["Company Name"] || 'Unknown Startup'
  const displayDescription = startup.description || startup["Company Description"] || startup.shortDescription || 'No description available'
  const displayUSP = startup.shortDescription || startup["USP"] || ''
  const displayLogo = startup.logoUrl || startup.logo
  const displayWebsite = startup.website || startup["URL"]
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

  return (
    <motion.div
      style={{ 
        x, 
        y,
        rotate, 
        opacity,
        scale
      }}
      drag={exitDirection ? false : true}
      dragConstraints={{ left: 0, right: 0, top: 0, bottom: 0 }}
      dragElastic={1}
      onDragEnd={handleDragEnd}
      animate={exitDirection ? {
        x: exitDirection === 'right' ? 500 : -500,
        y: exitDirection === 'right' ? -50 : 50,
        rotate: exitDirection === 'right' ? 30 : -30,
        opacity: 0,
        transition: {
          duration: 0.5,
          ease: [0.4, 0, 0.2, 1] // Smooth easing
        }
      } : {
        x: 0,
        y: 0,
        rotate: 0,
        opacity: 1
      }}
      transition={{
        type: "spring",
        stiffness: 300,
        damping: 30
      }}
      className="absolute inset-0 w-full h-full touch-none select-none will-change-transform"
      role="article"
      aria-label={`Startup card: ${displayName}. Swipe or use buttons to pass or show interest.`}
    >
      <Card className="w-full h-full max-h-[calc(100vh-180px)] sm:max-h-[calc(100vh-200px)] md:max-h-none min-h-[350px] xs:min-h-[400px] sm:min-h-[450px] md:h-full p-0 relative shadow-xl transition-shadow duration-300 flex flex-col overflow-hidden border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 rounded-2xl">
        {/* Action Buttons - Top Right */}
        <div className="absolute top-4 right-4 z-30 flex gap-2" role="group" aria-label="Voting actions">
          <motion.button
            onClick={(e) => {
              e.stopPropagation()
              handleButtonClick(false)
            }}
            disabled={isProcessing || !!exitDirection}
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
            className="w-11 h-11 rounded-full bg-white dark:bg-gray-800 border-2 border-red-500 hover:border-red-600 hover:bg-red-50 dark:hover:bg-red-950 text-red-600 hover:text-red-700 dark:text-red-500 shadow-xl hover:shadow-2xl flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
            aria-label={`Pass on ${displayName}`}
            title="Pass"
          >
            <Close className="w-5.5 h-5.5" aria-hidden="true"  />
          </motion.button>
          
          <motion.button
            onClick={(e) => {
              e.stopPropagation()
              handleButtonClick(true)
            }}
            disabled={isProcessing || !!exitDirection}
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
            className="w-11 h-11 rounded-full bg-gradient-to-br from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 text-white shadow-xl hover:shadow-2xl flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
            aria-label={`Show interest in ${displayName}`}
            title="Interested"
          >
            <svg className="w-5.5 h-5.5" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
              <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z" />
            </svg>
          </motion.button>
        </div>

        {/* Left Swipe Overlay - Pass */}
        <motion.div
          className="absolute inset-0 bg-gradient-to-br from-red-500/40 to-red-600/40 flex items-center justify-center backdrop-blur-[2px] z-20 pointer-events-none rounded-2xl"
          style={{ opacity: leftOverlayOpacity }}
          initial={false}
          aria-hidden="true"
        >
          <div className="flex flex-col items-center bg-red-500/20 backdrop-blur-md rounded-3xl px-8 py-5 border-4 border-red-500 shadow-2xl">
            <div className="text-6xl md:text-8xl font-black text-red-500 rotate-[-20deg] drop-shadow-2xl tracking-wider">
              PASS
            </div>
            <div className="text-lg md:text-xl text-red-100 font-bold mt-4 drop-shadow-lg">Not a fit</div>
          </div>
        </motion.div>

        {/* Right Swipe Overlay - Interested */}
        <motion.div
          className="absolute inset-0 bg-gradient-to-br from-green-500/40 to-emerald-600/40 flex items-center justify-center backdrop-blur-[2px] z-20 pointer-events-none rounded-2xl"
          style={{ opacity: rightOverlayOpacity }}
          initial={false}
          aria-hidden="true"
        >
          <div className="flex flex-col items-center bg-green-500/20 backdrop-blur-md rounded-3xl px-8 py-5 border-4 border-green-500 shadow-2xl">
            <div className="text-6xl md:text-8xl font-black text-green-500 rotate-[20deg] drop-shadow-2xl tracking-wider">
              ♥ LIKE
            </div>
            <div className="text-lg md:text-xl text-green-100 font-bold mt-4 drop-shadow-lg">Want to learn more</div>
          </div>
        </motion.div>

        <div className="flex-1 flex flex-col min-h-0 w-full overflow-hidden">
          {/* Sticky Header */}
          <header className="flex-shrink-0 z-20 p-3 sm:p-4 md:p-5 pb-3 md:pb-4 bg-gradient-to-br from-gray-50 via-white to-gray-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 border-b-2 border-gray-200 dark:border-gray-700 shadow-sm">
            <div className="flex gap-3 sm:gap-4 items-start">
              {displayLogo && (
                <div className="w-14 h-14 sm:w-16 sm:h-16 md:w-20 md:h-20 rounded-lg bg-white dark:bg-gray-900 flex items-center justify-center overflow-hidden flex-shrink-0 border-2 border-gray-200 dark:border-gray-700 shadow-md" role="img" aria-label="Company logo">
                  <img src={displayLogo} alt={`${displayName} logo`} className="w-full h-full object-contain p-1.5" />
                </div>
              )}
              <div className="flex-1 min-w-0">
                <h1 className="text-lg sm:text-xl md:text-2xl lg:text-3xl font-extrabold leading-tight tracking-tight mb-2 md:mb-3 text-gray-900 dark:text-white">
                  {displayName}
                </h1>
                <div className="flex flex-wrap gap-x-2 sm:gap-x-3 gap-y-1.5 md:gap-y-2" role="group" aria-label="Startup categories and attributes">
                  {topicsArray && topicsArray.length > 0 && (
                    <div className="flex flex-col gap-1">
                      <span className="text-[9px] md:text-[10px] text-gray-600 dark:text-gray-400 uppercase tracking-wider font-bold" id="topics-label">Topics</span>
                      <div className="flex flex-wrap gap-1 md:gap-1.5" role="list" aria-labelledby="topics-label">
                        {topicsArray.slice(0, 2).map((topic, i) => {
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
                  )}
                  {startup.maturity && (
                    <div className="flex flex-col gap-1">
                      <span className="text-[9px] md:text-[10px] text-gray-600 dark:text-gray-400 uppercase tracking-wider font-bold">Maturity</span>
                      <div className="flex flex-wrap gap-1 md:gap-1.5">
                        <Badge 
                          variant="outline" 
                          className={cn("text-[10px] md:text-xs font-semibold border-2 px-2 py-0.5", getMaturityColor(startup.maturity).bg, getMaturityColor(startup.maturity).text, getMaturityColor(startup.maturity).border)}
                        >
                          {startup.maturity}
                        </Badge>
                      </div>
                    </div>
                  )}
                  {displayWebsite && (
                    <div className="flex flex-col gap-1">
                      <span className="text-[9px] md:text-[10px] text-gray-600 dark:text-gray-400 uppercase tracking-wider font-bold">Website</span>
                      <div className="flex flex-wrap gap-1 md:gap-1.5">
                        <a 
                          href={displayWebsite.startsWith('http') ? displayWebsite : `https://${displayWebsite}`} 
                          target="_blank" 
                          rel="noopener noreferrer"
                          className="text-[10px] md:text-xs font-semibold text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300 hover:underline transition-colors"
                          onClick={(e) => e.stopPropagation()}
                          aria-label={`Visit ${displayName} website (opens in new tab)`}
                        >
                          {displayWebsite.replace(/^https?:\/\//, '').replace(/^www\./, '')}
                        </a>
                      </div>
                    </div>
                  )}
                  {techArray && techArray.length > 0 && (
                    <div className="flex flex-col gap-1">
                      <span className="text-[9px] md:text-[10px] text-gray-600 dark:text-gray-400 uppercase tracking-wider font-bold">Tech</span>
                      <div className="flex flex-wrap gap-1 md:gap-1.5">
                        {techArray.slice(0, 2).map((t, i) => {
                          const colors = getTechColor(t)
                          return (
                            <Badge 
                              key={i} 
                              variant="outline" 
                              className={cn("text-[10px] md:text-xs font-semibold border-2 px-2 py-0.5", colors.bg, colors.text, colors.border)}
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
          </header>

          {/* Scrollable Content Area */}
          <div className="flex-1 flex flex-col overflow-y-auto min-h-0">
            {/* Sticky "Startup Info" Title */}
            <div className="sticky top-0 z-10 bg-gray-50 dark:bg-gray-900 border-b-2 border-gray-300 dark:border-gray-600 h-11 flex items-center px-4 flex-shrink-0 shadow-sm">
              <h3 className="text-xs md:text-sm font-bold text-gray-900 dark:text-white uppercase tracking-wide">Startup Info</h3>
            </div>
            
            {/* Scrollable Columns */}
            <div className="flex flex-col lg:flex-row lg:overflow-hidden lg:flex-1 min-h-0">
              {/* Column 1: VC Analysis & Core Product */}
              <div className="w-full lg:w-1/3 lg:h-full border-r-0 lg:border-r-2 border-gray-200 dark:border-gray-700 lg:overflow-y-auto px-3 md:px-4 py-3 lg:py-2 space-y-3 lg:space-y-2.5 flex-shrink-0">
              {/* Venture Clienting Analysis - TOP SECTION */}
              {(startup.axa_overall_score !== undefined || startup.axaOverallScore !== undefined) && (
                <section aria-labelledby="vc-analysis-heading" className="mb-3">
                  <div className="flex items-center gap-2 mb-3">
                    <Award className="text-blue-600 dark:text-blue-400 w-5 h-5" aria-hidden="true"   />
                    <h3 id="vc-analysis-heading" className="text-xs md:text-sm font-extrabold text-gray-900 dark:text-white uppercase tracking-wider">Venture Clienting Analysis</h3>
                  </div>
                  
                  <div className="bg-gradient-to-br from-blue-50 via-blue-50 to-indigo-50 dark:from-blue-950/30 dark:via-blue-900/30 dark:to-indigo-950/30 p-3 md:p-4 rounded-lg border-2 border-blue-200 dark:border-blue-800/50 shadow-md space-y-3">
                    {/* Grade Display */}
                    <div>
                      <p className="text-[10px] md:text-xs text-gray-700 dark:text-gray-300 uppercase tracking-wider font-extrabold mb-2" id="axa-grade-label">Rise Score</p>
                      <div className="flex items-start gap-2.5" role="group" aria-labelledby="axa-grade-label">
                        <span className={cn(
                          'text-3xl md:text-4xl font-extrabold tabular-nums leading-none',
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
                          <div className="flex-1 flex items-start gap-2 bg-white dark:bg-gray-800/50 p-3 rounded-lg shadow-sm border border-blue-100 dark:border-blue-900">
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
                        <span className="text-[10px] md:text-xs text-gray-700 dark:text-gray-300 leading-relaxed font-medium">
                          {startup.axa_grade_explanation || startup.axaGradeExplanation || 'Assessment pending'}
                        </span>
                      </div>
                        )}
                      </div>
                    </div>

                    {/* Use Cases */}
                    {(() => {
                      const useCases = startup.axa_use_cases || startup.axaUseCases
                      let useCaseArray: string[] = []
                      
                      try {
                        if (Array.isArray(useCases)) {
                          useCaseArray = useCases
                        } else if (typeof useCases === 'string') {
                          let parsed = JSON.parse(useCases)
                          if (typeof parsed === 'string') parsed = JSON.parse(parsed)
                          useCaseArray = Array.isArray(parsed) ? parsed : []
                        }
                      } catch (e) {
                        useCaseArray = []
                      }

                      return useCaseArray.length > 0 && (
                        <div>
                          <p className="text-[10px] md:text-xs text-gray-700 dark:text-gray-300 uppercase tracking-wider font-extrabold mb-2">Use Cases</p>
                          <div className="flex flex-wrap gap-1.5">
                            {useCaseArray.map((useCase: string, idx: number) => (
                              <div key={idx} className="flex items-center gap-1.5 bg-gradient-to-r from-green-500 to-emerald-600 px-3 py-1.5 rounded-lg border border-green-600/80 shadow-sm">
                                <CheckCircle className="text-white flex-shrink-0 w-3 h-3"   />
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
                </section>
              )}

              {/* Company Details - Moved under VC Analysis */}
              <section aria-label="Company statistics">
                <h3 className="sr-only">Key Metrics</h3>
                <dl className="grid grid-cols-2 gap-3 md:gap-4">
                  <div className="flex items-start gap-3">
                    <MapPin size={18} className="text-gray-500 dark:text-gray-400 mt-1 flex-shrink-0" aria-hidden="true"  />
                    <div className="min-w-0 flex-1">
                      <dt className="text-[10px] md:text-xs text-gray-600 dark:text-gray-400 uppercase tracking-wider font-extrabold mb-1.5">Location</dt>
                      <dd>
                        <Badge 
                          variant="outline" 
                          className={cn("text-[10px] md:text-xs font-bold border-2 mt-1", getLocationColor(displayLocation).bg, getLocationColor(displayLocation).text, getLocationColor(displayLocation).border)}
                        >
                          {displayLocation}
                        </Badge>
                      </dd>
                    </div>
                  </div>
                  
                  <div className="flex items-start gap-3">
                    <UsersGroup className="text-gray-500 dark:text-gray-400 mt-1 flex-shrink-0 w-5 h-5" aria-hidden="true"   />
                    <div>
                      <dt className="text-[10px] md:text-xs text-gray-600 dark:text-gray-400 uppercase tracking-wider font-extrabold mb-1.5">Team Size</dt>
                      <dd className="text-xs md:text-sm font-bold text-gray-900 dark:text-gray-100">{displayEmployees}</dd>
                    </div>
                  </div>

                  <div className="flex items-start gap-3">
                    <Dollar size={18} className="text-gray-500 dark:text-gray-400 mt-1 flex-shrink-0" aria-hidden="true"  />
                    <div>
                      <dt className="text-[10px] md:text-xs text-gray-600 dark:text-gray-400 uppercase tracking-wider font-extrabold mb-1.5">Total Funding</dt>
                      <dd className="text-xs md:text-sm font-bold text-gray-900 dark:text-gray-100">{displayFunding}</dd>
                    </div>
                  </div>

                  <div className="flex items-start gap-3">
                    <ChartLineUp size={18} className="text-gray-500 dark:text-gray-400 mt-1 flex-shrink-0" aria-hidden="true"  />
                    <div>
                      <dt className="text-[10px] md:text-xs text-gray-600 dark:text-gray-400 uppercase tracking-wider font-extrabold mb-1.5">Funding Stage</dt>
                      <dd className="text-xs md:text-sm font-bold text-gray-900 dark:text-gray-100">{displayStage}</dd>
                    </div>
                  </div>

                  {(startup.dateFounded || startup.founding_year) && (
                    <div className="flex items-start gap-3">
                      <CalendarMonth size={18} className="text-gray-500 dark:text-gray-400 mt-1 flex-shrink-0" aria-hidden="true"  />
                      <div>
                        <dt className="text-[10px] md:text-xs text-gray-600 dark:text-gray-400 uppercase tracking-wider font-extrabold mb-1.5">Founded Year</dt>
                        <dd className="text-xs md:text-sm font-bold text-gray-900 dark:text-gray-100">
                          {startup.founding_year || (startup.dateFounded ? new Date(startup.dateFounded).getFullYear() : 'Unknown')}
                        </dd>
                      </div>
                    </div>
                  )}
                </dl>
              </section>
              </div>

              {/* Column 2: Core Product, Market & Tech */}
              <div className="w-full lg:w-1/3 lg:h-full border-t lg:border-t-0 lg:border-r-2 border-gray-200 dark:border-gray-700 lg:overflow-y-auto px-3 md:px-4 py-3 lg:py-2 space-y-3 lg:space-y-2.5 flex-shrink-0">
              {/* Core Product */}
              {(startup.core_product || startup.extracted_product) && (
                <section aria-labelledby="product-heading">
                  <div className="flex items-center gap-2 mb-3">
                    <Building className="text-blue-600 dark:text-blue-400 w-5 h-5" aria-hidden="true"   />
                    <h3 id="product-heading" className="text-xs md:text-sm font-extrabold text-gray-900 dark:text-white uppercase tracking-wider">Core Product</h3>
                  </div>
                  <div className="text-xs md:text-sm leading-relaxed text-gray-900 dark:text-gray-100 bg-gradient-to-br from-blue-50 to-cyan-50 dark:from-blue-950/30 dark:to-cyan-950/30 p-3 md:p-4 rounded-lg border-2 border-blue-200 dark:border-blue-800/50 shadow-md">
                    <p>{startup.core_product || startup.extracted_product}</p>
                  </div>
                </section>
              )}

              {/* Market Information */}
              {(startup.target_customers || startup.extracted_market) && (
                <section aria-labelledby="market-heading">
                  <div className="flex items-center gap-2 mb-3">
                    <Users className="text-purple-600 dark:text-purple-400 w-5 h-5" aria-hidden="true"   />
                    <h3 id="market-heading" className="text-xs md:text-sm font-extrabold text-gray-900 dark:text-white uppercase tracking-wider">Target Market</h3>
                  </div>
                  <div className="text-xs md:text-sm leading-relaxed text-gray-900 dark:text-gray-100 bg-gradient-to-br from-purple-50 to-violet-50 dark:from-purple-950/30 dark:to-violet-950/30 p-3 md:p-4 rounded-lg border-2 border-purple-200 dark:border-purple-800/50 shadow-md">
                    <p>{startup.target_customers || startup.extracted_market}</p>
                  </div>
                </section>
              )}

              {/* Problem Solved */}
              {startup.problem_solved && (
                <section aria-labelledby="problem-heading">
                  <div className="flex items-center gap-2 mb-3">
                    <Fire className="text-orange-600 dark:text-orange-400 w-5 h-5" aria-hidden="true"   />
                    <h3 id="problem-heading" className="text-xs md:text-sm font-extrabold text-gray-900 dark:text-white uppercase tracking-wider">Problem Solved</h3>
                  </div>
                  <div className="text-xs md:text-sm leading-relaxed text-gray-900 dark:text-gray-100 bg-gradient-to-br from-orange-50 to-amber-50 dark:from-orange-950/30 dark:to-amber-950/30 p-3 md:p-4 rounded-lg border-2 border-orange-200 dark:border-orange-800/50 shadow-md">
                    <p>{startup.problem_solved}</p>
                  </div>
                </section>
              )}

              {/* Competitors Section */}
              {startup.vp_competitors && (
                <section aria-labelledby="competitors-heading">
                  <div className="flex items-center gap-2 mb-3">
                    <Shield className="text-slate-600 dark:text-slate-400 w-5 h-5" aria-hidden="true"   />
                    <h3 id="competitors-heading" className="text-xs md:text-sm font-extrabold text-gray-900 dark:text-white uppercase tracking-wider">Competitive Landscape</h3>
                  </div>
                  <div className="text-xs md:text-sm leading-relaxed text-gray-900 dark:text-gray-100 bg-gradient-to-br from-slate-50 to-gray-100 dark:from-slate-950/30 dark:to-gray-900/30 p-3 md:p-4 rounded-lg border-2 border-slate-200 dark:border-slate-800/50 shadow-md">
                    <p>{startup.vp_competitors}</p>
                  </div>
                </section>
              )}
              </div>

              {/* Column 3: Value Proposition & Business Opportunity */}
              <div className="w-full lg:w-1/3 lg:h-full border-t lg:border-t-0 border-gray-200 dark:border-gray-700 lg:overflow-y-auto px-3 md:px-4 py-3 lg:py-2 space-y-3 lg:space-y-2.5 flex-shrink-0">
              {/* Value Proposition */}
              {(startup.value_proposition || startup.shortDescription) && (
                <section aria-labelledby="value-prop-heading">
                  <div className="flex items-center gap-2 mb-3">
                    <Star size={18} className="text-pink-600 dark:text-pink-400" aria-hidden="true"  />
                    <h3 id="value-prop-heading" className="text-xs md:text-sm font-extrabold text-gray-900 dark:text-white uppercase tracking-wider">Value Proposition</h3>
                  </div>
                  <div className="text-xs md:text-sm leading-relaxed text-gray-900 dark:text-gray-100 bg-gradient-to-br from-pink-50 via-rose-50 to-pink-50 dark:from-pink-950/30 dark:via-rose-950/30 dark:to-pink-950/30 p-3 md:p-4 rounded-lg border-2 border-pink-200 dark:border-pink-800/50 shadow-md">
                    <p>{startup.value_proposition || startup.shortDescription}</p>
                  </div>
                </section>
              )}

              {/* Business Opportunity */}
              {(startup.axa_business_leverage || startup.axaBusinessLeverage) && (
                <section aria-labelledby="opportunity-heading" className="mb-3">
                  <div className="flex items-center gap-2 mb-3">
                    <ChartLineUp size={18} className="text-blue-600 dark:text-blue-400" aria-hidden="true"  />
                    <h3 id="opportunity-heading" className="text-xs md:text-sm font-extrabold text-gray-900 dark:text-white uppercase tracking-wider">Business Opportunity for AXA</h3>
                  </div>
                  <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg border-2 border-gray-200 dark:border-gray-700 p-3 md:p-4 flex-shrink-0">
                    <p className="text-xs md:text-sm text-gray-700 dark:text-gray-300 leading-relaxed font-medium">{startup.axa_business_leverage || startup.axaBusinessLeverage}</p>
                  </div>
                </section>
              )}
              </div>
            </div>
          </div>
        </div>
      </Card>
    </motion.div>
  )
}
