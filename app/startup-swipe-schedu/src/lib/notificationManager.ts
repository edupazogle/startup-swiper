/**
 * Push Notification Manager
 * Handles PWA push notification subscriptions and permissions
 */

const API_BASE_URL = (import.meta as any).env?.VITE_API_URL || 
  (typeof window !== 'undefined' && window.location.hostname === 'tilyn.ai' 
    ? 'https://tilyn.ai' 
    : 'http://localhost:8000');

export class NotificationManager {
  private userId: string;
  private registration: ServiceWorkerRegistration | null = null;

  constructor(userId: string) {
    this.userId = userId;
  }

  /**
   * Initialize service worker and check notification support
   */
  async init(): Promise<boolean> {
    if (!('serviceWorker' in navigator)) {
      console.warn('Service Workers not supported');
      return false;
    }

    if (!('PushManager' in window)) {
      console.warn('Push notifications not supported');
      return false;
    }

    try {
      // Service worker completely removed
      console.log('Service Worker disabled');
      this.registration = null;

      // Wait for service worker to be ready
      await navigator.serviceWorker.ready;

      // Listen for messages from service worker (for deep linking)
      navigator.serviceWorker.addEventListener('message', this.handleServiceWorkerMessage);

      return true;
    } catch (error) {
      console.error('Service Worker registration failed:', error);
      return false;
    }
  }

  /**
   * Handle messages from service worker (for navigation/deep linking)
   */
  private handleServiceWorkerMessage = (event: MessageEvent) => {
    const { type, url } = event.data;

    if (type === 'NAVIGATE' && url) {
      // Parse URL and navigate within app
      const urlObj = new URL(url, window.location.origin);
      const params = new URLSearchParams(urlObj.search);
      
      const view = params.get('view');
      const meetingId = params.get('meeting');
      const action = params.get('action');

      // Dispatch custom event for app to handle navigation
      window.dispatchEvent(new CustomEvent('notification-navigate', {
        detail: { view, meetingId, action }
      }));
    }
  };

  /**
   * Check current notification permission status
   */
  getPermissionStatus(): NotificationPermission {
    return Notification.permission;
  }

  /**
   * Check if notifications are supported and enabled
   */
  isNotificationSupported(): boolean {
    return 'Notification' in window && 'serviceWorker' in navigator;
  }

  /**
   * Request notification permission from user
   */
  async requestPermission(): Promise<NotificationPermission> {
    if (!this.isNotificationSupported()) {
      throw new Error('Notifications not supported');
    }

    const permission = await Notification.requestPermission();
    console.log('Notification permission:', permission);

    if (permission === 'granted') {
      // Subscribe to push notifications
      await this.subscribeToPush();
    }

    return permission;
  }

  /**
   * Subscribe to push notifications
   */
  async subscribeToPush(): Promise<boolean> {
    if (!this.registration) {
      console.error('Service worker not registered');
      return false;
    }

    try {
      // Get VAPID public key from server
      const response = await fetch(`${API_BASE_URL}/notifications/vapid-public-key`);
      if (!response.ok) {
        console.error('Failed to get VAPID public key');
        return false;
      }

      const { publicKey } = await response.json();

      // Subscribe to push notifications
      const subscription = await this.registration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: this.urlBase64ToUint8Array(publicKey) as any
      });

      console.log('Push subscription:', subscription);

      // Send subscription to server
      const subscriptionData = {
        endpoint: subscription.endpoint,
        keys: {
          p256dh: arrayBufferToBase64(subscription.getKey('p256dh')!),
          auth: arrayBufferToBase64(subscription.getKey('auth')!)
        },
        userAgent: navigator.userAgent
      };

