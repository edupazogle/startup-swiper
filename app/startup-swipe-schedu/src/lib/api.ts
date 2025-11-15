/**
 * API Service Layer
 * Centralized API calls to backend database
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// Type definitions
export interface ApiStartup {
  id: string | number
  company_name?: string
  name?: string
  company_description?: string
  description?: string
  website?: string
  primary_industry?: string
  category?: string
  topics?: string[]
  tech?: string[]
  maturity?: string
  logoUrl?: string
  totalFunding?: number
  currentInvestmentStage?: string
  employees?: string
  [key: string]: any
}

export interface ApiCalendarEvent {
  id: string
  title: string
  start_time: string
  end_time: string
  type: string
  stage?: string
  category?: string
  link?: string
  is_fixed?: boolean
  highlight?: boolean
  attendees?: string[]
}

export interface ApiIdea {
  id: string
  name: string
  title: string
  category: string
  description: string
  tags: string[]
  timestamp: number
}

export interface ApiRating {
  startup_id: string
  user_id: string
  rating: number
}

export interface ApiVote {
  startupId: string
  userId: string
  userName?: string
  interested: boolean
  timestamp: string
  meetingScheduled?: boolean
}

/**
 * API Service Class
 */
class ApiService {
  private baseUrl: string

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl
  }

  private async fetchJson<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
    })

    if (!response.ok) {
      throw new Error(`API Error: ${response.status} ${response.statusText}`)
    }

    return response.json()
  }

  // Health Check
  async health() {
    return this.fetchJson<{ status: string; version: string }>('/health')
  }

  // Startups
  async getStartups(skip: number = 0, limit: number = 100) {
    return this.fetchJson<{ total: number; count: number; startups: ApiStartup[] }>(
      `/startups/all?skip=${skip}&limit=${limit}`
    )
  }

  async getAllStartups(skip: number = 0, limit: number = 10000) {
    return this.fetchJson<{ total: number; count: number; startups: ApiStartup[] }>(
      `/startups/all?skip=${skip}&limit=${limit}`
    )
  }

  async getPrioritizedStartups(userId: string, limit: number = 5000, minScore: number = 30) {
    return this.fetchJson<{
      total: number
      prioritized_count: number
      personalized: boolean
      startups: ApiStartup[]
    }>(
      `/startups/prioritized?user_id=${encodeURIComponent(userId)}&limit=${limit}&min_score=${minScore}`
    )
  }

  async getAxaFilteredStartups(limit: number = 300, minScore: number = 25) {
    return this.fetchJson<{
      total: number
      returned: number
      min_score: number
      source: string
      processing: {
        method: string
        llm_model: string
        validation: string
      }
      tier_breakdown: Record<string, number>
      startups: ApiStartup[]
    }>(
      `/startups/axa/filtered?limit=${limit}&min_score=${minScore}`
    )
  }

  async getEnrichmentStats() {
    return this.fetchJson<{
      total_startups: number
      enriched_count: number
      with_funding: number
      with_logo: number
      enrichment_percentage: number
    }>('/startups/enrichment/stats')
  }

  // Calendar Events
  async getCalendarEvents(skip: number = 0, limit: number = 100) {
    return this.fetchJson<ApiCalendarEvent[]>(`/calendar-events/?skip=${skip}&limit=${limit}`)
  }

  async getEventsByDateRange(startDate: string, endDate: string) {
    return this.fetchJson<{ events: ApiCalendarEvent[]; count: number }>(
      `/api/calendar-events/date-range?start_date=${encodeURIComponent(startDate)}&end_date=${encodeURIComponent(endDate)}`
    )
  }

  async createCalendarEvent(event: Partial<ApiCalendarEvent>) {
    return this.fetchJson<ApiCalendarEvent>('/calendar-events/', {
      method: 'POST',
      body: JSON.stringify(event),
    })
  }

  // Ideas
  async getIdeas(skip: number = 0, limit: number = 100) {
    return this.fetchJson<ApiIdea[]>(`/ideas/?skip=${skip}&limit=${limit}`)
  }

  async createIdea(idea: Omit<ApiIdea, 'id'>) {
    return this.fetchJson<ApiIdea>('/ideas/', {
      method: 'POST',
      body: JSON.stringify(idea),
    })
  }

  // Ratings
  async getAverageRatings(limit: number = 100) {
    return this.fetchJson<{ ratings: Array<{ startup_id: string; avg_rating: number; num_ratings: number }>; count: number }>(
      `/api/ratings/average?limit=${limit}`
    )
  }

  async addRating(startupId: string, userId: string, rating: number) {
    return this.fetchJson<{ startup_id: string; user_id: string; rating: number; status: string }>(
      '/api/ratings',
      {
        method: 'POST',
        body: JSON.stringify({ startup_id: startupId, user_id: userId, rating }),
      }
    )
  }

  // Votes
  async createVote(vote: ApiVote) {
    return this.fetchJson('/votes/', {
      method: 'POST',
      body: JSON.stringify(vote),
    })
  }

  async deleteVote(startupId: string, userId: string) {
    return this.fetchJson(`/votes/${startupId}/${userId}`, {
      method: 'DELETE',
    })
  }

  async getVotes(skip: number = 0, limit: number = 1000) {
    return this.fetchJson<ApiVote[]>(`/votes/?skip=${skip}&limit=${limit}`)
  }

  // User Management
  async getCurrentUser() {
    return this.fetchJson<{ user_id: string }>('/api/current-user')
  }

  async setCurrentUser(userId: string) {
    return this.fetchJson<{ user_id: string; status: string }>('/api/current-user', {
      method: 'POST',
      body: JSON.stringify({ user_id: userId }),
    })
  }

  async getFinishedUsers() {
    return this.fetchJson<{ finished_users: string[]; count: number }>('/api/finished-users')
  }

  async markUserFinished(userId: string) {
    return this.fetchJson<{ user_id: string; status: string }>('/api/finished-users', {
      method: 'POST',
      body: JSON.stringify({ user_id: userId }),
    })
  }

  // Metadata
  async getDataVersion() {
    return this.fetchJson<{ version: string }>('/api/data-version')
  }

  async getAuroralThemes() {
    return this.fetchJson<{
      description: string | null
      last_viewed: string | null
      themes: Array<{
        id: number
        name: string
        hours: string
        mood: string
        colors: string[]
      }>
    }>('/api/auroral-themes')
  }
}

// Export singleton instance
export const api = new ApiService()

// Export default for convenience
export default api
