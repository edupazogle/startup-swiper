/**
 * Topics and Use Cases API client
 * Manages hierarchical topic/use case data fetching
 */

const API_BASE = 'http://localhost:8000'

export interface UseCase {
  id: number
  name: string
}

export interface Topic {
  id: number
  name: string
  use_cases?: UseCase[]
}

export interface TopicsResponse {
  topics: Topic[]
  total_topics: number
  total_use_cases: number
}

export interface UseCasesResponse {
  topic_id: number
  topic_name: string
  use_cases: UseCase[]
  count: number
}

export interface QuickListResponse {
  topics: string[]
  count: number
}

/**
 * Fetch all topics with their use cases
 */
export async function fetchAllTopics(): Promise<TopicsResponse> {
  try {
    const response = await fetch(`${API_BASE}/topics-usecases/topics`)
    if (!response.ok) {
      throw new Error(`Failed to fetch topics: ${response.statusText}`)
    }
    return await response.json()
  } catch (error) {
    console.error('Error fetching topics:', error)
    throw error
  }
}

/**
 * Fetch use cases for a specific topic
 */
export async function fetchUseCasesForTopic(topicId: number): Promise<UseCasesResponse> {
  try {
    const response = await fetch(`${API_BASE}/topics-usecases/topics/${topicId}/use-cases`)
    if (!response.ok) {
      throw new Error(`Failed to fetch use cases: ${response.statusText}`)
    }
    return await response.json()
  } catch (error) {
    console.error(`Error fetching use cases for topic ${topicId}:`, error)
    throw error
  }
}

/**
 * Fetch quick list of just topic names
 */
export async function fetchTopicsQuickList(): Promise<QuickListResponse> {
  try {
    const response = await fetch(`${API_BASE}/topics-usecases/quick-list`)
    if (!response.ok) {
      throw new Error(`Failed to fetch topics: ${response.statusText}`)
    }
    return await response.json()
  } catch (error) {
    console.error('Error fetching quick topic list:', error)
    throw error
  }
}

/**
 * Get topic ID by name
 */
export function getTopicIdByName(topics: Topic[], topicName: string): number | null {
  const topic = topics.find(t => t.name === topicName)
  return topic?.id || null
}

/**
 * Get topic name by ID
 */
export function getTopicNameById(topics: Topic[], topicId: number): string | null {
  const topic = topics.find(t => t.id === topicId)
  return topic?.name || null
}