      const saveResponse = await fetch(
        `${API_BASE_URL}/notifications/push/subscribe?user_id=${this.userId}`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(subscriptionData)
        }
      );

      if (!saveResponse.ok) {
        console.error('Failed to save subscription to server');
        return false;
      }

      console.log('Push subscription saved to server');
      return true;

    } catch (error) {
      console.error('Failed to subscribe to push notifications:', error);
      return false;
    }
  }

  /**
   * Unsubscribe from push notifications
   */
  async unsubscribe(): Promise<boolean> {
    if (!this.registration) {
      return false;
    }

    try {
      const subscription = await this.registration.pushManager.getSubscription();
      if (!subscription) {
        return true; // Already unsubscribed
      }

      // Unsubscribe from push
      await subscription.unsubscribe();

      // Notify server
      await fetch(`${API_BASE_URL}/notifications/push/unsubscribe`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ endpoint: subscription.endpoint })
      });

      console.log('Unsubscribed from push notifications');
      return true;

    } catch (error) {
      console.error('Failed to unsubscribe:', error);
      return false;
    }
  }

  /**
   * Get current push subscription status
   */
  async getSubscription(): Promise<PushSubscription | null> {
    if (!this.registration) {
      return null;
    }

    return await this.registration.pushManager.getSubscription();
  }

  /**
   * Show a local notification (for testing)
   */
  async showLocalNotification(title: string, options?: NotificationOptions): Promise<void> {
    if (!this.registration) {
      throw new Error('Service worker not registered');
    }

    if (Notification.permission !== 'granted') {
      throw new Error('Notification permission not granted');
    }

    await this.registration.showNotification(title, {
      icon: '/icon-192.png',
      badge: '/badge-72.png',
      ...options
    });
  }

  /**
   * Convert VAPID key to Uint8Array
   */
  private urlBase64ToUint8Array(base64String: string): Uint8Array {
    const padding = '='.repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding)
      .replace(/\-/g, '+')
      .replace(/_/g, '/');

    const rawData = window.atob(base64);
    const outputArray = new Uint8Array(rawData.length);

    for (let i = 0; i < rawData.length; ++i) {
      outputArray[i] = rawData.charCodeAt(i);
    }
    return outputArray;
  }
}

/**
 * Convert ArrayBuffer to Base64
 */
function arrayBufferToBase64(buffer: ArrayBuffer): string {
  const bytes = new Uint8Array(buffer);
  let binary = '';
  for (let i = 0; i < bytes.byteLength; i++) {
    binary += String.fromCharCode(bytes[i]);
  }
  return window.btoa(binary);
}

/**
 * API functions for managing meeting insights
 */
export const InsightsAPI = {
  /**
   * Submit a meeting insight
   */
  async submitInsight(insight: {
    meetingId: string;
    userId: string;
    startupId?: string;
    startupName?: string;
    insight: string;
    tags?: string[];
    rating?: number;
    followUp?: boolean;
  }): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/insights/submit`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(insight)
    });

    if (!response.ok) {
      throw new Error('Failed to submit insight');
    }

    return response.json();
  },

  /**
   * Get pending insights for a user
   */
  async getPendingInsights(userId: string): Promise<any[]> {
    const response = await fetch(`${API_BASE_URL}/insights/pending/${userId}`);
    
    if (!response.ok) {
      throw new Error('Failed to get pending insights');
    }

    const data = await response.json();
    return data.pending || [];
  },

  /**
   * Get all insights for a user
   */
  async getUserInsights(userId: string): Promise<any[]> {
    const response = await fetch(`${API_BASE_URL}/insights/user/${userId}`);
    
    if (!response.ok) {
      throw new Error('Failed to get user insights');
    }

    return response.json();
  },

  /**
   * Schedule a notification for a meeting
   */
  async scheduleNotification(
    meetingId: string,
    userId: string,
    meetingEndTime: string
  ): Promise<any> {
    const response = await fetch(
      `${API_BASE_URL}/notifications/schedule?meeting_id=${meetingId}&user_id=${userId}&meeting_end_time=${encodeURIComponent(meetingEndTime)}`,
      { method: 'POST' }
    );

    if (!response.ok) {
      throw new Error('Failed to schedule notification');
    }

    return response.json();
  },

  /**
   * Dismiss a notification
   */
  async dismissNotification(notificationId: number, userId: string): Promise<void> {
    const response = await fetch(
      `${API_BASE_URL}/notifications/dismiss/${notificationId}?user_id=${userId}`,
      { method: 'POST' }
    );

    if (!response.ok) {
      throw new Error('Failed to dismiss notification');
    }
  }
};
