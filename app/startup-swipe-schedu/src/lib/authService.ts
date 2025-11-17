/**
 * Authentication Service
 * Handles JWT tokens, refresh tokens, and API authentication
 */

import { api } from './api'

const ACCESS_TOKEN_KEY = 'access_token'
const REFRESH_TOKEN_KEY = 'refresh_token'
const TOKEN_EXPIRY_KEY = 'token_expiry'
const USER_EMAIL_KEY = 'user_email'

export interface LoginResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
}

export interface User {
  id: number
  email: string
  full_name?: string
  is_active: boolean
  created_at: string
}

class AuthService {
  private refreshPromise: Promise<string> | null = null

  /**
   * Login with email and password
   */
  async login(email: string, password: string): Promise<User> {
    try {
      const response = await fetch(`${this.getApiUrl()}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      })

      if (!response.ok) {
        if (response.status === 401) {
          throw new Error('Invalid credentials')
        } else if (response.status === 500) {
          throw new Error('Server error. Please try again later.')
        } else {
          throw new Error('Login failed. Please try again.')
        }
      }

      const data: LoginResponse = await response.json()
      this.setTokens(data.access_token, data.refresh_token, data.expires_in)
      localStorage.setItem(USER_EMAIL_KEY, email)

      // Fetch user data
      const user = await this.getCurrentUser()
      console.log('✓ Login successful:', user.email)
      return user
    } catch (error) {
      console.error('Login failed:', error)
      throw error
    }
  }

  /**
   * Register new user
   */
  async register(email: string, password: string, fullName?: string): Promise<User> {
    try {
      const response = await fetch(`${this.getApiUrl()}/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password, full_name: fullName }),
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || 'Registration failed')
      }

      const user: User = await response.json()
      
      // Auto-login after registration
      await this.login(email, password)
      
      return user
    } catch (error) {
      console.error('Registration failed:', error)
      throw error
    }
  }

  /**
   * Logout - revoke refresh token and clear local storage
   */
  async logout(): Promise<void> {
    const refreshToken = this.getRefreshToken()
    
    if (refreshToken) {
      try {
        await fetch(`${this.getApiUrl()}/auth/logout`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ refresh_token: refreshToken }),
        })
      } catch (error) {
        console.error('Logout API call failed:', error)
      }
    }

    this.clearTokens()
  }

  /**
   * Get current user from API
   */
  async getCurrentUser(): Promise<User> {
    const response = await this.authenticatedFetch('/auth/me')
    return response.json()
  }

  /**
   * Get access token from storage
   */
  getAccessToken(): string | null {
    return localStorage.getItem(ACCESS_TOKEN_KEY)
  }

  /**
   * Get refresh token from storage
   */
  getRefreshToken(): string | null {
    return localStorage.getItem(REFRESH_TOKEN_KEY)
  }

  /**
   * Check if user is authenticated
   */
  isAuthenticated(): boolean {
    const token = this.getAccessToken()
    const expiry = localStorage.getItem(TOKEN_EXPIRY_KEY)
    
    if (!token || !expiry) {
      return false
    }

    // Check if token is expired
    const expiryTime = parseInt(expiry, 10)
    const now = Date.now()
    
    return now < expiryTime
  }

  /**
   * Refresh access token using refresh token
   */
  async refreshAccessToken(): Promise<string> {
    // Prevent multiple simultaneous refresh requests
    if (this.refreshPromise) {
      return this.refreshPromise
    }

    this.refreshPromise = this._doRefresh()
    
    try {
      const token = await this.refreshPromise
      return token
    } finally {
      this.refreshPromise = null
    }
  }

  private async _doRefresh(): Promise<string> {
    const refreshToken = this.getRefreshToken()

    if (!refreshToken) {
      throw new Error('No refresh token available')
    }

    try {
      const response = await fetch(`${this.getApiUrl()}/auth/refresh`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token: refreshToken }),
      })

      if (!response.ok) {
        throw new Error('Token refresh failed')
      }

      const data: LoginResponse = await response.json()
      this.setTokens(data.access_token, data.refresh_token, data.expires_in)

      return data.access_token
    } catch (error) {
      console.error('Token refresh failed:', error)
      this.clearTokens()
      throw error
    }
  }

  /**
   * Make authenticated API request with automatic token refresh
   */
  async authenticatedFetch(endpoint: string, options: RequestInit = {}): Promise<Response> {
    let token = this.getAccessToken()

    // Check if token needs refresh (within 5 minutes of expiry)
    const expiry = localStorage.getItem(TOKEN_EXPIRY_KEY)
    if (expiry) {
      const expiryTime = parseInt(expiry, 10)
      const now = Date.now()
      const fiveMinutes = 5 * 60 * 1000

      if (now >= expiryTime - fiveMinutes) {
        try {
          token = await this.refreshAccessToken()
        } catch (error) {
          console.error('Failed to refresh token:', error)
          throw new Error('Authentication required')
        }
      }
    }

    if (!token) {
      throw new Error('No access token available')
    }

    const headers = {
      ...options.headers,
      Authorization: `Bearer ${token}`,
    }

    const response = await fetch(`${this.getApiUrl()}${endpoint}`, {
      ...options,
      headers,
    })

    // If 401, try to refresh token and retry once
    if (response.status === 401) {
      try {
        token = await this.refreshAccessToken()
        
        const retryHeaders = {
          ...options.headers,
          Authorization: `Bearer ${token}`,
        }

        return fetch(`${this.getApiUrl()}${endpoint}`, {
          ...options,
          headers: retryHeaders,
        })
      } catch (error) {
        this.clearTokens()
        throw new Error('Authentication failed')
      }
    }

    return response
  }

  /**
   * Store tokens in localStorage
   */
  private setTokens(accessToken: string, refreshToken: string, expiresIn: number): void {
    localStorage.setItem(ACCESS_TOKEN_KEY, accessToken)
    localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken)
    
    // Calculate expiry time (current time + expires_in seconds)
    const expiryTime = Date.now() + (expiresIn * 1000)
    localStorage.setItem(TOKEN_EXPIRY_KEY, expiryTime.toString())
  }

  /**
   * Clear all tokens from storage
   */
  private clearTokens(): void {
    localStorage.removeItem(ACCESS_TOKEN_KEY)
    localStorage.removeItem(REFRESH_TOKEN_KEY)
    localStorage.removeItem(TOKEN_EXPIRY_KEY)
    localStorage.removeItem(USER_EMAIL_KEY)
  }

  /**
   * Get API base URL
   */
  private getApiUrl(): string {
    // Check environment variable first
    if (import.meta.env.VITE_API_URL) {
      return import.meta.env.VITE_API_URL
    }
    
    // For production deployment on tilyn.ai
    if (typeof window !== 'undefined' && window.location.hostname === 'tilyn.ai') {
      return 'https://tilyn.ai/api'
    }
    
    // Local development fallback
    return 'http://localhost:8000'
  }

  /**
   * Get stored user email
   */
  getUserEmail(): string | null {
    return localStorage.getItem(USER_EMAIL_KEY)
  }
}

// Export singleton instance
export const authService = new AuthService()
