"""
Notification Service for Post-Meeting Insights
Handles scheduling, sending, and tracking of push notifications
"""
import asyncio
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from pywebpush import webpush, WebPushException
import os
from dotenv import load_dotenv

from models import NotificationQueue, PushSubscription, MeetingInsight, CalendarEvent
from database import SessionLocal

load_dotenv()

# VAPID keys for web push (generate these for production)
VAPID_PRIVATE_KEY = os.getenv("VAPID_PRIVATE_KEY", "")
VAPID_PUBLIC_KEY = os.getenv("VAPID_PUBLIC_KEY", "")
VAPID_CLAIMS = {
    "sub": "mailto:support@slush2025.com"
}

class NotificationService:
    """Service to manage post-meeting insight notifications"""
    
    def __init__(self):
        self.notification_delay_minutes = 5  # Send notification 5 minutes after meeting ends
    
    async def schedule_meeting_insight_notification(
        self,
        db: Session,
        user_id: str,
        meeting_id: str,
        meeting_end_time: datetime
    ) -> NotificationQueue:
        """
        Schedule a notification to be sent 5 minutes after a meeting ends
        
        Args:
            db: Database session
            user_id: User ID to notify
            meeting_id: Calendar event ID of the meeting
            meeting_end_time: When the meeting ends
            
        Returns:
            NotificationQueue object
        """
        scheduled_for = meeting_end_time + timedelta(minutes=self.notification_delay_minutes)
        
        # Check if notification already scheduled
        existing = db.query(NotificationQueue).filter(
            NotificationQueue.meetingId == meeting_id,
            NotificationQueue.userId == user_id
        ).first()
        
        if existing:
            # Update existing notification
            existing.meetingEndTime = meeting_end_time
            existing.scheduledFor = scheduled_for
            existing.sent = False
            existing.dismissed = False
            db.commit()
            db.refresh(existing)
            return existing
        
        # Create new notification
        notification = NotificationQueue(
            userId=user_id,
            meetingId=meeting_id,
            meetingEndTime=meeting_end_time,
            scheduledFor=scheduled_for
        )
        db.add(notification)
        db.commit()
        db.refresh(notification)
        
        return notification
    
    async def send_pending_notifications(self, db: Session) -> int:
        """
        Check for pending notifications and send them if it's time
        Should be called periodically (e.g., every minute)
        
        Returns:
            Number of notifications sent
        """
        now = datetime.utcnow()
        
        # Find notifications that should be sent
        pending = db.query(NotificationQueue).filter(
            NotificationQueue.sent == False,
            NotificationQueue.dismissed == False,
            NotificationQueue.insightSubmitted == False,
            NotificationQueue.scheduledFor <= now
        ).all()
        
        sent_count = 0
        
        for notification in pending:
            # Get meeting details
            meeting = db.query(CalendarEvent).filter(
                CalendarEvent.id == int(notification.meetingId) if notification.meetingId.isdigit() else -1
            ).first()
            
            meeting_title = meeting.title if meeting else "your meeting"
            
            # Get user's push subscriptions
            subscriptions = db.query(PushSubscription).filter(
                PushSubscription.userId == notification.userId,
                PushSubscription.active == True
            ).all()
            
            if subscriptions:
                # Send push notification to all user's devices
                success = await self._send_push_notification(
                    subscriptions=subscriptions,
                    notification_data={
                        "title": "🎯 Share Your Insight",
                        "body": f"How was {meeting_title}? Share one key insight!",
                        "icon": "/icon-192.png",
                        "badge": "/badge-72.png",
                        "tag": f"meeting-insight-{notification.meetingId}",
                        "requireInteraction": True,
                        "data": {
                            "meetingId": notification.meetingId,
                            "url": f"/?view=insights&meeting={notification.meetingId}",
                            "action": "submit-insight"
                        },
                        "actions": [
                            {
                                "action": "submit",
                                "title": "Share Insight"
                            },
                            {
                                "action": "dismiss",
                                "title": "Later"
                            }
                        ]
                    }
                )
                
                if success:
                    notification.sent = True
                    notification.sentAt = datetime.utcnow()
                    sent_count += 1
            
            db.commit()
        
        return sent_count
    
    async def _send_push_notification(
        self,
        subscriptions: List[PushSubscription],
        notification_data: Dict[str, Any]
    ) -> bool:
        """
        Send a push notification to multiple subscriptions
        
        Args:
            subscriptions: List of push subscriptions
            notification_data: Notification payload
            
        Returns:
            True if at least one notification was sent successfully
        """
        if not VAPID_PRIVATE_KEY or not VAPID_PUBLIC_KEY:
            print("Warning: VAPID keys not configured. Push notifications disabled.")
            return False
        
        success = False
        
        for subscription in subscriptions:
            try:
                subscription_info = {
                    "endpoint": subscription.endpoint,
                    "keys": {
                        "p256dh": subscription.p256dh,
                        "auth": subscription.auth
                    }
                }
                
                webpush(
                    subscription_info=subscription_info,
                    data=json.dumps(notification_data),
                    vapid_private_key=VAPID_PRIVATE_KEY,
                    vapid_claims=VAPID_CLAIMS
                )
                
                subscription.lastUsed = datetime.utcnow()
                success = True
                
            except WebPushException as e:
                print(f"Failed to send push notification: {e}")
                if e.response and e.response.status_code == 410:
                    # Subscription expired
                    subscription.active = False
            except Exception as e:
                print(f"Error sending push notification: {e}")
        
        return success
    
    async def dismiss_notification(
        self,
        db: Session,
        notification_id: int,
        user_id: str
    ) -> bool:
        """
        Dismiss a notification (user clicked 'Later')
        
        Args:
            db: Database session
            notification_id: Notification ID
            user_id: User ID (for security)
            
        Returns:
            True if dismissed successfully
        """
        notification = db.query(NotificationQueue).filter(
            NotificationQueue.id == notification_id,
            NotificationQueue.userId == user_id
        ).first()
        
        if notification:
            notification.dismissed = True
            db.commit()
            return True
        
        return False
    
    async def mark_insight_submitted(
        self,
        db: Session,
        meeting_id: str,
        user_id: str
    ) -> bool:
        """
        Mark that an insight was submitted for a meeting
        This will prevent further notifications
        
        Args:
            db: Database session
            meeting_id: Meeting ID
            user_id: User ID
            
        Returns:
            True if marked successfully
        """
        notification = db.query(NotificationQueue).filter(
            NotificationQueue.meetingId == meeting_id,
            NotificationQueue.userId == user_id
        ).first()
        
        if notification:
            notification.insightSubmitted = True
            db.commit()
            return True
        
        return False
    
    async def get_pending_insights(
        self,
        db: Session,
        user_id: str
    ) -> List[Dict[str, Any]]:
        """
        Get list of meetings waiting for insights
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            List of meetings needing insights
        """
        notifications = db.query(NotificationQueue).filter(
            NotificationQueue.userId == user_id,
            NotificationQueue.insightSubmitted == False,
            NotificationQueue.dismissed == False
        ).all()
        
        results = []
        for notification in notifications:
            # Get meeting details
            meeting = db.query(CalendarEvent).filter(
                CalendarEvent.id == int(notification.meetingId) if notification.meetingId.isdigit() else -1
            ).first()
            
            # Check if insight already exists
            existing_insight = db.query(MeetingInsight).filter(
                MeetingInsight.meetingId == notification.meetingId,
                MeetingInsight.userId == user_id
            ).first()
            
            if not existing_insight and meeting:
                results.append({
                    "notificationId": notification.id,
                    "meetingId": notification.meetingId,
                    "meetingTitle": meeting.title,
                    "meetingEndTime": notification.meetingEndTime.isoformat(),
                    "scheduledFor": notification.scheduledFor.isoformat(),
                    "sent": notification.sent
                })
        
        return results
    
    def subscribe_to_push(
        self,
        db: Session,
        user_id: str,
        subscription_data: Dict[str, Any]
    ) -> PushSubscription:
        """
        Register a push notification subscription
        
        Args:
            db: Database session
            user_id: User ID
            subscription_data: Push subscription details from browser
            
        Returns:
            PushSubscription object
        """
        # Check if subscription already exists
        existing = db.query(PushSubscription).filter(
            PushSubscription.endpoint == subscription_data["endpoint"]
        ).first()
        
        if existing:
            # Update existing subscription
            existing.userId = user_id
            existing.p256dh = subscription_data["keys"]["p256dh"]
            existing.auth = subscription_data["keys"]["auth"]
            existing.active = True
            existing.lastUsed = datetime.utcnow()
            db.commit()
            db.refresh(existing)
            return existing
        
        # Create new subscription
        subscription = PushSubscription(
            userId=user_id,
            endpoint=subscription_data["endpoint"],
            p256dh=subscription_data["keys"]["p256dh"],
            auth=subscription_data["keys"]["auth"],
            userAgent=subscription_data.get("userAgent")
        )
        db.add(subscription)
        db.commit()
        db.refresh(subscription)
        
        return subscription
    
    def unsubscribe_from_push(
        self,
        db: Session,
        endpoint: str
    ) -> bool:
        """
        Unregister a push notification subscription
        
        Args:
            db: Database session
            endpoint: Subscription endpoint
            
        Returns:
            True if unsubscribed successfully
        """
        subscription = db.query(PushSubscription).filter(
            PushSubscription.endpoint == endpoint
        ).first()
        
        if subscription:
            subscription.active = False
            db.commit()
            return True
        
        return False


# Background task to send notifications periodically
async def notification_worker():
    """
    Background worker that checks for pending notifications every minute
    Should be run as a separate async task
    """
    service = NotificationService()
    
    while True:
        try:
            db = SessionLocal()
            sent_count = await service.send_pending_notifications(db)
            if sent_count > 0:
                print(f"Sent {sent_count} insight reminder notifications")
            db.close()
        except Exception as e:
            print(f"Error in notification worker: {e}")
        
        # Wait 1 minute before checking again
        await asyncio.sleep(60)
