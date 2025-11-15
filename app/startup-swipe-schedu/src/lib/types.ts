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
  employees?: string
  billingCity?: string
  billingCountry?: string
  dateFounded?: string
  currentInvestmentStage?: string
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
