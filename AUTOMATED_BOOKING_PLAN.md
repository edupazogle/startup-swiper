# Automated Meeting Booking System - Implementation Plan

## Executive Summary

Implement an intelligent agent that automatically books meetings with startups using Selenium automation. When a user clicks "Book Meeting", the system:

1. **Launches Selenium** to navigate the startup's booking platform
2. **Selects available person** from the startup team
3. **Finds matching time slots** for both parties
4. **Sends personalized message** with AXA Venture Client introduction
5. **Monitors confirmation status** (checks every minute)
6. **Auto-adds to calendar** once confirmed

---

## 🤖 System Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                   Automated Meeting Booking Flow                  │
├──────────────────────────────────────────────────────────────────┤
│                                                                    │
│  User clicks "Book Meeting" button                                │
│         ↓                                                          │
│  [PENDING] Button shows "Booking... ⏳"                           │
│         ↓                                                          │
│  Launch Selenium Agent                                             │
│         ↓                                                          │
│  ┌──────────────────────────────────────────┐                    │
│  │  Selenium Automation Steps:              │                    │
│  │  1. Navigate to booking platform         │                    │
│  │  2. Select available person from startup │                    │
│  │  3. Check availability calendars         │                    │
│  │  4. Find 2 matching time slots           │                    │
│  │  5. Fill booking form with details       │                    │
│  │  6. Enter AXA message                    │                    │
│  │  7. Submit booking request               │                    │
│  └──────────────────────────────────────────┘                    │
│         ↓                                                          │
│  Button shows "Pending Confirmation ⏳"                           │
│         ↓                                                          │
│  Background Worker (checks every minute)                           │
│         ↓                                                          │
│  Check confirmation status via:                                    │
│    • Email monitoring                                              │
│    • Platform API polling                                          │
│    • Selenium status check                                         │
│         ↓                                                          │
│  ┌──────────────┬─────────────────┐                              │
│  │  Confirmed?  │  Still Pending  │                              │
│  └──────────────┴─────────────────┘                              │
│         ↓                  ↓                                       │
│  Add to Calendar    Keep checking                                 │
│  Button: "✓ Booked"    (max 24 hours)                            │
│  Send notification                                                 │
│                                                                    │
└──────────────────────────────────────────────────────────────────┘
```

---

## 📊 Data Models

### 1. Meeting Booking Request

```python
# models.py additions

class MeetingBookingStatus(str, Enum):
    PENDING = "pending"  # Initiated
    BOOKING_IN_PROGRESS = "booking_in_progress"  # Selenium running
    PENDING_CONFIRMATION = "pending_confirmation"  # Waiting for startup to confirm
    CONFIRMED = "confirmed"  # Confirmed by startup
    ADDED_TO_CALENDAR = "added_to_calendar"  # Added to user calendar
    FAILED = "failed"  # Booking failed
    CANCELLED = "cancelled"  # User cancelled

class BookingPlatform(str, Enum):
    CALENDLY = "calendly"
    CAL_COM = "cal.com"
    HUBSPOT_MEETINGS = "hubspot_meetings"
    CHILI_PIPER = "chili_piper"
    SLUSH_PLATFORM = "slush_platform"
    CUSTOM = "custom"

class MeetingBookingRequest(Base):
    __tablename__ = "meeting_booking_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    startup_id = Column(String, ForeignKey("startups_enhanced.startup_id"), index=True)
    
    # Request Details
    status = Column(String, default=MeetingBookingStatus.PENDING, index=True)
    
    # Booking Platform Info
    booking_platform = Column(String)  # calendly, cal.com, etc.
    booking_url = Column(String)  # URL to booking page
    
    # Selected Options
    selected_person_name = Column(String, nullable=True)
    selected_person_email = Column(String, nullable=True)
    selected_person_role = Column(String, nullable=True)
    
    # Time Slots (proposed)
    proposed_slot_1_datetime = Column(DateTime, nullable=True)
    proposed_slot_2_datetime = Column(DateTime, nullable=True)
    confirmed_slot_datetime = Column(DateTime, nullable=True)
    
    # Message sent
    message_template = Column(Text)
    message_sent = Column(Text)
    
    # Selenium Session Info
    selenium_session_id = Column(String, nullable=True)
    selenium_screenshots = Column(JSON, default=list)  # Screenshots of the process
    
    # Confirmation Tracking
    confirmation_check_count = Column(Integer, default=0)
    last_confirmation_check = Column(DateTime, nullable=True)
    confirmation_method = Column(String, nullable=True)  # email, api, platform_check
    confirmation_received_at = Column(DateTime, nullable=True)
    
    # External References
    external_booking_id = Column(String, nullable=True)  # ID from booking platform
    calendar_event_id = Column(String, nullable=True)  # Google/Outlook calendar ID
    
    # User Info for booking
    user_name = Column(String)
    user_email = Column(String)
    user_company = Column(String, default="AXA Innovation")
    user_role = Column(String, default="Venture Client Team")
    
    # Error Handling
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    booking_started_at = Column(DateTime, nullable=True)
    booking_completed_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

