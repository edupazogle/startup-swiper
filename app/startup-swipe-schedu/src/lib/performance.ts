/**
 * Performance monitoring utilities for tracking modal performance
 */

interface PerformanceMetrics {
  modalOpenTime: number
  contentLoadTime: number
  firstInteractionTime: number
  apiResponseTime: number
}

class PerformanceMonitor {
  private metrics: Map<string, number> = new Map()
  private enabled = import.meta.env.DEV

  /**
   * Mark the start of a performance measurement
   */
  mark(name: string): void {
    if (!this.enabled) return
    this.metrics.set(name, performance.now())
  }

  /**
   * Measure time since mark was set
   */
  measure(name: string): number {
    if (!this.enabled) return 0
    
    const startTime = this.metrics.get(name)
    if (!startTime) {
      console.warn(`No mark found for: ${name}`)
      return 0
    }

    const duration = performance.now() - startTime
    this.metrics.delete(name)
    
    return duration
  }

  /**
   * Log performance metric
   */
  log(label: string, duration: number): void {
    if (!this.enabled) return
    
    const color = duration < 100 ? 'green' : duration < 1000 ? 'orange' : 'red'
    console.log(
      `%c⚡ ${label}: ${duration.toFixed(2)}ms`,
      `color: ${color}; font-weight: bold`
    )
  }

  /**
   * Measure and log in one call
   */
  measureAndLog(name: string, label?: string): void {
    const duration = this.measure(name)
    this.log(label || name, duration)
  }

  /**
   * Get Web Vitals if available
   */
  getWebVitals(): void {
    if (!this.enabled) return

    // First Contentful Paint
    const paintEntries = performance.getEntriesByType('paint')
    paintEntries.forEach((entry) => {
      console.log(`%c${entry.name}: ${entry.startTime.toFixed(2)}ms`, 'color: blue')
    })

    // Largest Contentful Paint
    try {
      const observer = new PerformanceObserver((list) => {
        const entries = list.getEntries()
        const lastEntry = entries[entries.length - 1]
        console.log(
          `%cLargest Contentful Paint: ${lastEntry.startTime.toFixed(2)}ms`,
          'color: blue'
        )
      })
      observer.observe({ entryTypes: ['largest-contentful-paint'] })
    } catch (e) {
      // LCP not supported
    }
  }

  /**
   * Track network timing for API calls
   */
  trackAPI(url: string, startTime: number): void {
    if (!this.enabled) return
    
    const duration = performance.now() - startTime
    this.log(`API: ${url}`, duration)
    
    if (duration > 5000) {
      console.warn(`⚠️ Slow API call detected: ${url} took ${duration.toFixed(2)}ms`)
    }
  }

  /**
   * Check if user is on slow connection
   */
  isSlowConnection(): boolean {
    if ('connection' in navigator) {
      const conn = (navigator as any).connection
      const effectiveType = conn?.effectiveType
      
      // 2G or slow-2g is considered slow
      return effectiveType === '2g' || effectiveType === 'slow-2g'
    }
    return false
  }

  /**
   * Get network info
   */
  getNetworkInfo(): string {
    if ('connection' in navigator) {
      const conn = (navigator as any).connection
      return conn?.effectiveType || 'unknown'
    }
    return 'unknown'
  }

  /**
   * Log initial page load metrics
   */
  logPageLoad(): void {
    if (!this.enabled) return

    window.addEventListener('load', () => {
      setTimeout(() => {
        const perfData = performance.getEntriesByType('navigation')[0] as any
        
        if (perfData) {
          console.group('📊 Page Load Performance')
          console.log(`DNS Lookup: ${(perfData.domainLookupEnd - perfData.domainLookupStart).toFixed(2)}ms`)
          console.log(`TCP Connection: ${(perfData.connectEnd - perfData.connectStart).toFixed(2)}ms`)
          console.log(`Request: ${(perfData.responseStart - perfData.requestStart).toFixed(2)}ms`)
          console.log(`Response: ${(perfData.responseEnd - perfData.responseStart).toFixed(2)}ms`)
          console.log(`DOM Processing: ${(perfData.domComplete - perfData.domLoading).toFixed(2)}ms`)
          console.log(`Load Complete: ${(perfData.loadEventEnd - perfData.loadEventStart).toFixed(2)}ms`)
          console.log(`Network: ${this.getNetworkInfo()}`)
          console.groupEnd()
        }
      }, 0)
    })
  }
}

export const performanceMonitor = new PerformanceMonitor()

// Start monitoring page load
performanceMonitor.logPageLoad()

// Helper hook for React components
export function usePerformanceMonitor(componentName: string) {
  const mark = (action: string) => {
    performanceMonitor.mark(`${componentName}.${action}`)
  }

  const measureAndLog = (action: string) => {
    performanceMonitor.measureAndLog(
      `${componentName}.${action}`,
      `${componentName} - ${action}`
    )
  }

  return { mark, measureAndLog }
}
