export interface Startup {
  id: string | number
  name: string
  shortDescription: string
  description: string
  logoUrl?: string
  website?: string
  topics: string[]
  tech: string[]
  maturity: string
  maturity_score?: number
  totalFunding?: string
  total_funding?: number
  total_equity_funding?: number
  last_funding_date?: string
  valuation?: number
  latest_revenue_min?: number
  latest_revenue_max?: number
  revenue_date?: string
  employees?: string
  billingCity?: string
  billingCountry?: string
  dateFounded?: string
  currentInvestmentStage?: string
  funding_stage?: string
  "Company Name"?: string
  "Company Description"?: string
  "Category"?: string
  "AXA Category"?: string
  "Stage"?: string
  "Final Priority Score"?: number
  "Headquarter Country"?: string
  "Funding"?: string
  "USP"?: string
  "URL"?: string
  "Additional Info"?: string
  logo?: string
  contactPerson?: string
  contactEmail?: string
  // AXA Evaluation Fields
  axa_evaluation_date?: string
  axaEvaluationDate?: string
  axa_overall_score?: number
  axaOverallScore?: number
  axa_priority_tier?: string
  axaPriorityTier?: string
  axa_can_use_as_provider?: boolean
  axaCanUseAsProvider?: boolean
  axa_business_leverage?: string
  axaBusinessLeverage?: string
  axa_primary_topic?: string
  axaPrimaryTopic?: string
  axa_use_cases?: string | string[]
  axaUseCases?: string | string[]
  // Product & Market Fields
  value_proposition?: string
  core_product?: string
  target_customers?: string
  problem_solved?: string
  key_differentiator?: string
  business_model?: string
  vp_competitors?: string
  extracted_product?: string
  extracted_market?: string
  extracted_competitors?: string
  company_name?: string
}

export interface Vote {
  startupId: string
  userId: string
  userName: string
  interested: boolean
  timestamp: number
  meetingScheduled?: boolean
  rating?: number
}

export interface TeamMember {
  id: string
  name: string
  avatar?: string
}

export type EventLocation = 'Founder stage' | 'Impact stage' | 'Builder stage' | 'Startup stage' | 'Meeting' | 'Venture clienting'

export type EventCategory = 'Agentic' | 'Agentic AI' | 'AI' | 'Great speakers' | 'Venture' | 'Health' | 'Software development' | 'DeepTech computing' | 'Slush 100'

export interface CalendarEvent {
  id: string
  title: string
  description?: string
  startTime: Date | string | number
  endTime: Date | string | number
  location?: EventLocation | string
  category?: EventCategory
  type: 'meeting' | 'presentation' | 'break'
  attendees: string[]
  startupId?: string
  startupName?: string
  confirmed?: boolean
  isFixed?: boolean
  link?: string
  highlight?: boolean
}

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: number
}

export type IdeaCategory = '1' | '2' | '3' | '4' | '5' | '6' | '7' | '8' | '9' | '10'

export interface Idea {
  id: string
  name: string
  title: string
  category: IdeaCategory
  description: string
  tags: string[]
  timestamp: number
  images?: string[]
}
