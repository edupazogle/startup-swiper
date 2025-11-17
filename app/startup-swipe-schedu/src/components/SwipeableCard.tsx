import { useState, useRef } from 'react'
import { motion, useMotionValue, useTransform, PanInfo } from 'framer-motion'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs'
import { Separator } from '@/components/ui/separator'
import { Startup } from '@/lib/types'
import { MapPin, Users, CurrencyDollar, Sparkle, GlobeHemisphereWest, Calendar, TrendUp, CheckCircle, Target, Briefcase, Check, X, ArrowUpRight } from '@phosphor-icons/react'
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
  const [hasVoted, setHasVoted] = useState(false)
  const [isDragging, setIsDragging] = useState(false)
  const x = useMotionValue(0)
  const rotate = useTransform(x, [-300, 0, 300], [-30, 0, 30])
  const opacity = useTransform(x, [-300, 0, 300], [0.7, 1, 0.7])

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
    setIsDragging(false)
    
    // Increased threshold for better mobile experience
    const threshold = 150
    const velocity = Math.abs(info.velocity.x)
    const distance = Math.abs(info.offset.x)
    
    // Swipe if either threshold or velocity is met
    if (distance > threshold || velocity > 500) {
      setHasVoted(true)
      onSwipe(info.offset.x > 0)
    }
  }

  const leftOverlayOpacity = useTransform(x, [-300, 0], [1, 0])
  const rightOverlayOpacity = useTransform(x, [0, 300], [0, 1])

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
      style={{ x, rotate, opacity }}
      drag="x"
      dragConstraints={{ left: 0, right: 0 }}
      dragElastic={0.7}
      dragDirectionLock={true}
      dragMomentum={false}
      dragTransition={{ bounceStiffness: 600, bounceDamping: 20 }}
      onDragStart={() => setIsDragging(true)}
      onDragEnd={handleDragEnd}
      whileTap={{ cursor: 'grabbing' }}
      className="absolute rounded-lg touch-none select-none"
      role="article"
      aria-label={`Startup card: ${displayName}. Swipe or use buttons to pass or show interest.`}
    >
      <Card className="w-full h-full max-h-[calc(100vh-180px)] sm:max-h-[calc(100vh-200px)] md:max-h-none min-h-[350px] xs:min-h-[400px] sm:min-h-[450px] md:h-full p-0 relative shadow-md hover:shadow-xl transition-shadow duration-300 flex flex-row overflow-hidden border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800">
        {/* Action Buttons - Top Right */}
        <div className="absolute top-4 right-4 z-30 flex gap-2" role="group" aria-label="Voting actions">
          <motion.button
            onClick={(e) => {
              e.stopPropagation()
              setHasVoted(true)
              onSwipe(false)
            }}
            disabled={isProcessing}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="w-12 h-12 rounded-full bg-white dark:bg-gray-800 border-2 border-red-500 hover:border-red-600 hover:bg-red-50 dark:hover:bg-red-950 text-red-600 hover:text-red-700 dark:text-red-500 shadow-xl hover:shadow-2xl flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
            aria-label={`Pass on ${displayName}`}
            title="Pass"
          >
            <X size={24} weight="bold" aria-hidden="true" />
          </motion.button>
          
          <motion.button
            onClick={(e) => {
              e.stopPropagation()
              setHasVoted(true)
              onSwipe(true)
            }}
            disabled={isProcessing}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="w-12 h-12 rounded-full bg-gradient-to-br from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 text-white shadow-xl hover:shadow-2xl flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
            aria-label={`Show interest in ${displayName}`}
            title="Interested"
          >
            <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
              <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z" />
            </svg>
          </motion.button>
        </div>

        <motion.div
          className="absolute inset-0 bg-gradient-to-br from-red-500/30 to-red-600/30 flex items-center justify-center backdrop-blur-md z-20 pointer-events-none rounded-lg"
          style={{ opacity: leftOverlayOpacity }}
          initial={{ opacity: 0 }}
          animate={{ opacity: leftOverlayOpacity }}
          aria-hidden="true"
        >
          <div className="flex flex-col items-center bg-white/10 backdrop-blur-sm rounded-2xl px-8 py-6 border-2 border-red-500">
            <div className="text-5xl md:text-7xl font-black text-red-500 rotate-[-25deg] drop-shadow-2xl">
              ✕ PASS
            </div>
            <div className="text-base md:text-lg text-red-600 dark:text-red-400 font-bold mt-3">Not a fit</div>
          </div>
        </motion.div>

        <motion.div
          className="absolute inset-0 bg-gradient-to-br from-green-500/30 to-emerald-600/30 flex items-center justify-center backdrop-blur-md z-20 pointer-events-none rounded-lg"
          style={{ opacity: rightOverlayOpacity }}
          initial={{ opacity: 0 }}
          animate={{ opacity: rightOverlayOpacity }}
          aria-hidden="true"
        >
          <div className="flex flex-col items-center bg-white/10 backdrop-blur-sm rounded-2xl px-8 py-6 border-2 border-green-500">
            <div className="text-5xl md:text-7xl font-black text-green-500 rotate-[25deg] drop-shadow-2xl">
              ♥ INTERESTED
            </div>
            <div className="text-base md:text-lg text-green-600 dark:text-green-400 font-bold mt-3">Want to learn more</div>
          </div>
        </motion.div>

        <div className="relative z-10 h-full flex flex-col w-full">
          <header className="p-5 md:p-7 pb-4 md:pb-5 bg-gradient-to-br from-gray-50 via-white to-gray-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 border-b border-gray-200 dark:border-gray-700">
            <div className="flex gap-4 md:gap-5 items-start">
              {displayLogo && (
                <div className="w-20 h-20 md:w-24 md:h-24 rounded-xl bg-white dark:bg-gray-900 flex items-center justify-center overflow-hidden flex-shrink-0 border-2 border-gray-200 dark:border-gray-700 shadow-md" role="img" aria-label="Company logo">
                  <img src={displayLogo} alt={`${displayName} logo`} className="w-full h-full object-contain p-2" />
                </div>
              )}
              <div className="flex-1 min-w-0">
                <h1 className="text-2xl md:text-3xl font-extrabold leading-tight tracking-tight mb-3 text-gray-900 dark:text-white">
                  {displayName}
                </h1>
                <div className="flex flex-wrap gap-x-4 gap-y-3" role="group" aria-label="Startup categories and attributes">
                  {topicsArray && topicsArray.length > 0 && (
                    <div className="flex flex-col gap-1">
                      <span className="text-[10px] md:text-xs text-gray-500 dark:text-gray-400 uppercase tracking-wider font-semibold" id="topics-label">Topics</span>
                      <div className="flex flex-wrap gap-1.5" role="list" aria-labelledby="topics-label">
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
                    <div className="flex flex-col gap-1">
                      <span className="text-[10px] md:text-xs text-gray-500 dark:text-gray-400 uppercase tracking-wider font-semibold">Maturity</span>
                      <div className="flex flex-wrap gap-1.5">
                        <Badge 
                          variant="outline" 
                          className={cn("text-xs font-semibold border-2 px-2.5 py-0.5", getMaturityColor(startup.maturity).bg, getMaturityColor(startup.maturity).text, getMaturityColor(startup.maturity).border)}
                        >
                          {startup.maturity}
                        </Badge>
                      </div>
                    </div>
                  )}
                  {techArray && techArray.length > 0 && (
                    <div className="flex flex-col gap-1">
                      <span className="text-[10px] md:text-xs text-gray-500 dark:text-gray-400 uppercase tracking-wider font-semibold">Tech</span>
                      <div className="flex flex-wrap gap-1.5">
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
          </header>

          {/* Startup Info Section - Full Width */}
          <div className="flex-1 flex flex-col overflow-hidden">
            <div className="bg-gray-100 dark:bg-gray-900 border-b-2 border-gray-200 dark:border-gray-700 h-12 flex items-center px-4 flex-shrink-0">
              <h3 className="text-sm font-semibold text-gray-900 dark:text-white">Startup Info</h3>
            </div>
            <div className="flex-1 flex flex-col lg:flex-row overflow-y-auto lg:overflow-hidden min-h-0">
              {/* Column 1: VC Analysis & Core Product */}
              <div className="w-full lg:w-1/3 lg:h-full border-r-0 lg:border-r border-gray-200 dark:border-gray-700 lg:overflow-y-auto px-3 md:px-4 py-3 md:py-4 space-y-3 md:space-y-4 flex-shrink-0">
              {/* Venture Clienting Analysis - TOP SECTION */}
              {(startup.axa_overall_score !== undefined || startup.axaOverallScore !== undefined) && (
                <section aria-labelledby="vc-analysis-heading" className="mb-4">
                  <div className="flex items-center gap-2 mb-3">
                    <Target size={20} className="text-blue-600 dark:text-blue-400" weight="duotone" aria-hidden="true" />
                    <h3 id="vc-analysis-heading" className="text-sm font-extrabold text-blue-700 dark:text-blue-300 uppercase tracking-wider">Venture Clienting Analysis</h3>
                  </div>
                  
                  <div className="bg-gradient-to-br from-blue-50 via-blue-50 to-indigo-50 dark:from-blue-950/30 dark:via-blue-900/30 dark:to-indigo-950/30 p-4 rounded-xl border-2 border-blue-200 dark:border-blue-800/50 shadow-sm space-y-3">
                    {/* Grade Display */}
                    <div>
                      <p className="text-xs text-gray-600 dark:text-gray-400 uppercase tracking-wider font-bold mb-2" id="axa-grade-label">Rise Score</p>
                      <div className="flex items-start gap-3" role="group" aria-labelledby="axa-grade-label">
                        <span className={cn(
                          'text-4xl md:text-5xl font-extrabold tabular-nums leading-none',
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
                          <div className="flex-1 flex items-start gap-2 bg-white dark:bg-gray-800/50 p-3 rounded-lg shadow-sm">
                            <Sparkle 
                              size={16} 
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
                        <span className="text-xs text-gray-700 dark:text-gray-300 leading-snug">
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
                          <p className="text-xs text-gray-600 dark:text-gray-400 uppercase tracking-wider font-bold mb-2">Use Cases</p>
                          <div className="flex flex-wrap gap-2">
                            {useCaseArray.map((useCase: string, idx: number) => (
                              <div key={idx} className="flex items-center gap-1.5 bg-gradient-to-r from-green-500 to-emerald-600 px-2 py-1 rounded-lg border border-green-600/80 shadow-sm">
                                <CheckCircle size={12} weight="bold" className="text-white flex-shrink-0" />
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

              {/* Product Information */}
              {(startup.core_product || startup.extracted_product) && (
                <section aria-labelledby="product-heading">
                  <div className="flex items-center gap-2 mb-3">
                    <Briefcase size={20} className="text-blue-600 dark:text-blue-400" weight="duotone" aria-hidden="true" />
                    <h3 id="product-heading" className="text-sm font-extrabold text-blue-700 dark:text-blue-300 uppercase tracking-wider">Core Product</h3>
                  </div>
                  <div className="text-sm leading-relaxed text-gray-900 dark:text-gray-100 bg-gradient-to-br from-blue-50 to-cyan-50 dark:from-blue-950/30 dark:to-cyan-950/30 p-4 rounded-xl border-2 border-blue-200 dark:border-blue-800/50 shadow-sm">
                    <p>{startup.core_product || startup.extracted_product}</p>
                  </div>
                </section>
              )}
              </div>
              
              {/* Column 2: Value Proposition, Market & Tech */}
              <div className="w-full lg:w-1/3 lg:h-full border-t lg:border-t-0 lg:border-r border-gray-200 dark:border-gray-700 lg:overflow-y-auto px-3 md:px-4 py-3 md:py-4 space-y-3 md:space-y-4 flex-shrink-0">
              {/* Value Proposition - Always show in consistent box format */}
              {(startup.value_proposition || startup.shortDescription) && (
                <section aria-labelledby="value-prop-heading">
                  <div className="flex items-center gap-2 mb-3">
                    <Sparkle size={20} className="text-pink-600 dark:text-pink-400" weight="duotone" aria-hidden="true" />
                    <h3 id="value-prop-heading" className="text-sm font-extrabold text-pink-700 dark:text-pink-300 uppercase tracking-wider">Value Proposition</h3>
                  </div>
                  <div className="text-sm leading-relaxed text-gray-900 dark:text-gray-100 bg-gradient-to-br from-pink-50 via-rose-50 to-pink-50 dark:from-pink-950/30 dark:via-rose-950/30 dark:to-pink-950/30 p-4 rounded-xl border-2 border-pink-200 dark:border-pink-800/50 shadow-sm">
                    <p>{startup.value_proposition || startup.shortDescription}</p>
                  </div>
                </section>
              )}

              {/* Market Information */}
              {(startup.target_customers || startup.extracted_market) && (
                <section aria-labelledby="market-heading">
                  <div className="flex items-center gap-2 mb-3">
                    <Target size={20} className="text-purple-600 dark:text-purple-400" weight="duotone" aria-hidden="true" />
                    <h3 id="market-heading" className="text-sm font-extrabold text-purple-700 dark:text-purple-300 uppercase tracking-wider">Target Market</h3>
                  </div>
                  <div className="text-sm leading-relaxed text-gray-900 dark:text-gray-100 bg-gradient-to-br from-purple-50 to-violet-50 dark:from-purple-950/30 dark:to-violet-950/30 p-4 rounded-xl border-2 border-purple-200 dark:border-purple-800/50 shadow-sm">
                    <p>{startup.target_customers || startup.extracted_market}</p>
                  </div>
                </section>
              )}

              {/* Problem Solved */}
              {startup.problem_solved && (
                <section aria-labelledby="problem-heading">
                  <div className="flex items-center gap-2 mb-3">
                    <Target size={20} className="text-orange-600 dark:text-orange-400" weight="duotone" aria-hidden="true" />
                    <h3 id="problem-heading" className="text-sm font-extrabold text-orange-700 dark:text-orange-300 uppercase tracking-wider">Problem Solved</h3>
                  </div>
                  <div className="text-sm leading-relaxed text-gray-900 dark:text-gray-100 bg-gradient-to-br from-orange-50 to-amber-50 dark:from-orange-950/30 dark:to-amber-950/30 p-4 rounded-xl border-2 border-orange-200 dark:border-orange-800/50 shadow-sm">
                    <p>{startup.problem_solved}</p>
                  </div>
                </section>
              )}

              {/* Competitors Section */}
              {startup.vp_competitors && (
                <section aria-labelledby="competitors-heading">
                  <div className="flex items-center gap-2 mb-3">
                    <Briefcase size={20} className="text-slate-600 dark:text-slate-400" weight="duotone" aria-hidden="true" />
                    <h3 id="competitors-heading" className="text-sm font-extrabold text-slate-700 dark:text-slate-300 uppercase tracking-wider">Competitive Landscape</h3>
                  </div>
                  <div className="text-sm leading-relaxed text-gray-900 dark:text-gray-100 bg-gradient-to-br from-slate-50 to-gray-100 dark:from-slate-950/30 dark:to-gray-900/30 p-4 rounded-xl border-2 border-slate-200 dark:border-slate-800/50 shadow-sm">
                    <p>{startup.vp_competitors}</p>
                  </div>
                </section>
              )}
              </div>
              
              {/* Column 3: Business Opportunity & Company Info */}
              <div className="w-full lg:w-1/3 lg:h-full border-t lg:border-t-0 border-gray-200 dark:border-gray-700 lg:overflow-y-auto px-3 md:px-4 py-3 md:py-4 space-y-3 md:space-y-4 flex-shrink-0">
              {/* Business Opportunity */}
              {(startup.axa_business_leverage || startup.axaBusinessLeverage) && (
                <section aria-labelledby="opportunity-heading">
                  <div className="flex items-center gap-2 mb-3">
                    <Briefcase size={20} className="text-green-600 dark:text-green-400" weight="duotone" aria-hidden="true" />
                    <h3 id="opportunity-heading" className="text-sm font-extrabold text-green-700 dark:text-green-300 uppercase tracking-wider">Business Opportunity for AXA</h3>
                  </div>
                  <div className="text-sm leading-relaxed text-gray-900 dark:text-gray-100 bg-gradient-to-br from-green-50 to-emerald-50 dark:from-green-950/30 dark:to-emerald-950/30 p-4 rounded-xl border-2 border-green-200 dark:border-green-800/50 shadow-sm">
                    <p>{startup.axa_business_leverage || startup.axaBusinessLeverage}</p>
                  </div>
                </section>
              )}

              <section aria-label="Company statistics">
                <h3 className="sr-only">Key Metrics</h3>
                <dl className="grid grid-cols-2 gap-4">
                  <div className="flex items-start gap-3">
                    <MapPin size={20} className="text-gray-500 dark:text-gray-400 mt-0.5 flex-shrink-0" weight="duotone" aria-hidden="true" />
                    <div className="min-w-0 flex-1">
                      <dt className="text-xs text-gray-500 dark:text-gray-400 uppercase tracking-wider font-semibold mb-1">Location</dt>
                      <dd>
                        <Badge 
                          variant="outline" 
                          className={cn("text-xs font-bold border-2 mt-1", getLocationColor(displayLocation).bg, getLocationColor(displayLocation).text, getLocationColor(displayLocation).border)}
                        >
                          {displayLocation}
                        </Badge>
                      </dd>
                    </div>
                  </div>
                  
                  <div className="flex items-start gap-3">
                    <Users size={20} className="text-gray-500 dark:text-gray-400 mt-0.5 flex-shrink-0" weight="duotone" aria-hidden="true" />
                    <div>
                      <dt className="text-xs text-gray-500 dark:text-gray-400 uppercase tracking-wider font-semibold mb-1">Team Size</dt>
                      <dd className="text-sm font-bold text-gray-900 dark:text-gray-100">{displayEmployees}</dd>
                    </div>
                  </div>

                  <div className="flex items-start gap-3">
                    <CurrencyDollar size={20} className="text-gray-500 dark:text-gray-400 mt-0.5 flex-shrink-0" weight="duotone" aria-hidden="true" />
                    <div>
                      <dt className="text-xs text-gray-500 dark:text-gray-400 uppercase tracking-wider font-semibold mb-1">Total Funding</dt>
                      <dd className="text-sm font-bold text-gray-900 dark:text-gray-100">{displayFunding}</dd>
                    </div>
                  </div>

                  <div className="flex items-start gap-3">
                    <TrendUp size={20} className="text-gray-500 dark:text-gray-400 mt-0.5 flex-shrink-0" weight="duotone" aria-hidden="true" />
                    <div>
                      <dt className="text-xs text-gray-500 dark:text-gray-400 uppercase tracking-wider font-semibold mb-1">Funding Stage</dt>
                      <dd className="text-sm font-bold text-gray-900 dark:text-gray-100">{displayStage}</dd>
                    </div>
                  </div>

                  {(startup.dateFounded || startup.founding_year) && (
                    <div className="flex items-start gap-3">
                      <Calendar size={20} className="text-gray-500 dark:text-gray-400 mt-0.5 flex-shrink-0" weight="duotone" aria-hidden="true" />
                      <div>
                        <dt className="text-xs text-gray-500 dark:text-gray-400 uppercase tracking-wider font-semibold mb-1">Founded Year</dt>
                        <dd className="text-sm font-bold text-gray-900 dark:text-gray-100">
                          {startup.founding_year || (startup.dateFounded ? new Date(startup.dateFounded).getFullYear() : 'Unknown')}
                        </dd>
                      </div>
                    </div>
                  )}

                  {startup.maturity && (
                    <div className="flex items-start gap-3">
                      <TrendUp size={20} className="text-gray-500 dark:text-gray-400 mt-0.5 flex-shrink-0" weight="duotone" aria-hidden="true" />
                      <div>
                        <dt className="text-xs text-gray-500 dark:text-gray-400 uppercase tracking-wider font-semibold mb-1">Maturity Level</dt>
                        <dd>
                          <Badge 
                            variant="outline"
                            className={cn("text-xs font-bold border-2 mt-1 px-2.5 py-0.5", getMaturityColor(startup.maturity).bg, getMaturityColor(startup.maturity).text, getMaturityColor(startup.maturity).border)}
                          >
                            {startup.maturity}
                          </Badge>
                        </dd>
                      </div>
                    </div>
                  )}

                  {displayWebsite && (
                    <div className="col-span-2 flex items-start gap-3">
                      <GlobeHemisphereWest size={20} className="text-gray-500 dark:text-gray-400 mt-0.5 flex-shrink-0" weight="duotone" aria-hidden="true" />
                      <div className="min-w-0 flex-1">
                        <dt className="text-xs text-gray-500 dark:text-gray-400 uppercase tracking-wider font-semibold mb-1">Website</dt>
                        <dd>
                          <a 
                            href={displayWebsite.startsWith('http') ? displayWebsite : `https://${displayWebsite}`} 
                            target="_blank" 
                            rel="noopener noreferrer"
                            className="text-sm font-medium text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300 hover:underline break-all inline-flex items-center gap-1"
                            onClick={(e) => e.stopPropagation()}
                            aria-label={`Visit ${displayName} website (opens in new tab)`}
                          >
                            {displayWebsite.replace(/^https?:\/\//, '').replace(/^www\./, '')}
                            <ArrowUpRight size={12} weight="bold" aria-hidden="true" />
                          </a>
                        </dd>
                      </div>
                    </div>
                  )}
                </dl>
              </section>
              </div>
            </div>
          </div>
        </div>
      </Card>
    </motion.div>
  )
}