### 2. Booking Platform Configuration

```python
class StartupBookingConfig(Base):
    __tablename__ = "startup_booking_configs"
    
    id = Column(Integer, primary_key=True)
    startup_id = Column(String, ForeignKey("startups_enhanced.startup_id"), unique=True)
    
    # Platform Details
    platform_type = Column(String)  # calendly, cal.com, etc.
    booking_url = Column(String)
    
    # Available Team Members
    available_people = Column(JSON)  # [{"name": "John Doe", "role": "CEO", "email": "john@startup.com"}]
    
    # Automation Selectors (for Selenium)
    selectors = Column(JSON)  # CSS/XPath selectors for automation
    # Example: {
    #   "person_dropdown": "#person-select",
    #   "time_slots": ".time-slot-button",
    #   "message_field": "#booking-message",
    #   "submit_button": "button[type='submit']"
    # }
    
    # Special Instructions
    automation_notes = Column(Text, nullable=True)
    requires_auth = Column(Boolean, default=False)
    
    # Success Indicators
    success_indicators = Column(JSON)  # Elements that indicate successful booking
    
    # Metadata
    last_tested = Column(DateTime, nullable=True)
    is_working = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

---

## 🤖 Selenium Booking Agent

```python
# selenium_booking_agent.py

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from datetime import datetime, timedelta
import time
import logging
from typing import Optional, Dict, List
import json

logger = logging.getLogger(__name__)

class SeleniumBookingAgent:
    """
    Automated meeting booking agent using Selenium
    """
    
    DEFAULT_MESSAGE = """Hello, my name is {user_name} from the Venture Clienting team at AXA Innovation. 

We are visiting Slush as a team with several AXA entity stakeholders, IT team and representatives from business. 

Our goal as the Venture Client unit is to showcase how startups can deliver the value we need. 

Thanks!"""
    
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.driver = None
        self.screenshots = []
        
    def initialize_driver(self):
        """Initialize Selenium WebDriver"""
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument('--headless')
        
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.implicitly_wait(10)
        
        logger.info("Selenium WebDriver initialized")
    
    def take_screenshot(self, name: str) -> str:
        """Take screenshot and return path"""
        if not self.driver:
            return None
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshots/booking_{name}_{timestamp}.png"
        
        try:
            self.driver.save_screenshot(filename)
            self.screenshots.append(filename)
            logger.info(f"Screenshot saved: {filename}")
            return filename
        except Exception as e:
            logger.error(f"Failed to take screenshot: {e}")
            return None
    
    def book_meeting(
        self,
        booking_request: MeetingBookingRequest,
        booking_config: StartupBookingConfig,
        user_availability: List[Dict]
    ) -> Dict:
        """
        Main method to book a meeting
        """
        try:
            self.initialize_driver()
            
            # Step 1: Navigate to booking page
            result = self._navigate_to_booking_page(booking_config.booking_url)
            if not result["success"]:
                return result
            
            # Step 2: Select team member
            result = self._select_team_member(booking_config)
            if not result["success"]:
                return result
            
            # Step 3: Find matching time slots
            result = self._find_matching_time_slots(
                booking_config,
                user_availability
            )
            if not result["success"]:
                return result
            
            # Step 4: Fill booking form
            result = self._fill_booking_form(
                booking_request,
                booking_config
            )
            if not result["success"]:
                return result
            
            # Step 5: Submit booking
            result = self._submit_booking(booking_config)
            if not result["success"]:
                return result
            
            return {
                "success": True,
                "message": "Booking submitted successfully",
                "screenshots": self.screenshots,
                "selected_person": result.get("selected_person"),
                "proposed_slots": result.get("proposed_slots"),
                "booking_id": result.get("booking_id")
            }
            
        except Exception as e:
            logger.error(f"Booking failed: {e}")
            self.take_screenshot("error")
            return {
                "success": False,
                "error": str(e),
                "screenshots": self.screenshots
            }
        
        finally:
            if self.driver:
                self.driver.quit()
    
    def _navigate_to_booking_page(self, url: str) -> Dict:
        """Navigate to the booking platform"""
        try:
            logger.info(f"Navigating to: {url}")
            self.driver.get(url)
            time.sleep(3)  # Wait for page load
            
            self.take_screenshot("page_loaded")
            
            return {"success": True}
        
        except Exception as e:
            logger.error(f"Failed to navigate: {e}")
            return {"success": False, "error": str(e)}
    
    def _select_team_member(self, booking_config: StartupBookingConfig) -> Dict:
        """Select an available team member"""
        try:
            available_people = booking_config.available_people
            
            if not available_people:
                logger.warning("No team members configured")
                return {
                    "success": True,
                    "selected_person": None,
                    "message": "No team member selection required"
                }
            
            selectors = booking_config.selectors or {}
            person_selector = selectors.get("person_dropdown") or selectors.get("person_button")
            
            if person_selector:
                # Wait for person selector to be available
                wait = WebDriverWait(self.driver, 15)
                element = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, person_selector))
                )
                
                # Click on first available person
                element.click()
                time.sleep(2)
                
                self.take_screenshot("person_selected")
                
                selected = available_people[0] if available_people else {}
                logger.info(f"Selected team member: {selected.get('name')}")
                
                return {
                    "success": True,
                    "selected_person": selected
                }
            
            return {
                "success": True,
                "selected_person": available_people[0] if available_people else None
            }
        
        except Exception as e:
            logger.error(f"Failed to select team member: {e}")
            return {"success": False, "error": str(e)}
    
    def _find_matching_time_slots(
        self,
        booking_config: StartupBookingConfig,
        user_availability: List[Dict]
    ) -> Dict:
        """Find 2 matching time slots"""
        try:
            selectors = booking_config.selectors or {}
            time_slot_selector = selectors.get("time_slots", ".time-slot")
            
            # Wait for time slots to load
            wait = WebDriverWait(self.driver, 20)
            wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, time_slot_selector))
            )
            
            time.sleep(2)  # Let calendar fully load
            
            # Get all available time slots
            time_slot_elements = self.driver.find_elements(By.CSS_SELECTOR, time_slot_selector)
            
            logger.info(f"Found {len(time_slot_elements)} available time slots")
            
            # Extract time slot data
            available_slots = []
            for element in time_slot_elements[:10]:  # Check first 10 slots
                try:
                    time_text = element.text
                    # Parse time from text (format varies by platform)
                    # This is a simplified version
                    available_slots.append({
                        "element": element,
                        "time_text": time_text,
                        "datetime": self._parse_slot_time(time_text)
                    })
                except Exception as e:
                    logger.warning(f"Failed to parse slot: {e}")
                    continue
            
            # Find 2 slots that match user availability
            matching_slots = self._match_slots_with_user_availability(
                available_slots,
                user_availability
            )
            
            if len(matching_slots) < 2:
                logger.warning(f"Only found {len(matching_slots)} matching slots")
            
            # Click on first matching slot to proceed
            if matching_slots:
                matching_slots[0]["element"].click()
                time.sleep(2)
                self.take_screenshot("time_slot_selected")
            
            return {
                "success": True,
                "proposed_slots": matching_slots[:2],
                "available_slot_count": len(available_slots)
            }
        
        except Exception as e:
            logger.error(f"Failed to find time slots: {e}")
            self.take_screenshot("time_slots_error")
            return {"success": False, "error": str(e)}
    
    def _fill_booking_form(
        self,
        booking_request: MeetingBookingRequest,
        booking_config: StartupBookingConfig
    ) -> Dict:
        """Fill out the booking form with user details and message"""
        try:
            selectors = booking_config.selectors or {}
            
            # Fill name
            name_field = selectors.get("name_field", "input[name='name']")
            try:
                name_input = self.driver.find_element(By.CSS_SELECTOR, name_field)
                name_input.clear()
                name_input.send_keys(booking_request.user_name)
                logger.info(f"Filled name: {booking_request.user_name}")
            except NoSuchElementException:
                logger.warning("Name field not found")
            
            # Fill email
            email_field = selectors.get("email_field", "input[name='email']")
            try:
                email_input = self.driver.find_element(By.CSS_SELECTOR, email_field)
                email_input.clear()
                email_input.send_keys(booking_request.user_email)
                logger.info(f"Filled email: {booking_request.user_email}")
            except NoSuchElementException:
                logger.warning("Email field not found")
            
            # Fill message/notes
            message_field = selectors.get("message_field", "textarea[name='notes']")
            try:
                message_input = self.driver.find_element(By.CSS_SELECTOR, message_field)
                message_input.clear()
                
                # Use custom message or default template
                message = booking_request.message_template or self.DEFAULT_MESSAGE.format(
                    user_name=booking_request.user_name
                )
                
                message_input.send_keys(message)
                logger.info("Filled booking message")
                
                # Store the actual message sent
                booking_request.message_sent = message
            except NoSuchElementException:
                logger.warning("Message field not found")
            
            time.sleep(1)
            self.take_screenshot("form_filled")
            
            return {"success": True}
        
        except Exception as e:
            logger.error(f"Failed to fill form: {e}")
            return {"success": False, "error": str(e)}
    
    def _submit_booking(self, booking_config: StartupBookingConfig) -> Dict:
        """Submit the booking form"""
        try:
            selectors = booking_config.selectors or {}
            submit_button_selector = selectors.get(
                "submit_button",
                "button[type='submit'], .submit-button, button:contains('Book'), button:contains('Schedule')"
            )
            
            # Wait for submit button
            wait = WebDriverWait(self.driver, 10)
            submit_button = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, submit_button_selector))
            )
            
            self.take_screenshot("before_submit")
            
            # Click submit
            submit_button.click()
            logger.info("Clicked submit button")
            
            # Wait for confirmation
            time.sleep(5)
            
            self.take_screenshot("after_submit")
            
            # Look for success indicators
            success_indicators = booking_config.success_indicators or []
            success_detected = False
            
            for indicator in success_indicators:
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, indicator)
                    if element:
                        success_detected = True
                        logger.info(f"Success indicator found: {indicator}")
                        break
                except NoSuchElementException:
                    continue
            
            # Try to extract booking ID from confirmation page
            booking_id = self._extract_booking_id()
            
            return {
                "success": True,
                "booking_submitted": True,
                "success_detected": success_detected,
                "booking_id": booking_id
            }
        
        except Exception as e:
            logger.error(f"Failed to submit booking: {e}")
            return {"success": False, "error": str(e)}
    
    def _parse_slot_time(self, time_text: str) -> Optional[datetime]:
        """Parse time slot text to datetime"""
        # This is platform-specific and would need customization
        # For now, return None
        try:
            # Example parsing logic (would vary by platform)
            # "Monday, Nov 18 · 2:00pm" -> datetime
            # This is simplified
            return None
        except Exception:
            return None
    
    def _match_slots_with_user_availability(
        self,
        available_slots: List[Dict],
        user_availability: List[Dict]
    ) -> List[Dict]:
        """Match startup slots with user availability"""
        # Simplified matching logic
        # In production, would compare datetimes
        return available_slots[:2]  # Return first 2 for now
    
    def _extract_booking_id(self) -> Optional[str]:
        """Extract booking ID from confirmation page"""
        try:
            # Try common patterns
            page_text = self.driver.page_source
            
            # Look for booking ID patterns
            import re
            patterns = [
                r'booking[_-]?id[:\s]+([A-Za-z0-9-]+)',
                r'confirmation[_-]?code[:\s]+([A-Za-z0-9-]+)',
                r'reference[:\s]+([A-Za-z0-9-]+)'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    return match.group(1)
            
            return None
        except Exception:
            return None
```

---

## 🔄 Confirmation Monitoring Service

```python
# booking_confirmation_service.py

import asyncio
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class BookingConfirmationService:
    """
    Background service to monitor booking confirmations
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.check_interval = 60  # Check every minute
    
    async def monitor_confirmations(self):
        """
        Continuously monitor pending booking requests
        """
        while True:
            try:
                await self._check_pending_bookings()
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Error in confirmation monitoring: {e}")
                await asyncio.sleep(self.check_interval)
    
    async def _check_pending_bookings(self):
        """
        Check all pending booking requests
        """
        # Get all pending confirmation bookings
        pending_bookings = self.db.query(MeetingBookingRequest).filter(
            MeetingBookingRequest.status == MeetingBookingStatus.PENDING_CONFIRMATION,
            MeetingBookingRequest.created_at > datetime.utcnow() - timedelta(hours=24)
        ).all()
        
        logger.info(f"Checking {len(pending_bookings)} pending bookings")
        
        for booking in pending_bookings:
            try:
                await self._check_booking_status(booking)
            except Exception as e:
                logger.error(f"Error checking booking {booking.id}: {e}")
    
    async def _check_booking_status(self, booking: MeetingBookingRequest):
        """
        Check status of a single booking
        """
        booking.confirmation_check_count += 1
        booking.last_confirmation_check = datetime.utcnow()
        
        # Try different confirmation methods
        confirmed = False
        
        # Method 1: Check email for confirmation
        if not confirmed:
            confirmed = await self._check_email_confirmation(booking)
            if confirmed:
                booking.confirmation_method = "email"
        
        # Method 2: Check booking platform API
        if not confirmed:
            confirmed = await self._check_platform_api(booking)
            if confirmed:
                booking.confirmation_method = "api"
        
        # Method 3: Selenium platform check
        if not confirmed and booking.confirmation_check_count % 5 == 0:
            # Check via Selenium every 5 checks (5 minutes)
            confirmed = await self._check_platform_selenium(booking)
            if confirmed:
                booking.confirmation_method = "selenium"
        
        if confirmed:
            booking.status = MeetingBookingStatus.CONFIRMED
            booking.confirmation_received_at = datetime.utcnow()
            
            # Add to calendar
            await self._add_to_calendar(booking)
            
            # Send notification to user
            await self._notify_user(booking)
            
            logger.info(f"Booking {booking.id} confirmed!")
        
        # Timeout after 24 hours
        if booking.confirmation_check_count > 1440:  # 24 hours of minute checks
            booking.status = MeetingBookingStatus.FAILED
            booking.error_message = "Confirmation timeout after 24 hours"
            logger.warning(f"Booking {booking.id} timed out")
        
        self.db.commit()
    
    async def _check_email_confirmation(self, booking: MeetingBookingRequest) -> bool:
        """
        Check user's email for confirmation from booking platform
        """
        # This would integrate with email API (Gmail, Outlook, etc.)
        # For now, return False
        return False
    
    async def _check_platform_api(self, booking: MeetingBookingRequest) -> bool:
        """
        Check booking platform API for confirmation
        """
        # This would integrate with Calendly API, Cal.com API, etc.
        # For now, return False
        return False
    
    async def _check_platform_selenium(self, booking: MeetingBookingRequest) -> bool:
        """
        Use Selenium to check booking platform for confirmation
        """
        # This would launch Selenium to check booking status
        # For now, return False
        return False
    
    async def _add_to_calendar(self, booking: MeetingBookingRequest):
        """
        Add confirmed meeting to user's calendar
        """
        from calendar_sync_engine import CalendarSyncEngine
        
        calendar_engine = CalendarSyncEngine(self.db)
        
        # Create calendar meeting
        # This would use the existing calendar integration
        logger.info(f"Adding booking {booking.id} to calendar")
    
    async def _notify_user(self, booking: MeetingBookingRequest):
        """
        Notify user that meeting is confirmed
        """
        # Send notification (email, push, in-app)
        logger.info(f"Notifying user about confirmed booking {booking.id}")
```

---

## 🔌 API Endpoints

```python
# api/main.py - Booking endpoints

from selenium_booking_agent import SeleniumBookingAgent
from booking_confirmation_service import BookingConfirmationService

@app.post("/api/meetings/book")
async def book_meeting_with_startup(
    request: schemas.BookMeetingRequest,
    background_tasks: BackgroundTasks,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Initiate automated meeting booking with startup
    """
    # Create booking request
    booking_request = MeetingBookingRequest(
        user_id=current_user.id,
        startup_id=request.startup_id,
        status=MeetingBookingStatus.PENDING,
        user_name=request.user_name or f"{current_user.first_name} {current_user.last_name}",
        user_email=request.user_email or current_user.email,
        user_company="AXA Innovation",
        user_role="Venture Client Team",
        message_template=request.custom_message
    )
    
    db.add(booking_request)
    db.commit()
    db.refresh(booking_request)
    
    # Get booking configuration for startup
    booking_config = db.query(StartupBookingConfig).filter(
        StartupBookingConfig.startup_id == request.startup_id
    ).first()
    
    if not booking_config:
        raise HTTPException(
            status_code=400,
            detail="Booking not configured for this startup"
        )
    
    # Launch booking process in background
    background_tasks.add_task(
        execute_automated_booking,
        booking_request.id,
        db
    )
    
    return {
        "success": True,
        "booking_id": booking_request.id,
        "status": booking_request.status,
        "message": "Booking process initiated"
    }

@app.get("/api/meetings/booking-status/{booking_id}")
async def get_booking_status(
    booking_id: int,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get status of a booking request
    """
    booking = db.query(MeetingBookingRequest).filter(
        MeetingBookingRequest.id == booking_id,
        MeetingBookingRequest.user_id == current_user.id
    ).first()
    
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    return {
        "booking_id": booking.id,
        "status": booking.status,
        "startup_id": booking.startup_id,
        "selected_person": booking.selected_person_name,
        "proposed_slots": [
            booking.proposed_slot_1_datetime,
            booking.proposed_slot_2_datetime
        ] if booking.proposed_slot_1_datetime else [],
        "confirmed_slot": booking.confirmed_slot_datetime,
        "confirmation_checks": booking.confirmation_check_count,
        "last_check": booking.last_confirmation_check,
        "error": booking.error_message,
        "screenshots": booking.selenium_screenshots
    }

@app.post("/api/meetings/cancel-booking/{booking_id}")
async def cancel_booking(
    booking_id: int,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Cancel a pending booking
    """
    booking = db.query(MeetingBookingRequest).filter(
        MeetingBookingRequest.id == booking_id,
        MeetingBookingRequest.user_id == current_user.id
    ).first()
    
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    booking.status = MeetingBookingStatus.CANCELLED
    db.commit()
    
    return {
        "success": True,
        "message": "Booking cancelled"
    }

# Background task function
def execute_automated_booking(booking_id: int, db: Session):
    """
    Execute the automated booking process
    """
    booking = db.query(MeetingBookingRequest).filter(
        MeetingBookingRequest.id == booking_id
    ).first()
    
    if not booking:
        return
    
    try:
        # Update status
        booking.status = MeetingBookingStatus.BOOKING_IN_PROGRESS
        booking.booking_started_at = datetime.utcnow()
        db.commit()
        
        # Get booking config
        booking_config = db.query(StartupBookingConfig).filter(
            StartupBookingConfig.startup_id == booking.startup_id
        ).first()
        
        # Get user availability (simplified)
        user_availability = []  # Would come from user's calendar
        
        # Initialize Selenium agent
        agent = SeleniumBookingAgent(headless=True)
        
        # Execute booking
        result = agent.book_meeting(
            booking,
            booking_config,
            user_availability
        )
        
        if result["success"]:
            booking.status = MeetingBookingStatus.PENDING_CONFIRMATION
            booking.selenium_screenshots = result.get("screenshots", [])
            booking.selected_person_name = result.get("selected_person", {}).get("name")
            booking.selected_person_email = result.get("selected_person", {}).get("email")
            booking.external_booking_id = result.get("booking_id")
            
            # Extract proposed slots if available
            proposed_slots = result.get("proposed_slots", [])
            if len(proposed_slots) >= 1:
                booking.proposed_slot_1_datetime = proposed_slots[0].get("datetime")
            if len(proposed_slots) >= 2:
                booking.proposed_slot_2_datetime = proposed_slots[1].get("datetime")
        else:
            booking.status = MeetingBookingStatus.FAILED
            booking.error_message = result.get("error", "Unknown error")
            booking.selenium_screenshots = result.get("screenshots", [])
        
        booking.booking_completed_at = datetime.utcnow()
        db.commit()
        
    except Exception as e:
        logger.error(f"Booking execution failed: {e}")
        booking.status = MeetingBookingStatus.FAILED
        booking.error_message = str(e)
        db.commit()
```

---

## 🎨 Frontend Components

### Enhanced Book Meeting Button

```typescript
// components/Meetings/BookMeetingButton.tsx

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Calendar, Clock, CheckCircle, AlertCircle, Loader2 } from 'lucide-react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';

interface BookMeetingButtonProps {
  startupId: string;
  startupName: string;
  onBookingComplete?: (bookingId: number) => void;
}

export function BookMeetingButton({ 
  startupId, 
  startupName,
  onBookingComplete 
}: BookMeetingButtonProps) {
  const [status, setStatus] = useState<'idle' | 'booking' | 'pending' | 'confirmed' | 'failed'>('idle');
  const [bookingId, setBookingId] = useState<number | null>(null);
  const [showDialog, setShowDialog] = useState(false);
  const [bookingDetails, setBookingDetails] = useState<any>(null);
  const [checkInterval, setCheckInterval] = useState<NodeJS.Timeout | null>(null);
  
  useEffect(() => {
    // Start checking status if pending
    if (status === 'pending' && bookingId) {
      const interval = setInterval(() => {
        checkBookingStatus(bookingId);
      }, 60000); // Check every minute
      
      setCheckInterval(interval);
      
      return () => {
        if (interval) clearInterval(interval);
      };
    }
  }, [status, bookingId]);
  
  const handleBookMeeting = async () => {
    setStatus('booking');
    setShowDialog(true);
    
    try {
      const response = await fetch('/api/meetings/book', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          startup_id: startupId,
          custom_message: null  // Uses default AXA message
        })
      });
      
      const data = await response.json();
      
      if (data.success) {
        setBookingId(data.booking_id);
        setStatus('pending');
        
        // Start checking status immediately
        setTimeout(() => checkBookingStatus(data.booking_id), 5000);
      } else {
        setStatus('failed');
      }
    } catch (error) {
      console.error('Booking failed:', error);
      setStatus('failed');
    }
  };
  
  const checkBookingStatus = async (id: number) => {
    try {
      const response = await fetch(`/api/meetings/booking-status/${id}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      const data = await response.json();
      setBookingDetails(data);
      
      if (data.status === 'confirmed' || data.status === 'added_to_calendar') {
        setStatus('confirmed');
        if (checkInterval) {
          clearInterval(checkInterval);
          setCheckInterval(null);
        }
        
        if (onBookingComplete) {
          onBookingComplete(id);
        }
      } else if (data.status === 'failed') {
        setStatus('failed');
        if (checkInterval) {
          clearInterval(checkInterval);
          setCheckInterval(null);
        }
      }
    } catch (error) {
      console.error('Status check failed:', error);
    }
  };
  
  const getButtonContent = () => {
    switch (status) {
      case 'booking':
        return (
          <>
            <Loader2 className="w-4 h-4 mr-2 animate-spin" />
            Booking...
          </>
        );
      case 'pending':
        return (
          <>
            <Clock className="w-4 h-4 mr-2 animate-pulse" />
            Pending Confirmation ⏳
          </>
        );
      case 'confirmed':
        return (
          <>
            <CheckCircle className="w-4 h-4 mr-2" />
            ✓ Booked
          </>
        );
      case 'failed':
        return (
          <>
            <AlertCircle className="w-4 h-4 mr-2" />
            Booking Failed
          </>
        );
      default:
        return (
          <>
            <Calendar className="w-4 h-4 mr-2" />
            Book Meeting
          </>
        );
    }
  };
  
  const getButtonVariant = () => {
    switch (status) {
      case 'confirmed':
        return 'secondary';
      case 'failed':
        return 'destructive';
      default:
        return 'default';
    }
  };
  
  return (
    <>
      <Button
        onClick={handleBookMeeting}
        disabled={status === 'booking' || status === 'pending' || status === 'confirmed'}
        variant={getButtonVariant()}
        className={status === 'confirmed' ? 'bg-green-100 text-green-800' : ''}
      >
        {getButtonContent()}
      </Button>
      
      {/* Booking Status Dialog */}
      <Dialog open={showDialog} onOpenChange={setShowDialog}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>
              {status === 'booking' && '🤖 Automated Booking in Progress'}
              {status === 'pending' && '⏳ Waiting for Confirmation'}
              {status === 'confirmed' && '✓ Meeting Confirmed!'}
              {status === 'failed' && '❌ Booking Failed'}
            </DialogTitle>
          </DialogHeader>
          
          <div className="space-y-4">
            {status === 'booking' && (
              <div className="text-center py-8">
                <Loader2 className="w-16 h-16 mx-auto mb-4 animate-spin text-blue-600" />
                <p className="text-lg font-semibold mb-2">Our AI agent is booking your meeting...</p>
                <div className="text-sm text-gray-600 space-y-1">
                  <p>✓ Navigating to {startupName}'s booking platform</p>
                  <p>✓ Selecting available team member</p>
                  <p>✓ Finding matching time slots</p>
                  <p>✓ Filling booking details</p>
                  <p>✓ Sending your message</p>
                </div>
              </div>
            )}
            
            {status === 'pending' && bookingDetails && (
              <div className="space-y-4">
                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                  <div className="flex items-center gap-2 mb-2">
                    <Clock className="w-5 h-5 text-yellow-600 animate-pulse" />
                    <span className="font-semibold text-yellow-900">
                      Waiting for {startupName} to confirm
                    </span>
                  </div>
                  <p className="text-sm text-yellow-800">
                    We're checking for confirmation every minute. You'll be notified when confirmed.
                  </p>
                </div>
                
                {bookingDetails.selected_person && (
                  <div>
                    <p className="text-sm font-semibold mb-1">Meeting with:</p>
                    <p className="text-sm text-gray-600">{bookingDetails.selected_person}</p>
                  </div>
                )}
                
                {bookingDetails.proposed_slots && bookingDetails.proposed_slots.length > 0 && (
                  <div>
                    <p className="text-sm font-semibold mb-2">Proposed time slots:</p>
                    <div className="space-y-1">
                      {bookingDetails.proposed_slots.map((slot: string, idx: number) => (
                        <p key={idx} className="text-sm text-gray-600">
                          {slot ? new Date(slot).toLocaleString() : 'TBD'}
                        </p>
                      ))}
                    </div>
                  </div>
                )}
                
                <div className="text-xs text-gray-500">
                  Checked {bookingDetails.confirmation_checks} times
                  {bookingDetails.last_check && ` (last: ${new Date(bookingDetails.last_check).toLocaleTimeString()})`}
                </div>
              </div>
            )}
            
            {status === 'confirmed' && bookingDetails && (
              <div className="space-y-4">
                <div className="bg-green-50 border border-green-200 rounded-lg p-4 text-center">
                  <CheckCircle className="w-16 h-16 mx-auto mb-3 text-green-600" />
                  <p className="text-lg font-semibold text-green-900 mb-1">
                    Meeting Confirmed!
                  </p>
                  <p className="text-sm text-green-700">
                    Your meeting with {startupName} has been added to your calendar
                  </p>
                </div>
                
                {bookingDetails.confirmed_slot && (
                  <div className="text-center">
                    <p className="text-sm font-semibold mb-1">Scheduled for:</p>
                    <p className="text-lg font-bold text-gray-900">
                      {new Date(bookingDetails.confirmed_slot).toLocaleString()}
                    </p>
                  </div>
                )}
                
                <div className="flex gap-2">
                  <Button 
                    onClick={() => window.location.href = '/calendar'}
                    className="flex-1"
                  >
                    <Calendar className="w-4 h-4 mr-2" />
                    View Calendar
                  </Button>
                  <Button 
                    variant="outline"
                    onClick={() => setShowDialog(false)}
                    className="flex-1"
                  >
                    Close
                  </Button>
                </div>
              </div>
            )}
            
            {status === 'failed' && bookingDetails && (
              <div className="space-y-4">
                <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                  <AlertCircle className="w-5 h-5 text-red-600 mx-auto mb-2" />
                  <p className="text-sm text-red-800 text-center">
                    {bookingDetails.error || 'Automated booking failed. Please try booking manually.'}
                  </p>
                </div>
                
                <Button 
                  onClick={() => {
                    setStatus('idle');
                    setShowDialog(false);
                  }}
                  className="w-full"
                >
                  Try Again
                </Button>
              </div>
            )}
          </div>
        </DialogContent>
      </Dialog>
    </>
  );
}
```

---

## 📋 Pydantic Schemas

```python
# schemas.py additions

class BookMeetingRequest(BaseModel):
    startup_id: str
    user_name: Optional[str] = None
    user_email: Optional[str] = None
    custom_message: Optional[str] = None
    preferred_times: Optional[List[datetime]] = None

class BookingStatusResponse(BaseModel):
    booking_id: int
    status: str
    startup_id: str
    selected_person: Optional[str]
    proposed_slots: List[Optional[datetime]]
    confirmed_slot: Optional[datetime]
    confirmation_checks: int
    last_check: Optional[datetime]
    error: Optional[str]
    screenshots: List[str]
```

---

## 📦 Dependencies to Install

```bash
# Add to requirements.txt
selenium==4.15.2
webdriver-manager==4.0.1
Pillow==10.1.0  # For screenshot processing
```

---

## 🚀 Setup & Configuration

### 1. Install Chrome/Chromium

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y chromium-browser chromium-chromedriver

# Or use webdriver-manager (recommended)
pip install webdriver-manager
```

### 2. Configure Startup Booking Platforms

```python
# Script to add booking configurations
from database import SessionLocal
from models import StartupBookingConfig

def configure_startup_booking(startup_id: str, platform: str, url: str):
    db = SessionLocal()
    
    config = StartupBookingConfig(
        startup_id=startup_id,
        platform_type=platform,
        booking_url=url,
        available_people=[
            {"name": "John Doe", "role": "CEO", "email": "john@startup.com"},
            {"name": "Jane Smith", "role": "CTO", "email": "jane@startup.com"}
        ],
        selectors={
            "person_button": ".team-member-button",
            "time_slots": ".time-slot-button",
            "name_field": "input[name='name']",
            "email_field": "input[name='email']",
            "message_field": "textarea[name='notes']",
            "submit_button": "button[type='submit']"
        },
        success_indicators=[
            ".confirmation-message",
            ".success-banner",
            "h1:contains('Confirmed')"
        ]
    )
    
    db.add(config)
    db.commit()
```

### 3. Start Confirmation Monitor

```python
# In main.py startup event
@app.on_event("startup")
async def startup_event():
    """Start background tasks"""
    from booking_confirmation_service import BookingConfirmationService
    
    db = SessionLocal()
    confirmation_service = BookingConfirmationService(db)
    asyncio.create_task(confirmation_service.monitor_confirmations())
```

---

## ✅ Testing

```python
# test_booking_agent.py

def test_booking_agent():
    """Test the booking agent"""
    agent = SeleniumBookingAgent(headless=False)  # Visual mode for testing
    
    # Mock booking request
    booking_request = MeetingBookingRequest(
        user_name="Eduardo Paz",
        user_email="eduardo.paz@axa-innovation.com",
        startup_id="test_startup"
    )
    
    # Mock booking config
    booking_config = StartupBookingConfig(
        booking_url="https://calendly.com/test-startup",
        platform_type="calendly",
        selectors={...}
    )
    
    result = agent.book_meeting(booking_request, booking_config, [])
    
    print(f"Booking result: {result}")
    print(f"Screenshots: {agent.screenshots}")
```

---

*End of Automated Meeting Booking System Implementation Plan*
