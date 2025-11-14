# Enhanced Matching System - Implementation Plan

## Executive Summary

This plan outlines the implementation of an enhanced attendee-to-startup matching system featuring a "Top Agentic Startups" carousel with intelligent categorization and strategic positioning for partnership opportunities.

---

## 🎯 Core Objective

Create an intelligent matching system that:
1. Identifies strategic partnership opportunities
2. Highlights non-competitive enabler technologies
3. Showcases proven agentic service providers
4. Positions startups as value-add partners, not competitors

---

## 🎠 Feature: "Top Agentic Startups" Carousel

### Visual Layout

```
┌─────────────────────────────────────────────────────────────────┐
│                    🌟 Top Agentic Startups 🌟                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐           │
│  │   [LOGO]    │   │   [LOGO]    │   │   [LOGO]    │  ▶        │
│  │             │   │             │   │             │           │
│  │ Startup Name│   │ Startup Name│   │ Startup Name│           │
│  │             │   │             │   │             │           │
│  │ 🔧 Platform │   │ 🤖 Agentic  │   │ 🔧 Platform │           │
│  │   Enabler   │   │  Service    │   │   Enabler   │           │
│  │             │   │             │   │             │           │
│  │ "Could del- │   │ "Autonomous │   │ "Enterprise │           │
│  │  iver obs-  │   │  Agentic HR │   │  API Mgmt   │           │
│  │  ervability │   │  used by 30 │   │  for Global │           │
│  │  for our    │   │  Fortune 500│   │  Platform"  │           │
│  │  Platform"  │   │  companies" │   │             │           │
│  │             │   │             │   │             │           │
│  │ [View More] │   │ [View More] │   │ [View More] │           │
│  └─────────────┘   └─────────────┘   └─────────────┘           │
│                                                                   │
│  ◀  ● ○ ○ ○  ▶          3 of 12 startups                        │
└─────────────────────────────────────────────────────────────────┘
```

### Startup Types & Badges

#### Type 1: 🔧 Platform Enablers
**Purpose**: Infrastructure/tools that support platform delivery without competing

**Examples**:
- Observability & Monitoring
- API Management & Gateway
- Security & Compliance
- Data Pipeline & ETL
- DevOps Automation
- Infrastructure as Code

**Badge Color**: Blue (#3B82F6)

#### Type 2: 🤖 Agentic Service Providers  
**Purpose**: Proven agentic solutions in non-insurance domains

**Examples**:
- Agentic Marketing Automation
- Agentic HR & Recruitment
- Agentic Customer Service (non-insurance)
- Agentic Legal Research
- Agentic Financial Planning (non-insurance)
- Agentic Supply Chain Management

**Badge Color**: Purple (#8B5CF6)

---

## 📊 Data Model Extensions

### 1. Enhanced Startup Schema

```python
# models.py additions

class StartupCategory(str, Enum):
    PLATFORM_ENABLER = "platform_enabler"
    AGENTIC_SERVICE = "agentic_service"
    OTHER = "other"

class StartupEnhanced(Base):
    __tablename__ = "startups_enhanced"
    
    id = Column(Integer, primary_key=True, index=True)
    startup_id = Column(String, unique=True, index=True)
    name = Column(String, index=True)
    logo_url = Column(String, nullable=True)
    
    # Category & Classification
    category = Column(String)  # platform_enabler or agentic_service
    is_top_pick = Column(Boolean, default=False)
    priority_score = Column(Float, default=0.0)
    
    # USP & Positioning
    usp_short = Column(String(200))  # Short pitch for carousel
    usp_long = Column(Text)  # Detailed value proposition
    value_proposition = Column(Text)  # How it helps without competing
    
    # Credentials
    proven_track_record = Column(Text)  # e.g., "Used by 50 Fortune 500"
    customer_count = Column(Integer, nullable=True)
    fortune_500_clients = Column(Integer, nullable=True)
    
    # Strategic Fit
    capabilities_delivered = Column(JSON)  # List of capabilities
    non_competitive_areas = Column(JSON)  # Areas where doesn't compete
    integration_complexity = Column(String)  # Low/Medium/High
    
    # Insurance Relevance Flags
    is_insurance_focused = Column(Boolean, default=False)
    insurance_vertical_exclusion = Column(Boolean, default=False)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

### 2. Matching Preferences Schema

```python
class AttendeeMatchingPreferences(Base):
    __tablename__ = "attendee_matching_preferences"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Strategic Priorities
    looking_for_platform_enablers = Column(Boolean, default=True)
    looking_for_agentic_services = Column(Boolean, default=True)
    
    # Capability Needs
    needed_capabilities = Column(JSON)  # ["observability", "api_mgmt", etc.]
    
    # Service Interests
    interested_service_domains = Column(JSON)  # ["marketing", "hr", etc.]
    
    # Filters
    min_fortune_500_clients = Column(Integer, default=0)
    max_integration_complexity = Column(String, default="High")
    exclude_insurance_focused = Column(Boolean, default=True)
    
    # Match History
    viewed_startups = Column(JSON, default=list)
    interested_startups = Column(JSON, default=list)
    passed_startups = Column(JSON, default=list)
```

### 3. Match Scoring Schema

```python
class StartupMatch(Base):
    __tablename__ = "startup_matches"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    startup_id = Column(String, ForeignKey("startups_enhanced.startup_id"))
    
    # Scoring
    overall_score = Column(Float, index=True)
    strategic_fit_score = Column(Float)
    capability_match_score = Column(Float)
    credibility_score = Column(Float)
    integration_ease_score = Column(Float)
    
    # Match Reasons
    match_reasons = Column(JSON)  # ["Delivers observability", "Non-competitive"]
    
    # User Actions
    viewed = Column(Boolean, default=False)
    interested = Column(Boolean, default=False)
    passed = Column(Boolean, default=False)
    meeting_requested = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
```

---

## 🧠 Intelligent Matching Algorithm

### Matching Logic Flow

```python
# matching_algorithm.py

from typing import List, Dict
from sqlalchemy.orm import Session

class AgenticMatchingEngine:
    """
    Enhanced matching engine for attendee-to-startup recommendations
    """
    
    def __init__(self, db: Session):
        self.db = db
        
    def calculate_match_score(
        self,
        attendee: AttendeeMatchingPreferences,
        startup: StartupEnhanced
    ) -> Dict:
        """
        Calculate comprehensive match score
        """
        scores = {
            "strategic_fit": self._score_strategic_fit(attendee, startup),
            "capability_match": self._score_capability_match(attendee, startup),
            "credibility": self._score_credibility(startup),
            "integration_ease": self._score_integration_ease(startup),
            "non_competitive": self._score_non_competitive(startup)
        }
        
        # Weighted overall score
        weights = {
            "strategic_fit": 0.30,
            "capability_match": 0.25,
            "credibility": 0.20,
            "integration_ease": 0.15,
            "non_competitive": 0.10
        }
        
        overall = sum(scores[k] * weights[k] for k in scores.keys())
        
        return {
            "overall_score": overall,
            "component_scores": scores,
            "match_reasons": self._generate_match_reasons(attendee, startup, scores)
        }
    
    def _score_strategic_fit(
        self,
        attendee: AttendeeMatchingPreferences,
        startup: StartupEnhanced
    ) -> float:
        """
        Score based on strategic alignment
        """
        score = 0.0
        
        # Category preference match
        if startup.category == "platform_enabler" and attendee.looking_for_platform_enablers:
            score += 40.0
        if startup.category == "agentic_service" and attendee.looking_for_agentic_services:
            score += 40.0
        
        # Insurance exclusion preference
        if attendee.exclude_insurance_focused and not startup.is_insurance_focused:
            score += 20.0
        
        return min(score, 100.0)
    
    def _score_capability_match(
        self,
        attendee: AttendeeMatchingPreferences,
        startup: StartupEnhanced
    ) -> float:
        """
        Score based on capability alignment
        """
        if not attendee.needed_capabilities or not startup.capabilities_delivered:
            return 50.0
        
        needed = set(attendee.needed_capabilities)
        delivered = set(startup.capabilities_delivered)
        
        if not needed:
            return 50.0
        
        overlap = len(needed & delivered)
        score = (overlap / len(needed)) * 100.0
        
        return score
    
    def _score_credibility(self, startup: StartupEnhanced) -> float:
        """
        Score based on track record and credentials
        """
        score = 0.0
        
        # Fortune 500 clients
        if startup.fortune_500_clients:
            score += min(startup.fortune_500_clients * 2, 50.0)
        
        # Customer count
        if startup.customer_count:
            if startup.customer_count >= 100:
                score += 30.0
            elif startup.customer_count >= 50:
                score += 20.0
            elif startup.customer_count >= 20:
                score += 10.0
        
        # Has proven track record text
        if startup.proven_track_record:
            score += 20.0
        
        return min(score, 100.0)
    
    def _score_integration_ease(self, startup: StartupEnhanced) -> float:
        """
        Score based on integration complexity
        """
        complexity_scores = {
            "Low": 100.0,
            "Medium": 70.0,
            "High": 40.0
        }
        return complexity_scores.get(startup.integration_complexity, 50.0)
    
    def _score_non_competitive(self, startup: StartupEnhanced) -> float:
        """
        Score based on non-competitive positioning
        """
        score = 50.0  # Base score
        
        if startup.non_competitive_areas:
            score += min(len(startup.non_competitive_areas) * 10, 50.0)
        
        return score
    
    def _generate_match_reasons(
        self,
        attendee: AttendeeMatchingPreferences,
        startup: StartupEnhanced,
        scores: Dict
    ) -> List[str]:
        """
        Generate human-readable match reasons
        """
        reasons = []
        
        # Category match
        if startup.category == "platform_enabler":
            reasons.append(f"Platform Enabler: {startup.usp_short}")
        elif startup.category == "agentic_service":
            reasons.append(f"Proven Agentic Service: {startup.usp_short}")
        
        # Credentials
        if startup.fortune_500_clients and startup.fortune_500_clients > 0:
            reasons.append(f"Used by {startup.fortune_500_clients} Fortune 500 companies")
        
        # Capability match
        if scores["capability_match"] > 70:
            reasons.append("Strong capability alignment with your needs")
        
        # Non-competitive
        if startup.non_competitive_areas:
            reasons.append("Non-competitive enabler technology")
        
        # Easy integration
        if startup.integration_complexity == "Low":
            reasons.append("Easy integration complexity")
        
        return reasons
    
    def get_top_matches(
        self,
        user_id: int,
        limit: int = 12
    ) -> List[Dict]:
        """
        Get top matching startups for carousel
        """
        attendee = self.db.query(AttendeeMatchingPreferences).filter(
            AttendeeMatchingPreferences.user_id == user_id
        ).first()
        
        if not attendee:
            attendee = self._create_default_preferences(user_id)
        
        # Get candidate startups
        startups = self.db.query(StartupEnhanced).filter(
            StartupEnhanced.is_top_pick == True
        ).all()
        
        # Score all startups
        matches = []
        for startup in startups:
            score_data = self.calculate_match_score(attendee, startup)
            matches.append({
                "startup": startup,
                "score_data": score_data
            })
        
        # Sort by overall score
        matches.sort(key=lambda x: x["score_data"]["overall_score"], reverse=True)
        
        # Save match records
        self._save_match_records(user_id, matches[:limit])
        
        return matches[:limit]
    
    def _create_default_preferences(self, user_id: int) -> AttendeeMatchingPreferences:
        """
        Create default matching preferences
        """
        prefs = AttendeeMatchingPreferences(
            user_id=user_id,
            looking_for_platform_enablers=True,
            looking_for_agentic_services=True,
            needed_capabilities=[
                "observability",
                "api_management",
                "security",
                "monitoring"
            ],
            interested_service_domains=[
                "marketing",
                "hr",
                "customer_service"
            ],
            exclude_insurance_focused=True
        )
        self.db.add(prefs)
        self.db.commit()
        return prefs
    
    def _save_match_records(self, user_id: int, matches: List[Dict]):
        """
        Save match records to database
        """
        for match in matches:
            startup = match["startup"]
            score_data = match["score_data"]
            
            # Check if record exists
            existing = self.db.query(StartupMatch).filter(
                StartupMatch.user_id == user_id,
                StartupMatch.startup_id == startup.startup_id
            ).first()
            
            if not existing:
                match_record = StartupMatch(
                    user_id=user_id,
                    startup_id=startup.startup_id,
                    overall_score=score_data["overall_score"],
                    strategic_fit_score=score_data["component_scores"]["strategic_fit"],
                    capability_match_score=score_data["component_scores"]["capability_match"],
                    credibility_score=score_data["component_scores"]["credibility"],
                    integration_ease_score=score_data["component_scores"]["integration_ease"],
                    match_reasons=score_data["match_reasons"]
                )
                self.db.add(match_record)
        
        self.db.commit()
```

---

## 🎨 Frontend Implementation

### 1. React Component Structure

```typescript
// components/TopAgenticStartups/TopAgenticStartupsCarousel.tsx

import { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { ChevronLeft, ChevronRight } from 'lucide-react';

interface Startup {
  id: string;
  name: string;
  logo_url: string;
  category: 'platform_enabler' | 'agentic_service';
  usp_short: string;
  proven_track_record: string;
  fortune_500_clients?: number;
  overall_score: number;
  match_reasons: string[];
}

export function TopAgenticStartupsCarousel() {
  const [startups, setStartups] = useState<Startup[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [loading, setLoading] = useState(true);
  
  const itemsPerPage = 3;
  
  useEffect(() => {
    fetchTopStartups();
  }, []);
  
  const fetchTopStartups = async () => {
    try {
      const response = await fetch('/api/matching/top-startups', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      const data = await response.json();
      setStartups(data.startups);
    } catch (error) {
      console.error('Error fetching startups:', error);
    } finally {
      setLoading(false);
    }
  };
  
  const nextSlide = () => {
    setCurrentIndex((prev) => 
      (prev + itemsPerPage) % startups.length
    );
  };
  
  const prevSlide = () => {
    setCurrentIndex((prev) => 
      prev === 0 ? startups.length - itemsPerPage : prev - itemsPerPage
    );
  };
  
  const getCategoryLabel = (category: string) => {
    return category === 'platform_enabler' 
      ? '🔧 Platform Enabler' 
      : '🤖 Agentic Service';
  };
  
  const getCategoryColor = (category: string) => {
    return category === 'platform_enabler' ? 'blue' : 'purple';
  };
  
  const visibleStartups = startups.slice(
    currentIndex, 
    currentIndex + itemsPerPage
  );
  
  if (loading) {
    return <div>Loading top startups...</div>;
  }
  
  return (
    <div className="w-full bg-gradient-to-r from-blue-50 to-purple-50 p-8 rounded-lg mb-8">
      {/* Header */}
      <div className="text-center mb-6">
        <h2 className="text-3xl font-bold text-gray-900 mb-2">
          🌟 Top Agentic Startups 🌟
        </h2>
        <p className="text-gray-600">
          Strategic partners to accelerate your Global Agentic Platform
        </p>
      </div>
      
      {/* Carousel */}
      <div className="relative">
        {/* Previous Button */}
        <button
          onClick={prevSlide}
          className="absolute left-0 top-1/2 -translate-y-1/2 -translate-x-12 z-10
                     bg-white rounded-full p-2 shadow-lg hover:bg-gray-100"
          disabled={currentIndex === 0}
        >
          <ChevronLeft className="w-6 h-6" />
        </button>
        
        {/* Cards Container */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {visibleStartups.map((startup) => (
            <StartupCard 
              key={startup.id} 
              startup={startup}
              categoryLabel={getCategoryLabel(startup.category)}
              categoryColor={getCategoryColor(startup.category)}
            />
          ))}
        </div>
        
        {/* Next Button */}
        <button
          onClick={nextSlide}
          className="absolute right-0 top-1/2 -translate-y-1/2 translate-x-12 z-10
                     bg-white rounded-full p-2 shadow-lg hover:bg-gray-100"
          disabled={currentIndex >= startups.length - itemsPerPage}
        >
          <ChevronRight className="w-6 h-6" />
        </button>
      </div>
      
      {/* Pagination Dots */}
      <div className="flex justify-center items-center mt-6 gap-4">
        <button onClick={prevSlide} className="text-gray-500 hover:text-gray-700">
          ◀
        </button>
        <div className="flex gap-2">
          {Array.from({ length: Math.ceil(startups.length / itemsPerPage) }).map((_, i) => (
            <button
              key={i}
              onClick={() => setCurrentIndex(i * itemsPerPage)}
              className={`w-3 h-3 rounded-full transition-colors ${
                Math.floor(currentIndex / itemsPerPage) === i
                  ? 'bg-blue-600'
                  : 'bg-gray-300'
              }`}
            />
          ))}
        </div>
        <button onClick={nextSlide} className="text-gray-500 hover:text-gray-700">
          ▶
        </button>
        <span className="text-sm text-gray-600 ml-4">
          {currentIndex + 1}-{Math.min(currentIndex + itemsPerPage, startups.length)} of {startups.length} startups
        </span>
      </div>
    </div>
  );
}

// Startup Card Component
function StartupCard({ 
  startup, 
  categoryLabel, 
  categoryColor 
}: { 
  startup: Startup; 
  categoryLabel: string; 
  categoryColor: string;
}) {
  return (
    <Card className="p-6 bg-white hover:shadow-xl transition-shadow duration-300 flex flex-col h-full">
      {/* Logo */}
      <div className="flex justify-center mb-4">
        <img 
          src={startup.logo_url || '/placeholder-logo.png'} 
          alt={startup.name}
          className="h-16 w-16 object-contain"
        />
      </div>
      
      {/* Name */}
      <h3 className="text-xl font-bold text-center mb-3 text-gray-900">
        {startup.name}
      </h3>
      
      {/* Category Badge */}
      <div className="flex justify-center mb-4">
        <Badge 
          variant="secondary"
          className={`bg-${categoryColor}-100 text-${categoryColor}-800 px-4 py-1`}
        >
          {categoryLabel}
        </Badge>
      </div>
      
      {/* USP */}
      <div className="flex-grow mb-4">
        <p className="text-sm text-gray-700 text-center italic">
          "{startup.usp_short}"
        </p>
      </div>
      
      {/* Track Record */}
      {startup.proven_track_record && (
        <div className="mb-4">
          <p className="text-xs text-gray-600 text-center">
            {startup.proven_track_record}
          </p>
        </div>
      )}
      
      {/* Match Score */}
      <div className="mb-4">
        <div className="flex justify-between items-center mb-1">
          <span className="text-xs text-gray-600">Match Score</span>
          <span className="text-xs font-bold text-blue-600">
            {Math.round(startup.overall_score)}%
          </span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div 
            className="bg-blue-600 h-2 rounded-full transition-all"
            style={{ width: `${startup.overall_score}%` }}
          />
        </div>
      </div>
      
      {/* Match Reasons */}
      <div className="mb-4">
        <p className="text-xs font-semibold text-gray-700 mb-2">Why matched:</p>
        <ul className="text-xs text-gray-600 space-y-1">
          {startup.match_reasons.slice(0, 2).map((reason, idx) => (
            <li key={idx} className="flex items-start">
              <span className="text-green-500 mr-1">✓</span>
              <span>{reason}</span>
            </li>
          ))}
        </ul>
      </div>
      
      {/* Action Button */}
      <Button 
        className="w-full bg-blue-600 hover:bg-blue-700 text-white"
        onClick={() => window.location.href = `/startup/${startup.id}`}
      >
        View Details
      </Button>
    </Card>
  );
}
```

### 2. Enhanced Matching Page

```typescript
// pages/MatchingPage.tsx

import { TopAgenticStartupsCarousel } from '@/components/TopAgenticStartups/TopAgenticStartupsCarousel';
import { MatchingPreferencesPanel } from '@/components/Matching/MatchingPreferencesPanel';
import { AllStartupsGrid } from '@/components/Matching/AllStartupsGrid';

export function MatchingPage() {
  return (
    <div className="container mx-auto px-4 py-8">
      {/* Top Carousel */}
      <TopAgenticStartupsCarousel />
      
      {/* Preferences Panel */}
      <div className="mb-8">
        <MatchingPreferencesPanel />
      </div>
      
      {/* All Startups */}
      <div>
        <h2 className="text-2xl font-bold mb-4">All Startups</h2>
        <AllStartupsGrid />
      </div>
    </div>
  );
}
```

---

## 🔌 API Endpoints

### 1. Get Top Matching Startups

```python
# api/main.py

from matching_algorithm import AgenticMatchingEngine

@app.get("/api/matching/top-startups")
async def get_top_matching_startups(
    limit: int = 12,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get top matching startups for carousel
    """
    engine = AgenticMatchingEngine(db)
    matches = engine.get_top_matches(current_user.id, limit=limit)
    
    startups_data = []
    for match in matches:
        startup = match["startup"]
        score_data = match["score_data"]
        
        startups_data.append({
            "id": startup.startup_id,
            "name": startup.name,
            "logo_url": startup.logo_url,
            "category": startup.category,
            "usp_short": startup.usp_short,
            "proven_track_record": startup.proven_track_record,
            "fortune_500_clients": startup.fortune_500_clients,
            "overall_score": score_data["overall_score"],
            "match_reasons": score_data["match_reasons"]
        })
    
    return {"startups": startups_data}

@app.get("/api/matching/preferences")
async def get_matching_preferences(
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get user's matching preferences
    """
    prefs = db.query(AttendeeMatchingPreferences).filter(
        AttendeeMatchingPreferences.user_id == current_user.id
    ).first()
    
    if not prefs:
        # Create default
        engine = AgenticMatchingEngine(db)
        prefs = engine._create_default_preferences(current_user.id)
    
    return prefs

@app.put("/api/matching/preferences")
async def update_matching_preferences(
    preferences: schemas.MatchingPreferencesUpdate,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update matching preferences
    """
    prefs = db.query(AttendeeMatchingPreferences).filter(
        AttendeeMatchingPreferences.user_id == current_user.id
    ).first()
    
    if not prefs:
        prefs = AttendeeMatchingPreferences(user_id=current_user.id)
        db.add(prefs)
    
    # Update fields
    for key, value in preferences.dict(exclude_unset=True).items():
        setattr(prefs, key, value)
    
    db.commit()
    db.refresh(prefs)
    
    return prefs

@app.post("/api/matching/interaction")
async def record_interaction(
    interaction: schemas.StartupInteraction,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Record user interaction with startup (view, interest, pass)
    """
    match_record = db.query(StartupMatch).filter(
        StartupMatch.user_id == current_user.id,
        StartupMatch.startup_id == interaction.startup_id
    ).first()
    
    if match_record:
        if interaction.action == "view":
            match_record.viewed = True
        elif interaction.action == "interest":
            match_record.interested = True
        elif interaction.action == "pass":
            match_record.passed = True
        elif interaction.action == "meeting_request":
            match_record.meeting_requested = True
        
        db.commit()
    
    return {"status": "recorded"}
```

### 2. Admin: Manage Top Startups

```python
@app.post("/api/admin/startups/enhanced")
async def create_enhanced_startup(
    startup: schemas.StartupEnhancedCreate,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create or update enhanced startup profile (Admin only)
    """
    # Check admin permissions
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    db_startup = StartupEnhanced(**startup.dict())
    db.add(db_startup)
    db.commit()
    db.refresh(db_startup)
    
    return db_startup

@app.get("/api/admin/startups/enhanced")
async def list_enhanced_startups(
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    List all enhanced startups (Admin only)
    """
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    query = db.query(StartupEnhanced)
    
    if category:
        query = query.filter(StartupEnhanced.category == category)
    
    startups = query.offset(skip).limit(limit).all()
    
    return {"startups": startups, "total": query.count()}
```

---

## 📝 Sample Data: Startup Profiles

### Platform Enablers

```json
[
  {
    "startup_id": "observiq",
    "name": "ObservIQ",
    "logo_url": "/logos/observiq.png",
    "category": "platform_enabler",
    "is_top_pick": true,
    "priority_score": 95.0,
    "usp_short": "Could deliver the observability and monitoring capabilities for our Global Agentic Platform",
    "usp_long": "Enterprise-grade observability platform specifically designed for distributed agentic systems. Provides real-time monitoring, tracing, and analytics without interfering with core business logic.",
    "value_proposition": "Enables platform reliability without competing. Focuses purely on infrastructure monitoring.",
    "proven_track_record": "Used by 35 Fortune 500 companies",
    "fortune_500_clients": 35,
    "customer_count": 250,
    "capabilities_delivered": [
      "observability",
      "monitoring",
      "distributed_tracing",
      "performance_analytics",
      "alerting"
    ],
    "non_competitive_areas": [
      "Infrastructure monitoring only",
      "No business logic involvement",
      "Pure enabler technology"
    ],
    "integration_complexity": "Low",
    "is_insurance_focused": false,
    "insurance_vertical_exclusion": true
  },
  {
    "startup_id": "apigate",
    "name": "APIGate Pro",
    "logo_url": "/logos/apigate.png",
    "category": "platform_enabler",
    "is_top_pick": true,
    "priority_score": 92.0,
    "usp_short": "Enterprise API Management for Global Platform orchestration without business logic interference",
    "usp_long": "API gateway and management platform that handles routing, authentication, and rate limiting for complex agentic architectures.",
    "value_proposition": "Handles the 'plumbing' so your team can focus on value delivery",
    "proven_track_record": "Managing 500B+ API calls/month for enterprise clients",
    "fortune_500_clients": 42,
    "customer_count": 180,
    "capabilities_delivered": [
      "api_management",
      "api_gateway",
      "authentication",
      "rate_limiting",
      "api_analytics"
    ],
    "non_competitive_areas": [
      "Infrastructure layer only",
      "No domain-specific logic",
      "Pure enabler service"
    ],
    "integration_complexity": "Low",
    "is_insurance_focused": false,
    "insurance_vertical_exclusion": true
  },
  {
    "startup_id": "secureagent",
    "name": "SecureAgent",
    "logo_url": "/logos/secureagent.png",
    "category": "platform_enabler",
    "is_top_pick": true,
    "priority_score": 90.0,
    "usp_short": "Security and compliance layer for agentic systems - delivers the tough regulatory parts",
    "usp_long": "Comprehensive security framework for AI agents with built-in compliance for GDPR, SOC2, HIPAA. Takes care of security so you don't have to.",
    "value_proposition": "Delivers complex security/compliance without competing with core platform value",
    "proven_track_record": "Protecting 1000+ agentic applications",
    "fortune_500_clients": 28,
    "customer_count": 320,
    "capabilities_delivered": [
      "security",
      "compliance",
      "encryption",
      "audit_logging",
      "access_control"
    ],
    "non_competitive_areas": [
      "Security infrastructure only",
      "No business process involvement",
      "Regulatory compliance focus"
    ],
    "integration_complexity": "Medium",
    "is_insurance_focused": false,
    "insurance_vertical_exclusion": true
  }
]
```

### Agentic Service Providers

```json
[
  {
    "startup_id": "agentic_marketing_pro",
    "name": "AgenticMark",
    "logo_url": "/logos/agenticmark.png",
    "category": "agentic_service",
    "is_top_pick": true,
    "priority_score": 88.0,
    "usp_short": "Autonomous Agentic Marketing used by 50 Fortune 500 companies - proven track record",
    "usp_long": "Fully autonomous marketing agent platform handling campaign creation, execution, and optimization. Zero overlap with insurance operations.",
    "value_proposition": "Demonstrates agentic value in marketing domain - builds confidence without competing",
    "proven_track_record": "Used by 50 Fortune 500 companies, $2B+ in influenced revenue",
    "fortune_500_clients": 50,
    "customer_count": 450,
    "capabilities_delivered": [
      "agentic_marketing",
      "campaign_automation",
      "content_generation",
      "audience_targeting",
      "performance_optimization"
    ],
    "non_competitive_areas": [
      "Marketing only - no insurance",
      "Proven agentic capabilities",
      "Complementary service"
    ],
    "integration_complexity": "Low",
    "is_insurance_focused": false,
    "insurance_vertical_exclusion": true
  },
  {
    "startup_id": "hr_agent",
    "name": "TalentAgent AI",
    "logo_url": "/logos/talentagent.png",
    "category": "agentic_service",
    "is_top_pick": true,
    "priority_score": 85.0,
    "usp_short": "Agentic HR & Recruitment - autonomous talent acquisition with zero insurance domain overlap",
    "usp_long": "AI-powered recruitment agents that handle sourcing, screening, and initial engagement autonomously. Perfect example of agentic services in non-competing domain.",
    "value_proposition": "Shows agentic ROI in HR while supporting your team growth - no competition",
    "proven_track_record": "Placed 10,000+ candidates, used by 30 Fortune 500 companies",
    "fortune_500_clients": 30,
    "customer_count": 280,
    "capabilities_delivered": [
      "agentic_hr",
      "talent_sourcing",
      "candidate_screening",
      "interview_scheduling",
      "onboarding_automation"
    ],
    "non_competitive_areas": [
      "HR domain only",
      "No insurance involvement",
      "Internal operations support"
    ],
    "integration_complexity": "Low",
    "is_insurance_focused": false,
    "insurance_vertical_exclusion": true
  },
  {
    "startup_id": "supply_agent",
    "name": "ChainAgent",
    "logo_url": "/logos/chainagent.png",
    "category": "agentic_service",
    "is_top_pick": true,
    "priority_score": 82.0,
    "usp_short": "Agentic Supply Chain Management - autonomous optimization proven at scale",
    "usp_long": "Autonomous agents managing supply chain logistics, inventory, and vendor relationships. Demonstrates agentic value in complex operational domain.",
    "value_proposition": "Proven agentic orchestration in supply chain - similar complexity, zero overlap",
    "proven_track_record": "Managing $5B+ in supply chain operations",
    "fortune_500_clients": 25,
    "customer_count": 150,
    "capabilities_delivered": [
      "agentic_supply_chain",
      "inventory_optimization",
      "vendor_management",
      "logistics_automation",
      "demand_forecasting"
    ],
    "non_competitive_areas": [
      "Supply chain only",
      "No insurance domain",
      "Operational efficiency focus"
    ],
    "integration_complexity": "Medium",
    "is_insurance_focused": false,
    "insurance_vertical_exclusion": true
  }
]
```

---

## 🚀 Implementation Phases

### Phase 1: Foundation (Week 1-2)
- [ ] Create database migrations for new schemas
- [ ] Implement StartupEnhanced, AttendeeMatchingPreferences, StartupMatch models
- [ ] Set up basic API endpoints
- [ ] Create admin interface for startup data entry

### Phase 2: Matching Algorithm (Week 3-4)
- [ ] Implement AgenticMatchingEngine class
- [ ] Build scoring algorithms
- [ ] Test matching logic with sample data
- [ ] Optimize performance

### Phase 3: Frontend Components (Week 5-6)
- [ ] Build TopAgenticStartupsCarousel component
- [ ] Create StartupCard component
- [ ] Implement carousel navigation
- [ ] Add responsive design

### Phase 4: Integration (Week 7)
- [ ] Connect frontend to API
- [ ] Implement user interaction tracking
- [ ] Add preferences panel
- [ ] Test end-to-end flow

### Phase 5: Data Population (Week 8)
- [ ] Research and identify top startups
- [ ] Populate database with 50+ startup profiles
- [ ] Categorize and score startups
- [ ] Validate data quality

### Phase 6: Testing & Refinement (Week 9-10)
- [ ] User acceptance testing
- [ ] A/B test different USP formats
- [ ] Optimize matching algorithm based on feedback
- [ ] Performance optimization

### Phase 7: Launch (Week 11)
- [ ] Soft launch to beta users
- [ ] Gather feedback
- [ ] Iterate on design
- [ ] Full launch

---

## 📊 Success Metrics

### Engagement Metrics
- **Carousel View Rate**: % of users viewing carousel
- **Click-Through Rate**: % clicking "View Details"
- **Interest Rate**: % marking startups as interesting
- **Meeting Request Rate**: % requesting meetings

### Matching Quality Metrics
- **Match Score Distribution**: Average match scores
- **User Satisfaction**: Rating of match quality
- **Interaction Depth**: Time spent on startup profiles
- **Conversion Rate**: Startups leading to partnerships

### Business Metrics
- **Partnership Conversions**: Startups becoming partners
- **Platform Enabler Adoption**: Integration rate
- **Agentic Service Validation**: Service adoptions
- **ROI**: Value delivered vs cost

---

## 🎯 Key Positioning Strategies

### 1. Non-Competitive Framing
- Emphasize "enabler" vs "competitor"
- Highlight "tough parts we don't want to build"
- Focus on "accelerates your platform"

### 2. Credential-Based Trust
- Fortune 500 client counts
- Revenue managed/influenced
- Scale metrics (API calls, users, etc.)
- Industry recognition

### 3. Strategic Value Messaging
- "Delivers X so you can focus on Y"
- "Handles the undifferentiated heavy lifting"
- "Proven at scale, ready to integrate"
- "Complements, doesn't compete"

### 4. Domain Separation
- Clear visual separation (Platform vs Service)
- Explicit insurance exclusions
- "Adjacent domain" positioning
- "Parallel success stories"

---

## 🔐 Admin Tools

### Startup Management Dashboard
- Add/edit startup profiles
- Set top pick status
- Adjust priority scores
- Preview carousel appearance
- Analytics on startup performance

### Matching Analytics
- View match score distributions
- Identify low-performing matches
- A/B test different algorithms
- Monitor user feedback

---

## 📱 Mobile Considerations

- Responsive carousel (1 card on mobile, 2 on tablet, 3 on desktop)
- Touch-friendly swipe gestures
- Optimized image loading
- Simplified card layout on small screens

---

## 🔄 Future Enhancements

### V2 Features
- AI-generated personalized USPs
- Video pitch integration
- Live demo scheduling
- Startup comparison tool
- Saved favorites list
- Email digest of new matches

### V3 Features
- LLM-powered matching explanations
- Predictive partnership success scores
- Automated RFP generation
- Integration cost estimates
- ROI calculators

---

## 📖 Documentation Needs

- Admin guide for startup profile creation
- User guide for matching preferences
- API documentation
- USP writing guidelines
- Category definition guide

---

## ✅ Acceptance Criteria

### Carousel Must:
- [ ] Display 3 startups at a time (desktop)
- [ ] Show startup name, logo, category badge
- [ ] Display compelling USP
- [ ] Show match score and reasons
- [ ] Enable smooth navigation
- [ ] Load within 2 seconds
- [ ] Work on mobile/tablet/desktop

### Matching Must:
- [ ] Calculate scores accurately
- [ ] Respect user preferences
- [ ] Exclude insurance-focused startups
- [ ] Rank by strategic fit
- [ ] Update in real-time
- [ ] Handle edge cases gracefully

### Data Quality Must:
- [ ] All top startups have logos
- [ ] USPs are compelling and clear
- [ ] Categories are accurate
- [ ] Credentials are verified
- [ ] Non-competitive areas are explicit
- [ ] Integration complexity is realistic

---

**Implementation Owner**: Engineering Team
**Business Owner**: Product/Partnerships Team
**Timeline**: 11 weeks
**Priority**: High
**Dependencies**: Existing user authentication, database infrastructure

---

## 🎯 Main Matching Section: "Discover Your Agentic Partners"

### User Journey Goals

**Primary Objective**: Each attendee should:
1. **Meet 5 Agentic Startups** - For market education and upskilling on agentic technologies
2. **Select 5 Relevant Startups** - Linked to:
   - Specific insurance use cases
   - Local entity insurance activities
   - Business priorities and strategic goals
   - Operational pain points

### Visual Layout - Main Matching Grid

```
┌──────────────────────────────────────────────────────────────────┐
│  🎯 Discover Your Agentic Partners                               │
│  Goal: Meet 5 for market insights • Select 5 for your use cases  │
├──────────────────────────────────────────────────────────────────┤
│                                                                    │
│  Progress:  Met: 3/5 ⚡  |  Selected: 2/5 ❤️                     │
│                                                                    │
│  ┌─ Filters ────────────────────────────────────────┐            │
│  │ Sort by: ⚡ Most Hearts (38) ▼                    │            │
│  │ Insurance Activity: ☑ Claims  ☑ Underwriting     │            │
│  │ Use Case: ☑ Automation  ☑ Customer Service      │            │
│  └────────────────────────────────────────────────────┘          │
│                                                                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │   [LOGO]     │  │   [LOGO]     │  │   [LOGO]     │           │
│  │              │  │              │  │              │           │
│  │ ClaimsAI     │  │ UnderwriteX  │  │ PolicyAgent  │           │
│  │              │  │              │  │              │           │
│  │ ❤️ 38 hearts │  │ ❤️ 32 hearts │  │ ❤️ 28 hearts │           │
│  │ ✓ You matched│  │              │  │ ✓ You matched│           │
│  │              │  │              │  │              │           │
│  │ "Autonomous  │  │ "AI Under-   │  │ "24/7 Policy │           │
│  │ claims proc- │  │ writing cuts │  │ servicing    │           │
│  │ essing 10x   │  │ time by 60%" │  │ agent"       │           │
│  │ faster"      │  │              │  │              │           │
│  │              │  │              │  │              │           │
│  │ 🏢 Claims    │  │ 🏢 Underw.   │  │ 🏢 Policy    │           │
│  │ 🎯 Automation│  │ 🎯 Risk Ass. │  │ 🎯 Cust Serv │           │
│  │              │  │              │  │              │           │
│  │   [❤️ Match] │  │   [❤️ Match] │  │   [View]     │           │
│  └──────────────┘  └──────────────┘  └──────────────┘           │
│                                                                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │ More cards...│  │              │  │              │           │
│  └──────────────┘  └──────────────┘  └──────────────┘           │
│                                                                    │
│  [Load More Startups]                                             │
└──────────────────────────────────────────────────────────────────┘
```

### Card Design - Startup Card with Hearts

```
┌─────────────────────────────┐
│        [LOGO IMAGE]          │
│                              │
│      Startup Name            │
│                              │
│  ❤️ 38 hearts from attendees│
│  ✓ You matched on 2024-11-10│  ← Shows if user matched
│                              │
│  "One-line value prop that   │
│   shows insurance relevance" │
│                              │
│  🏢 Insurance Activities:    │
│     • Claims Processing      │
│     • Fraud Detection        │
│                              │
│  🎯 Use Cases:               │
│     • Automation             │
│     • Cost Reduction         │
│                              │
│  🌍 Local Entity Fit:        │
│     • High for EU entities   │
│     • GDPR compliant         │
│                              │
│  📊 Business Priority:       │
│     ⭐⭐⭐⭐⭐ (Operational Eff.)│
│                              │
│  [❤️ Match] [📅 Book Meeting]│
│                              │
│  Match Score: 94% 🟢         │
└─────────────────────────────┘
```

---

## 📊 Enhanced Data Models for Matching Goals

### 1. User Progress Tracking

```python
# models.py additions

class UserMatchingProgress(Base):
    __tablename__ = "user_matching_progress"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    
    # Progress Goals
    startups_met_count = Column(Integer, default=0)  # Goal: 5
    startups_met_goal = Column(Integer, default=5)
    
    startups_selected_count = Column(Integer, default=0)  # Goal: 5
    startups_selected_goal = Column(Integer, default=5)
    
    # Lists
    met_startup_ids = Column(JSON, default=list)  # Viewed profiles
    selected_startup_ids = Column(JSON, default=list)  # Hearted/matched
    
    # Completion
    has_met_goal = Column(Boolean, default=False)
    has_selected_goal = Column(Boolean, default=False)
    completed_at = Column(DateTime, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

### 2. Startup Popularity & Engagement

```python
class StartupPopularity(Base):
    __tablename__ = "startup_popularity"
    
    id = Column(Integer, primary_key=True)
    startup_id = Column(String, ForeignKey("startups_enhanced.startup_id"), unique=True)
    
    # Engagement Metrics
    total_hearts = Column(Integer, default=0, index=True)
    total_views = Column(Integer, default=0)
    total_meetings_booked = Column(Integer, default=0)
    
    # Trending
    hearts_last_24h = Column(Integer, default=0)
    hearts_last_7d = Column(Integer, default=0)
    is_trending = Column(Boolean, default=False)
    
    # Lists of user IDs
    hearted_by_user_ids = Column(JSON, default=list)
    viewed_by_user_ids = Column(JSON, default=list)
    
    # Ranking
    popularity_rank = Column(Integer, nullable=True)
    
    # Timestamps
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

### 3. Insurance-Specific Categorization

```python
class InsuranceActivity(str, Enum):
    CLAIMS_PROCESSING = "claims_processing"
    UNDERWRITING = "underwriting"
    FRAUD_DETECTION = "fraud_detection"
    POLICY_ADMINISTRATION = "policy_administration"
    CUSTOMER_SERVICE = "customer_service"
    RISK_ASSESSMENT = "risk_assessment"
    PRICING_OPTIMIZATION = "pricing_optimization"
    COMPLIANCE = "compliance"
    DISTRIBUTION = "distribution"
    REINSURANCE = "reinsurance"

class UseCase(str, Enum):
    AUTOMATION = "automation"
    COST_REDUCTION = "cost_reduction"
    CUSTOMER_EXPERIENCE = "customer_experience"
    RISK_MANAGEMENT = "risk_management"
    REGULATORY_COMPLIANCE = "regulatory_compliance"
    DATA_ANALYTICS = "data_analytics"
    OPERATIONAL_EFFICIENCY = "operational_efficiency"
    FRAUD_PREVENTION = "fraud_prevention"

class StartupInsuranceProfile(Base):
    __tablename__ = "startup_insurance_profiles"
    
    id = Column(Integer, primary_key=True)
    startup_id = Column(String, ForeignKey("startups_enhanced.startup_id"), unique=True)
    
    # Insurance Activities (multi-select)
    insurance_activities = Column(JSON)  # List of InsuranceActivity values
    primary_activity = Column(String, index=True)
    
    # Use Cases (multi-select)
    use_cases = Column(JSON)  # List of UseCase values
    primary_use_case = Column(String, index=True)
    
    # Local Entity Relevance
    regional_fit = Column(JSON)  # {"EU": "high", "APAC": "medium", "NA": "high"}
    regulatory_compliance = Column(JSON)  # ["GDPR", "SOC2", "ISO27001"]
    language_support = Column(JSON)  # ["en", "es", "de", "fr"]
    
    # Business Priority Alignment
    operational_efficiency_score = Column(Float, default=0.0)
    cost_reduction_score = Column(Float, default=0.0)
    customer_satisfaction_score = Column(Float, default=0.0)
    innovation_score = Column(Float, default=0.0)
    compliance_score = Column(Float, default=0.0)
    
    # Implementation Details
    implementation_time_weeks = Column(Integer, nullable=True)
    requires_integration = Column(Boolean, default=True)
    integration_partners = Column(JSON)  # ["Salesforce", "SAP", etc.]
    
    # Success Stories
    insurance_client_count = Column(Integer, default=0)
    insurance_case_studies = Column(JSON)  # List of case study references
    roi_examples = Column(JSON)  # [{"client": "X", "roi": "300%", "timeframe": "6mo"}]
```

### 4. User's Business Context

```python
class UserBusinessContext(Base):
    __tablename__ = "user_business_context"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    
    # User's Role & Responsibilities
    role = Column(String)  # "Claims Manager", "CTO", "Head of Underwriting"
    department = Column(String)
    seniority = Column(String)  # "Manager", "Director", "C-Level"
    
    # Local Entity Information
    entity_region = Column(String)  # "EU", "APAC", "NA", "LATAM"
    entity_countries = Column(JSON)  # ["UK", "Germany", "France"]
    entity_size = Column(String)  # "Small", "Medium", "Large"
    
    # Current Pain Points
    pain_points = Column(JSON)  # ["Manual claims processing", "High fraud rates"]
    
    # Business Priorities (ranked)
    top_priorities = Column(JSON)  # [
    #   {"priority": "Operational Efficiency", "rank": 1},
    #   {"priority": "Cost Reduction", "rank": 2}
    # ]
    
    # Insurance Activities of Interest
    focus_activities = Column(JSON)  # ["claims_processing", "fraud_detection"]
    
    # Use Cases Seeking
    target_use_cases = Column(JSON)  # ["automation", "cost_reduction"]
    
    # Constraints
    budget_range = Column(String)  # "50k-100k", "100k-500k"
    timeline = Column(String)  # "Immediate", "3-6 months", "6-12 months"
    technical_maturity = Column(String)  # "Early", "Growing", "Advanced"
    
    # Integration Requirements
    existing_systems = Column(JSON)  # ["Salesforce", "Guidewire", "Duck Creek"]
    integration_preference = Column(String)  # "API", "Pre-built", "Custom"
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

---

## 🎯 Enhanced Matching Algorithm with Insurance Context

```python
# matching_algorithm.py - Enhanced version

class InsuranceContextMatchingEngine(AgenticMatchingEngine):
    """
    Enhanced matching engine with insurance context and business priorities
    """
    
    def calculate_insurance_match_score(
        self,
        user_context: UserBusinessContext,
        user_prefs: AttendeeMatchingPreferences,
        startup: StartupEnhanced,
        startup_insurance: StartupInsuranceProfile
    ) -> Dict:
        """
        Calculate comprehensive match score with insurance context
        """
        base_scores = super().calculate_match_score(user_prefs, startup)
        
        # Additional insurance-specific scores
        insurance_scores = {
            "activity_match": self._score_activity_match(user_context, startup_insurance),
            "use_case_match": self._score_use_case_match(user_context, startup_insurance),
            "regional_fit": self._score_regional_fit(user_context, startup_insurance),
            "priority_alignment": self._score_priority_alignment(user_context, startup_insurance),
            "pain_point_solution": self._score_pain_point_solution(user_context, startup_insurance),
            "implementation_feasibility": self._score_implementation_feasibility(user_context, startup_insurance)
        }
        
        # Combined weighted score
        all_scores = {**base_scores["component_scores"], **insurance_scores}
        
        weights = {
            # Base scores (50%)
            "strategic_fit": 0.15,
            "capability_match": 0.15,
            "credibility": 0.10,
            "integration_ease": 0.05,
            "non_competitive": 0.05,
            
            # Insurance scores (50%)
            "activity_match": 0.15,
            "use_case_match": 0.15,
            "regional_fit": 0.05,
            "priority_alignment": 0.10,
            "pain_point_solution": 0.03,
            "implementation_feasibility": 0.02
        }
        
        overall = sum(all_scores[k] * weights[k] for k in all_scores.keys())
        
        return {
            "overall_score": overall,
            "component_scores": all_scores,
            "match_reasons": self._generate_insurance_match_reasons(
                user_context, startup, startup_insurance, all_scores
            ),
            "recommendation_priority": self._calculate_priority(overall, user_context, startup_insurance)
        }
    
    def _score_activity_match(
        self,
        user_context: UserBusinessContext,
        startup_insurance: StartupInsuranceProfile
    ) -> float:
        """
        Score based on insurance activity alignment
        """
        if not user_context.focus_activities or not startup_insurance.insurance_activities:
            return 50.0
        
        user_activities = set(user_context.focus_activities)
        startup_activities = set(startup_insurance.insurance_activities)
        
        if not user_activities:
            return 50.0
        
        overlap = len(user_activities & startup_activities)
        score = (overlap / len(user_activities)) * 100.0
        
        # Bonus for primary activity match
        if startup_insurance.primary_activity in user_activities:
            score = min(score + 20.0, 100.0)
        
        return score
    
    def _score_use_case_match(
        self,
        user_context: UserBusinessContext,
        startup_insurance: StartupInsuranceProfile
    ) -> float:
        """
        Score based on use case alignment
        """
        if not user_context.target_use_cases or not startup_insurance.use_cases:
            return 50.0
        
        user_use_cases = set(user_context.target_use_cases)
        startup_use_cases = set(startup_insurance.use_cases)
        
        if not user_use_cases:
            return 50.0
        
        overlap = len(user_use_cases & startup_use_cases)
        score = (overlap / len(user_use_cases)) * 100.0
        
        # Bonus for primary use case match
        if startup_insurance.primary_use_case in user_use_cases:
            score = min(score + 20.0, 100.0)
        
        return score
    
    def _score_regional_fit(
        self,
        user_context: UserBusinessContext,
        startup_insurance: StartupInsuranceProfile
    ) -> float:
        """
        Score based on regional and regulatory fit
        """
        score = 50.0  # Base score
        
        # Regional fit
        if user_context.entity_region and startup_insurance.regional_fit:
            fit_level = startup_insurance.regional_fit.get(user_context.entity_region, "low")
            fit_scores = {"high": 50.0, "medium": 30.0, "low": 10.0}
            score = fit_scores.get(fit_level, 50.0)
        
        # Regulatory compliance bonus
        if startup_insurance.regulatory_compliance:
            score = min(score + 20.0, 100.0)
        
        # Language support bonus
        if user_context.entity_countries and startup_insurance.language_support:
            # Check if startup supports languages for user's countries
            score = min(score + 10.0, 100.0)
        
        return score
    
    def _score_priority_alignment(
        self,
        user_context: UserBusinessContext,
        startup_insurance: StartupInsuranceProfile
    ) -> float:
        """
        Score based on business priority alignment
        """
        if not user_context.top_priorities:
            return 50.0
        
        score = 0.0
        total_weight = 0.0
        
        priority_score_map = {
            "Operational Efficiency": startup_insurance.operational_efficiency_score,
            "Cost Reduction": startup_insurance.cost_reduction_score,
            "Customer Satisfaction": startup_insurance.customer_satisfaction_score,
            "Innovation": startup_insurance.innovation_score,
            "Compliance": startup_insurance.compliance_score
        }
        
        # Weight by priority rank (1st priority = 40%, 2nd = 30%, 3rd = 20%, 4th = 10%)
        weights = [0.40, 0.30, 0.20, 0.10]
        
        for idx, priority_obj in enumerate(user_context.top_priorities[:4]):
            priority_name = priority_obj.get("priority")
            if priority_name in priority_score_map:
                weight = weights[idx] if idx < len(weights) else 0.05
                score += priority_score_map[priority_name] * weight
                total_weight += weight
        
        return score if total_weight > 0 else 50.0
    
    def _score_pain_point_solution(
        self,
        user_context: UserBusinessContext,
        startup_insurance: StartupInsuranceProfile
    ) -> float:
        """
        Score based on pain point resolution capability
        """
        if not user_context.pain_points:
            return 50.0
        
        # This would use NLP/semantic matching in production
        # For now, simple keyword matching
        score = 50.0
        
        if startup_insurance.use_cases:
            # If startup addresses automation and user has "manual" pain points
            pain_point_text = " ".join(user_context.pain_points).lower()
            
            if "automation" in startup_insurance.use_cases and "manual" in pain_point_text:
                score += 25.0
            
            if "fraud_prevention" in startup_insurance.use_cases and "fraud" in pain_point_text:
                score += 25.0
        
        return min(score, 100.0)
    
    def _score_implementation_feasibility(
        self,
        user_context: UserBusinessContext,
        startup_insurance: StartupInsuranceProfile
    ) -> float:
        """
        Score based on implementation feasibility
        """
        score = 50.0
        
        # Timeline match
        if user_context.timeline == "Immediate" and startup_insurance.implementation_time_weeks:
            if startup_insurance.implementation_time_weeks <= 4:
                score += 20.0
            elif startup_insurance.implementation_time_weeks <= 12:
                score += 10.0
        
        # Integration compatibility
        if user_context.existing_systems and startup_insurance.integration_partners:
            user_systems = set(user_context.existing_systems)
            startup_partners = set(startup_insurance.integration_partners)
            
            if user_systems & startup_partners:
                score += 20.0
        
        # Technical maturity match
        if user_context.technical_maturity == "Advanced" and startup_insurance.requires_integration:
            score += 10.0
        
        return min(score, 100.0)
    
    def _generate_insurance_match_reasons(
        self,
        user_context: UserBusinessContext,
        startup: StartupEnhanced,
        startup_insurance: StartupInsuranceProfile,
        scores: Dict
    ) -> List[str]:
        """
        Generate detailed match reasons with insurance context
        """
        reasons = []
        
        # Activity match
        if scores["activity_match"] > 70:
            activities = [a.replace("_", " ").title() for a in startup_insurance.insurance_activities[:2]]
            reasons.append(f"Addresses your focus: {', '.join(activities)}")
        
        # Use case match
        if scores["use_case_match"] > 70:
            use_cases = [u.replace("_", " ").title() for u in startup_insurance.use_cases[:2]]
            reasons.append(f"Delivers: {', '.join(use_cases)}")
        
        # Priority alignment
        if scores["priority_alignment"] > 70 and user_context.top_priorities:
            top_priority = user_context.top_priorities[0]["priority"]
            reasons.append(f"Aligns with priority: {top_priority}")
        
        # Regional fit
        if scores["regional_fit"] > 70:
            reasons.append(f"Strong fit for {user_context.entity_region} region")
        
        # Credibility
        if startup_insurance.insurance_client_count > 0:
            reasons.append(f"Proven with {startup_insurance.insurance_client_count} insurance clients")
        
        # ROI examples
        if startup_insurance.roi_examples:
            roi = startup_insurance.roi_examples[0]
            reasons.append(f"Delivered {roi['roi']} ROI in {roi['timeframe']}")
        
        return reasons
    
    def _calculate_priority(
        self,
        overall_score: float,
        user_context: UserBusinessContext,
        startup_insurance: StartupInsuranceProfile
    ) -> str:
        """
        Calculate recommendation priority
        """
        if overall_score >= 85:
            return "high"
        elif overall_score >= 70:
            return "medium"
        else:
            return "low"
    
    def get_sorted_startups_with_hearts(
        self,
        user_id: int,
        sort_by: str = "hearts",
        filters: Dict = None,
        limit: int = 50
    ) -> List[Dict]:
        """
        Get all startups sorted by popularity with match status
        """
        # Get user context
        user_context = self.db.query(UserBusinessContext).filter(
            UserBusinessContext.user_id == user_id
        ).first()
        
        user_prefs = self.db.query(AttendeeMatchingPreferences).filter(
            AttendeeMatchingPreferences.user_id == user_id
        ).first()
        
        user_progress = self.db.query(UserMatchingProgress).filter(
            UserMatchingProgress.user_id == user_id
        ).first()
        
        if not user_progress:
            user_progress = UserMatchingProgress(user_id=user_id)
            self.db.add(user_progress)
            self.db.commit()
        
        # Query startups
        query = self.db.query(
            StartupEnhanced,
            StartupInsuranceProfile,
            StartupPopularity
        ).join(
            StartupInsuranceProfile,
            StartupEnhanced.startup_id == StartupInsuranceProfile.startup_id
        ).join(
            StartupPopularity,
            StartupEnhanced.startup_id == StartupPopularity.startup_id
        )
        
        # Apply filters
        if filters:
            if filters.get("insurance_activities"):
                query = query.filter(
                    StartupInsuranceProfile.insurance_activities.contains(filters["insurance_activities"])
                )
            
            if filters.get("use_cases"):
                query = query.filter(
                    StartupInsuranceProfile.use_cases.contains(filters["use_cases"])
                )
        
        # Sort
        if sort_by == "hearts":
            query = query.order_by(StartupPopularity.total_hearts.desc())
        elif sort_by == "match_score":
            # Will sort after scoring
            pass
        elif sort_by == "trending":
            query = query.filter(StartupPopularity.is_trending == True)
            query = query.order_by(StartupPopularity.hearts_last_24h.desc())
        
        startups = query.limit(limit).all()
        
        # Score and format
        results = []
        for startup, insurance_profile, popularity in startups:
            # Calculate match score if we have context
            if user_context and user_prefs:
                score_data = self.calculate_insurance_match_score(
                    user_context, user_prefs, startup, insurance_profile
                )
            else:
                score_data = {
                    "overall_score": 50.0,
                    "match_reasons": ["Complete your profile for personalized matching"],
                    "recommendation_priority": "medium"
                }
            
            # Check if user has matched
            is_matched = str(user_id) in popularity.hearted_by_user_ids
            is_viewed = str(user_id) in popularity.viewed_by_user_ids
            
            results.append({
                "startup": startup,
                "insurance_profile": insurance_profile,
                "popularity": {
                    "total_hearts": popularity.total_hearts,
                    "is_trending": popularity.is_trending,
                    "hearts_last_24h": popularity.hearts_last_24h
                },
                "score_data": score_data,
                "user_interaction": {
                    "is_matched": is_matched,
                    "is_viewed": is_viewed,
                    "matched_date": self._get_match_date(user_id, startup.startup_id) if is_matched else None
                }
            })
        
        # Sort by match score if requested
        if sort_by == "match_score":
            results.sort(key=lambda x: x["score_data"]["overall_score"], reverse=True)
        
        return results
    
    def _get_match_date(self, user_id: int, startup_id: str) -> Optional[str]:
        """
        Get the date when user matched with startup
        """
        match = self.db.query(StartupMatch).filter(
            StartupMatch.user_id == user_id,
            StartupMatch.startup_id == startup_id,
            StartupMatch.interested == True
        ).first()
        
        return match.created_at.strftime("%Y-%m-%d") if match else None
    
    def record_heart(self, user_id: int, startup_id: str) -> Dict:
        """
        Record when user hearts/matches a startup
        """
        # Update user progress
        progress = self.db.query(UserMatchingProgress).filter(
            UserMatchingProgress.user_id == user_id
        ).first()
        
        if not progress:
            progress = UserMatchingProgress(user_id=user_id)
            self.db.add(progress)
        
        # Add to selected list if not already there
        if startup_id not in progress.selected_startup_ids:
            progress.selected_startup_ids.append(startup_id)
            progress.startups_selected_count = len(progress.selected_startup_ids)
            
            # Check if goal reached
            if progress.startups_selected_count >= progress.startups_selected_goal:
                progress.has_selected_goal = True
        
        # Update startup popularity
        popularity = self.db.query(StartupPopularity).filter(
            StartupPopularity.startup_id == startup_id
        ).first()
        
        if not popularity:
            popularity = StartupPopularity(startup_id=startup_id)
            self.db.add(popularity)
        
        # Add user to hearted list if not already there
        user_id_str = str(user_id)
        if user_id_str not in popularity.hearted_by_user_ids:
            popularity.hearted_by_user_ids.append(user_id_str)
            popularity.total_hearts += 1
            popularity.hearts_last_24h += 1
            popularity.hearts_last_7d += 1
        
        # Update match record
        match_record = self.db.query(StartupMatch).filter(
            StartupMatch.user_id == user_id,
            StartupMatch.startup_id == startup_id
        ).first()
        
        if match_record:
            match_record.interested = True
        
        self.db.commit()
        
        return {
            "success": True,
            "progress": {
                "selected": progress.startups_selected_count,
                "goal": progress.startups_selected_goal,
                "completed": progress.has_selected_goal
            }
        }
    
    def record_view(self, user_id: int, startup_id: str) -> Dict:
        """
        Record when user views a startup (counts towards "met" goal)
        """
        # Update user progress
        progress = self.db.query(UserMatchingProgress).filter(
            UserMatchingProgress.user_id == user_id
        ).first()
        
        if not progress:
            progress = UserMatchingProgress(user_id=user_id)
            self.db.add(progress)
        
        # Add to met list if not already there
        if startup_id not in progress.met_startup_ids:
            progress.met_startup_ids.append(startup_id)
            progress.startups_met_count = len(progress.met_startup_ids)
            
            # Check if goal reached
            if progress.startups_met_count >= progress.startups_met_goal:
                progress.has_met_goal = True
        
        # Update startup popularity
        popularity = self.db.query(StartupPopularity).filter(
            StartupPopularity.startup_id == startup_id
        ).first()
        
        if not popularity:
            popularity = StartupPopularity(startup_id=startup_id)
            self.db.add(popularity)
        
        # Add user to viewed list if not already there
        user_id_str = str(user_id)
        if user_id_str not in popularity.viewed_by_user_ids:
            popularity.viewed_by_user_ids.append(user_id_str)
            popularity.total_views += 1
        
        # Update match record
        match_record = self.db.query(StartupMatch).filter(
            StartupMatch.user_id == user_id,
            StartupMatch.startup_id == startup_id
        ).first()
        
        if match_record:
            match_record.viewed = True
        
        self.db.commit()
        
        return {
            "success": True,
            "progress": {
                "met": progress.startups_met_count,
                "goal": progress.startups_met_goal,
                "completed": progress.has_met_goal
            }
        }
```

---

## 🎨 Enhanced Frontend Components

### 1. Main Matching Grid Component

```typescript
// components/Matching/MainMatchingGrid.tsx

import { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Heart, Eye, Calendar, TrendingUp } from 'lucide-react';

interface MatchingProgress {
  met: number;
  met_goal: number;
  selected: number;
  selected_goal: number;
  has_met_goal: boolean;
  has_selected_goal: boolean;
}

interface StartupCard {
  id: string;
  name: string;
  logo_url: string;
  usp_short: string;
  insurance_activities: string[];
  use_cases: string[];
  regional_fit: string;
  business_priority_stars: number;
  total_hearts: number;
  is_trending: boolean;
  is_matched: boolean;
  matched_date?: string;
  match_score: number;
  match_reasons: string[];
  recommendation_priority: string;
}

export function MainMatchingGrid() {
  const [startups, setStartups] = useState<StartupCard[]>([]);
  const [progress, setProgress] = useState<MatchingProgress | null>(null);
  const [sortBy, setSortBy] = useState('hearts');
  const [filters, setFilters] = useState({
    insurance_activities: [],
    use_cases: []
  });
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    fetchStartupsAndProgress();
  }, [sortBy, filters]);
  
  const fetchStartupsAndProgress = async () => {
    try {
      const [startupsRes, progressRes] = await Promise.all([
        fetch(`/api/matching/startups?sort_by=${sortBy}&filters=${JSON.stringify(filters)}`, {
          headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
        }),
        fetch('/api/matching/progress', {
          headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
        })
      ]);
      
      const startupsData = await startupsRes.json();
      const progressData = await progressRes.json();
      
      setStartups(startupsData.startups);
      setProgress(progressData);
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };
  
  const handleHeart = async (startupId: string) => {
    try {
      const response = await fetch('/api/matching/heart', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ startup_id: startupId })
      });
      
      const data = await response.json();
      setProgress(data.progress);
      
      // Update local state
      setStartups(startups.map(s => 
        s.id === startupId 
          ? { ...s, is_matched: true, total_hearts: s.total_hearts + 1 }
          : s
      ));
      
      // Show celebration if goal reached
      if (data.progress.completed) {
        showGoalCompletedModal();
      }
    } catch (error) {
      console.error('Error recording heart:', error);
    }
  };
  
  const handleView = async (startupId: string) => {
    try {
      await fetch('/api/matching/view', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ startup_id: startupId })
      });
      
      // Refresh progress
      const progressRes = await fetch('/api/matching/progress', {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });
      const progressData = await progressRes.json();
      setProgress(progressData);
    } catch (error) {
      console.error('Error recording view:', error);
    }
  };
  
  const showGoalCompletedModal = () => {
    // Show celebration modal/toast
    alert('🎉 Congratulations! You\'ve reached your goal!');
  };
  
  if (loading) {
    return <div>Loading startups...</div>;
  }
  
  return (
    <div className="w-full">
      {/* Header & Progress */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-6 rounded-lg mb-6">
        <h2 className="text-2xl font-bold mb-2">🎯 Discover Your Agentic Partners</h2>
        <p className="mb-4">
          Goal: Meet 5 for market insights • Select 5 for your use cases
        </p>
        
        {progress && (
          <div className="flex gap-8">
            <div className="flex items-center gap-2">
              <Eye className="w-5 h-5" />
              <span className="text-lg">
                Met: {progress.met}/{progress.met_goal} ⚡
              </span>
              {progress.has_met_goal && <span className="text-green-300">✓</span>}
            </div>
            
            <div className="flex items-center gap-2">
              <Heart className="w-5 h-5" />
              <span className="text-lg">
                Selected: {progress.selected}/{progress.selected_goal} ❤️
              </span>
              {progress.has_selected_goal && <span className="text-green-300">✓</span>}
            </div>
          </div>
        )}
        
        {/* Progress Bars */}
        {progress && (
          <div className="grid grid-cols-2 gap-4 mt-4">
            <div>
              <div className="w-full bg-white/20 rounded-full h-2">
                <div 
                  className="bg-white h-2 rounded-full transition-all"
                  style={{ width: `${(progress.met / progress.met_goal) * 100}%` }}
                />
              </div>
            </div>
            <div>
              <div className="w-full bg-white/20 rounded-full h-2">
                <div 
                  className="bg-white h-2 rounded-full transition-all"
                  style={{ width: `${(progress.selected / progress.selected_goal) * 100}%` }}
                />
              </div>
            </div>
          </div>
        )}
      </div>
      
      {/* Filters & Sort */}
      <div className="bg-gray-100 p-4 rounded-lg mb-6 flex gap-4 items-center flex-wrap">
        <div className="flex items-center gap-2">
          <label className="font-semibold">Sort by:</label>
          <select 
            value={sortBy} 
            onChange={(e) => setSortBy(e.target.value)}
            className="border rounded px-3 py-1"
          >
            <option value="hearts">❤️ Most Hearts</option>
            <option value="match_score">🎯 Best Match</option>
            <option value="trending">🔥 Trending</option>
          </select>
        </div>
        
        <div className="flex items-center gap-2">
          <label className="font-semibold">Insurance Activity:</label>
          <div className="flex gap-2">
            {['Claims', 'Underwriting', 'Fraud', 'Customer Service'].map(activity => (
              <label key={activity} className="flex items-center gap-1">
                <input type="checkbox" />
                <span className="text-sm">{activity}</span>
              </label>
            ))}
          </div>
        </div>
      </div>
      
      {/* Startup Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {startups.map((startup) => (
          <StartupMatchCard
            key={startup.id}
            startup={startup}
            onHeart={handleHeart}
            onView={handleView}
          />
        ))}
      </div>
    </div>
  );
}

// Individual Startup Card
function StartupMatchCard({ 
  startup, 
  onHeart, 
  onView 
}: { 
  startup: StartupCard;
  onHeart: (id: string) => void;
  onView: (id: string) => void;
}) {
  const handleCardClick = () => {
    onView(startup.id);
    window.location.href = `/startup/${startup.id}`;
  };
  
  return (
    <Card className="p-5 hover:shadow-xl transition-shadow cursor-pointer relative">
      {/* Trending Badge */}
      {startup.is_trending && (
        <div className="absolute top-2 right-2">
          <Badge className="bg-orange-500 text-white">
            <TrendingUp className="w-3 h-3 mr-1" />
            Trending
          </Badge>
        </div>
      )}
      
      <div onClick={handleCardClick}>
        {/* Logo */}
        <div className="flex justify-center mb-3">
          <img 
            src={startup.logo_url || '/placeholder-logo.png'} 
            alt={startup.name}
            className="h-14 w-14 object-contain"
          />
        </div>
        
        {/* Name */}
        <h3 className="text-lg font-bold text-center mb-2">{startup.name}</h3>
        
        {/* Hearts & Match Status */}
        <div className="flex justify-center items-center gap-3 mb-3">
          <div className="flex items-center gap-1 text-red-500">
            <Heart className="w-4 h-4 fill-current" />
            <span className="text-sm font-semibold">{startup.total_hearts} hearts</span>
          </div>
          
          {startup.is_matched && (
            <Badge variant="secondary" className="bg-green-100 text-green-800">
              ✓ You matched
            </Badge>
          )}
        </div>
        
        {startup.is_matched && startup.matched_date && (
          <p className="text-xs text-gray-500 text-center mb-3">
            Matched on {startup.matched_date}
          </p>
        )}
        
        {/* USP */}
        <p className="text-sm text-gray-700 text-center italic mb-4">
          "{startup.usp_short}"
        </p>
        
        {/* Insurance Activities */}
        <div className="mb-3">
          <p className="text-xs font-semibold text-gray-700 mb-1">🏢 Insurance Activities:</p>
          <div className="flex flex-wrap gap-1">
            {startup.insurance_activities.slice(0, 2).map(activity => (
              <Badge key={activity} variant="outline" className="text-xs">
                {activity.replace('_', ' ')}
              </Badge>
            ))}
          </div>
        </div>
        
        {/* Use Cases */}
        <div className="mb-3">
          <p className="text-xs font-semibold text-gray-700 mb-1">🎯 Use Cases:</p>
          <div className="flex flex-wrap gap-1">
            {startup.use_cases.slice(0, 2).map(useCase => (
              <Badge key={useCase} variant="outline" className="text-xs">
                {useCase.replace('_', ' ')}
              </Badge>
            ))}
          </div>
        </div>
        
        {/* Regional Fit */}
        <div className="mb-3">
          <p className="text-xs text-gray-600">
            🌍 {startup.regional_fit}
          </p>
        </div>
        
        {/* Business Priority */}
        <div className="mb-3">
          <p className="text-xs font-semibold text-gray-700">📊 Business Priority:</p>
          <div className="flex items-center gap-1">
            {Array.from({ length: 5 }).map((_, i) => (
              <span key={i} className={i < startup.business_priority_stars ? 'text-yellow-400' : 'text-gray-300'}>
                ⭐
              </span>
            ))}
          </div>
        </div>
        
        {/* Match Score */}
        <div className="mb-4">
          <div className="flex justify-between items-center mb-1">
            <span className="text-xs text-gray-600">Match Score</span>
            <span className="text-xs font-bold text-blue-600">
              {Math.round(startup.match_score)}%
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className={`h-2 rounded-full transition-all ${
                startup.recommendation_priority === 'high' ? 'bg-green-600' :
                startup.recommendation_priority === 'medium' ? 'bg-blue-600' :
                'bg-gray-400'
              }`}
              style={{ width: `${startup.match_score}%` }}
            />
          </div>
        </div>
        
        {/* Match Reasons */}
        <div className="mb-4">
          <p className="text-xs font-semibold text-gray-700 mb-1">Why matched:</p>
          <ul className="text-xs text-gray-600 space-y-1">
            {startup.match_reasons.slice(0, 2).map((reason, idx) => (
              <li key={idx} className="flex items-start">
                <span className="text-green-500 mr-1">✓</span>
                <span>{reason}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
      
      {/* Action Buttons */}
      <div className="grid grid-cols-2 gap-2">
        <Button
          variant={startup.is_matched ? "secondary" : "default"}
          className={startup.is_matched ? "bg-green-100 text-green-800" : ""}
          onClick={(e) => {
            e.stopPropagation();
            if (!startup.is_matched) onHeart(startup.id);
          }}
          disabled={startup.is_matched}
        >
          <Heart className={`w-4 h-4 mr-1 ${startup.is_matched ? 'fill-current' : ''}`} />
          {startup.is_matched ? 'Matched' : 'Match'}
        </Button>
        
        <Button
          variant="outline"
          onClick={(e) => {
            e.stopPropagation();
            // Open booking modal
          }}
        >
          <Calendar className="w-4 h-4 mr-1" />
          Book
        </Button>
      </div>
    </Card>
  );
}
```

---

## 🔌 Additional API Endpoints

```python
# api/main.py - Additional endpoints

@app.get("/api/matching/startups")
async def get_all_startups_with_matches(
    sort_by: str = "hearts",
    filters: Optional[str] = None,
    limit: int = 50,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get all startups with popularity and match info
    """
    engine = InsuranceContextMatchingEngine(db)
    
    filter_dict = json.loads(filters) if filters else {}
    
    results = engine.get_sorted_startups_with_hearts(
        user_id=current_user.id,
        sort_by=sort_by,
        filters=filter_dict,
        limit=limit
    )
    
    # Format for frontend
    startups_data = []
    for result in results:
        startup = result["startup"]
        insurance = result["insurance_profile"]
        popularity = result["popularity"]
        score = result["score_data"]
        interaction = result["user_interaction"]
        
        startups_data.append({
            "id": startup.startup_id,
            "name": startup.name,
            "logo_url": startup.logo_url,
            "usp_short": startup.usp_short,
            "insurance_activities": insurance.insurance_activities,
            "use_cases": insurance.use_cases,
            "regional_fit": f"High fit for {list(insurance.regional_fit.keys())[0] if insurance.regional_fit else 'Global'}",
            "business_priority_stars": int(max(
                insurance.operational_efficiency_score,
                insurance.cost_reduction_score,
                insurance.customer_satisfaction_score
            ) / 20),
            "total_hearts": popularity["total_hearts"],
            "is_trending": popularity["is_trending"],
            "is_matched": interaction["is_matched"],
            "matched_date": interaction["matched_date"],
            "match_score": score["overall_score"],
            "match_reasons": score["match_reasons"],
            "recommendation_priority": score["recommendation_priority"]
        })
    
    return {"startups": startups_data}

@app.get("/api/matching/progress")
async def get_user_progress(
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get user's matching progress
    """
    progress = db.query(UserMatchingProgress).filter(
        UserMatchingProgress.user_id == current_user.id
    ).first()
    
    if not progress:
        progress = UserMatchingProgress(user_id=current_user.id)
        db.add(progress)
        db.commit()
    
    return {
        "met": progress.startups_met_count,
        "met_goal": progress.startups_met_goal,
        "selected": progress.startups_selected_count,
        "selected_goal": progress.startups_selected_goal,
        "has_met_goal": progress.has_met_goal,
        "has_selected_goal": progress.has_selected_goal,
        "completed": progress.has_met_goal and progress.has_selected_goal
    }

@app.post("/api/matching/heart")
async def record_heart(
    request: schemas.HeartRequest,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Record when user hearts a startup
    """
    engine = InsuranceContextMatchingEngine(db)
    result = engine.record_heart(current_user.id, request.startup_id)
    return result

@app.post("/api/matching/view")
async def record_startup_view(
    request: schemas.ViewRequest,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Record when user views a startup
    """
    engine = InsuranceContextMatchingEngine(db)
    result = engine.record_view(current_user.id, request.startup_id)
    return result
```

---

## 📅 Calendar Integration & Meeting Scheduling

### User Journey: Heart ↔️ Meeting Synchronization

**Core Flow:**
1. **User Hearts Startup** → Meeting automatically scheduled
2. **Meeting Time Pre-scheduled** → User hearts after event time set → Auto-added to calendar
3. **User Removes Heart** → Meeting removed from calendar
4. **User Removes Meeting** → Heart automatically removed

```
┌─────────────────────────────────────────────────────────────┐
│                Heart ↔️ Meeting Sync Flow                    │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  User Hearts Startup                                          │
│         ↓                                                     │
│  Check if event time exists                                   │
│         ↓                                                     │
│  ┌─────────────────────┬──────────────────────┐             │
│  │ Event Time Exists?  │  No Event Time Yet   │             │
│  └─────────────────────┴──────────────────────┘             │
│         ↓                        ↓                            │
│  Add to Calendar              Create Pending                  │
│  Send Confirmation            Meeting Request                 │
│         ↓                        ↓                            │
│  User sees meeting            Organizer schedules             │
│  in their calendar            meeting time                    │
│                                  ↓                            │
│                            Auto-add to user's                 │
│                            calendar & notify                  │
│                                                               │
│  User Removes Heart           User Deletes Meeting           │
│         ↓                           ↓                         │
│  Remove from calendar         Remove heart badge              │
│  Send cancellation            Update match status             │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 Data Models for Calendar Integration

### 1. Startup Meeting Events

```python
# models.py additions

class StartupMeetingEvent(Base):
    __tablename__ = "startup_meeting_events"
    
    id = Column(Integer, primary_key=True, index=True)
    startup_id = Column(String, ForeignKey("startups_enhanced.startup_id"), index=True)
    
    # Event Details
    event_title = Column(String)
    event_description = Column(Text)
    
    # Meeting Time
    meeting_datetime = Column(DateTime, nullable=True, index=True)
    duration_minutes = Column(Integer, default=30)
    timezone = Column(String, default="UTC")
    
    # Location
    meeting_location = Column(String, nullable=True)  # Physical or URL
    meeting_type = Column(String, default="virtual")  # "virtual", "in-person", "hybrid"
    meeting_url = Column(String, nullable=True)  # Zoom, Teams, etc.
    
    # Status
    is_scheduled = Column(Boolean, default=False, index=True)
    is_recurring = Column(Boolean, default=False)
    
    # Capacity Management
    max_attendees = Column(Integer, nullable=True)
    current_attendees_count = Column(Integer, default=0)
    is_full = Column(Boolean, default=False)
    
    # Metadata
    created_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

### 2. User Calendar Meetings

```python
class UserCalendarMeeting(Base):
    __tablename__ = "user_calendar_meetings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    startup_id = Column(String, ForeignKey("startups_enhanced.startup_id"), index=True)
    meeting_event_id = Column(Integer, ForeignKey("startup_meeting_events.id"), nullable=True)
    
    # Meeting Details (denormalized for quick access)
    meeting_title = Column(String)
    meeting_datetime = Column(DateTime, index=True)
    duration_minutes = Column(Integer)
    meeting_url = Column(String, nullable=True)
    meeting_location = Column(String, nullable=True)
    
    # Sync Status
    added_to_calendar = Column(Boolean, default=False)
    calendar_event_id = Column(String, nullable=True)  # External calendar ID
    
    # Source of meeting
    source = Column(String, default="heart")  # "heart", "manual", "admin"
    
    # Status
    status = Column(String, default="confirmed")  # "confirmed", "cancelled", "rescheduled"
    
    # User Actions
    user_confirmed = Column(Boolean, default=True)
    user_attended = Column(Boolean, nullable=True)
    
    # Reminders
    reminder_sent = Column(Boolean, default=False)
    reminder_sent_at = Column(DateTime, nullable=True)
    
    # Relationship tracking
    heart_match_id = Column(Integer, ForeignKey("startup_matches.id"), nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    cancelled_at = Column(DateTime, nullable=True)
```

### 3. Meeting Sync Log

```python
class MeetingSyncLog(Base):
    __tablename__ = "meeting_sync_logs"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    startup_id = Column(String, ForeignKey("startups_enhanced.startup_id"))
    calendar_meeting_id = Column(Integer, ForeignKey("user_calendar_meetings.id"))
    
    # Action
    action = Column(String)  # "added", "removed", "heart_added", "heart_removed", "meeting_deleted"
    triggered_by = Column(String)  # "heart", "calendar", "admin"
    
    # Details
    details = Column(JSON)
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow)
```

---

## 🔄 Calendar Sync Engine

```python
# calendar_sync_engine.py

from typing import Optional, Dict
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class CalendarSyncEngine:
    """
    Handles bidirectional sync between hearts and calendar meetings
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def heart_startup(
        self,
        user_id: int,
        startup_id: str,
        user_timezone: str = "UTC"
    ) -> Dict:
        """
        Handle when user hearts a startup:
        1. Check if meeting event exists for startup
        2. If yes, add to user's calendar
        3. If no, create pending meeting request
        4. Update progress tracking
        """
        try:
            # Check if meeting event exists for this startup
            meeting_event = self.db.query(StartupMeetingEvent).filter(
                StartupMeetingEvent.startup_id == startup_id,
                StartupMeetingEvent.is_scheduled == True
            ).first()
            
            if meeting_event:
                # Meeting time already scheduled
                result = self._add_meeting_to_calendar(
                    user_id=user_id,
                    startup_id=startup_id,
                    meeting_event=meeting_event,
                    user_timezone=user_timezone
                )
                
                return {
                    "success": True,
                    "meeting_scheduled": True,
                    "meeting_datetime": meeting_event.meeting_datetime,
                    "meeting_url": meeting_event.meeting_url,
                    "calendar_meeting_id": result["calendar_meeting_id"],
                    "message": f"Meeting scheduled for {meeting_event.meeting_datetime.strftime('%Y-%m-%d %H:%M')} added to your calendar"
                }
            else:
                # No meeting time yet - create pending request
                result = self._create_pending_meeting_request(
                    user_id=user_id,
                    startup_id=startup_id
                )
                
                return {
                    "success": True,
                    "meeting_scheduled": False,
                    "pending_request_id": result["request_id"],
                    "message": "Interest recorded. You'll be notified when meeting is scheduled."
                }
        
        except Exception as e:
            logger.error(f"Error in heart_startup: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def unheart_startup(
        self,
        user_id: int,
        startup_id: str
    ) -> Dict:
        """
        Handle when user removes heart:
        1. Find associated calendar meeting
        2. Remove from calendar
        3. Send cancellation notification
        4. Update progress tracking
        """
        try:
            # Find calendar meeting
            calendar_meeting = self.db.query(UserCalendarMeeting).filter(
                UserCalendarMeeting.user_id == user_id,
                UserCalendarMeeting.startup_id == startup_id,
                UserCalendarMeeting.status == "confirmed"
            ).first()
            
            if calendar_meeting:
                # Cancel meeting
                calendar_meeting.status = "cancelled"
                calendar_meeting.cancelled_at = datetime.utcnow()
                
                # Log the action
                self._log_sync_action(
                    user_id=user_id,
                    startup_id=startup_id,
                    calendar_meeting_id=calendar_meeting.id,
                    action="removed",
                    triggered_by="heart",
                    details={"reason": "User removed heart"}
                )
                
                self.db.commit()
                
                # Update external calendar if integrated
                if calendar_meeting.calendar_event_id:
                    self._remove_from_external_calendar(calendar_meeting)
                
                return {
                    "success": True,
                    "meeting_removed": True,
                    "message": "Meeting removed from your calendar"
                }
            else:
                return {
                    "success": True,
                    "meeting_removed": False,
                    "message": "No scheduled meeting found"
                }
        
        except Exception as e:
            logger.error(f"Error in unheart_startup: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def remove_meeting(
        self,
        user_id: int,
        calendar_meeting_id: int
    ) -> Dict:
        """
        Handle when user removes meeting from calendar:
        1. Remove meeting record
        2. Remove heart from startup
        3. Update match status
        """
        try:
            # Find calendar meeting
            calendar_meeting = self.db.query(UserCalendarMeeting).filter(
                UserCalendarMeeting.id == calendar_meeting_id,
                UserCalendarMeeting.user_id == user_id
            ).first()
            
            if not calendar_meeting:
                return {
                    "success": False,
                    "error": "Meeting not found"
                }
            
            startup_id = calendar_meeting.startup_id
            
            # Cancel meeting
            calendar_meeting.status = "cancelled"
            calendar_meeting.cancelled_at = datetime.utcnow()
            
            # Remove heart from startup
            self._remove_heart_from_startup(user_id, startup_id)
            
            # Log the action
            self._log_sync_action(
                user_id=user_id,
                startup_id=startup_id,
                calendar_meeting_id=calendar_meeting_id,
                action="meeting_deleted",
                triggered_by="calendar",
                details={"reason": "User deleted meeting from calendar"}
            )
            
            self.db.commit()
            
            return {
                "success": True,
                "heart_removed": True,
                "message": "Meeting cancelled and heart removed"
            }
        
        except Exception as e:
            logger.error(f"Error in remove_meeting: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def schedule_meeting_for_startup(
        self,
        startup_id: str,
        meeting_datetime: datetime,
        duration_minutes: int = 30,
        meeting_url: Optional[str] = None,
        meeting_location: Optional[str] = None,
        meeting_type: str = "virtual",
        max_attendees: Optional[int] = None,
        scheduled_by_user_id: Optional[int] = None
    ) -> Dict:
        """
        Admin/organizer schedules a meeting for a startup.
        Automatically adds to calendars of all users who have hearted.
        """
        try:
            # Get or create meeting event
            meeting_event = self.db.query(StartupMeetingEvent).filter(
                StartupMeetingEvent.startup_id == startup_id
            ).first()
            
            if not meeting_event:
                # Get startup info
                startup = self.db.query(StartupEnhanced).filter(
                    StartupEnhanced.startup_id == startup_id
                ).first()
                
                meeting_event = StartupMeetingEvent(
                    startup_id=startup_id,
                    event_title=f"Meet {startup.name if startup else 'Startup'}",
                    event_description=f"Scheduled meeting with {startup.name if startup else 'startup'}",
                    created_by_user_id=scheduled_by_user_id
                )
                self.db.add(meeting_event)
            
            # Update meeting details
            meeting_event.meeting_datetime = meeting_datetime
            meeting_event.duration_minutes = duration_minutes
            meeting_event.meeting_url = meeting_url
            meeting_event.meeting_location = meeting_location
            meeting_event.meeting_type = meeting_type
            meeting_event.max_attendees = max_attendees
            meeting_event.is_scheduled = True
            meeting_event.updated_at = datetime.utcnow()
            
            self.db.commit()
            
            # Find all users who have hearted this startup
            hearted_users = self.db.query(StartupMatch).filter(
                StartupMatch.startup_id == startup_id,
                StartupMatch.interested == True
            ).all()
            
            # Add to each user's calendar
            added_count = 0
            for match in hearted_users:
                result = self._add_meeting_to_calendar(
                    user_id=match.user_id,
                    startup_id=startup_id,
                    meeting_event=meeting_event,
                    user_timezone="UTC"  # Get from user profile
                )
                
                if result["success"]:
                    added_count += 1
                    
                    # Send notification to user
                    self._send_meeting_scheduled_notification(
                        user_id=match.user_id,
                        startup_id=startup_id,
                        meeting_event=meeting_event
                    )
            
            return {
                "success": True,
                "meeting_event_id": meeting_event.id,
                "users_notified": added_count,
                "meeting_datetime": meeting_datetime,
                "message": f"Meeting scheduled and added to {added_count} calendars"
            }
        
        except Exception as e:
            logger.error(f"Error in schedule_meeting_for_startup: {e}")
            self.db.rollback()
            return {
                "success": False,
                "error": str(e)
            }
    
    def _add_meeting_to_calendar(
        self,
        user_id: int,
        startup_id: str,
        meeting_event: StartupMeetingEvent,
        user_timezone: str = "UTC"
    ) -> Dict:
        """
        Add meeting to user's calendar
        """
        try:
            # Check if already exists
            existing = self.db.query(UserCalendarMeeting).filter(
                UserCalendarMeeting.user_id == user_id,
                UserCalendarMeeting.startup_id == startup_id,
                UserCalendarMeeting.status == "confirmed"
            ).first()
            
            if existing:
                return {
                    "success": True,
                    "calendar_meeting_id": existing.id,
                    "already_exists": True
                }
            
            # Get startup for meeting title
            startup = self.db.query(StartupEnhanced).filter(
                StartupEnhanced.startup_id == startup_id
            ).first()
            
            # Create calendar meeting
            calendar_meeting = UserCalendarMeeting(
                user_id=user_id,
                startup_id=startup_id,
                meeting_event_id=meeting_event.id,
                meeting_title=f"Meet {startup.name if startup else 'Startup'}",
                meeting_datetime=meeting_event.meeting_datetime,
                duration_minutes=meeting_event.duration_minutes,
                meeting_url=meeting_event.meeting_url,
                meeting_location=meeting_event.meeting_location,
                source="heart",
                status="confirmed",
                added_to_calendar=True
            )
            
            self.db.add(calendar_meeting)
            
            # Update meeting event attendee count
            meeting_event.current_attendees_count += 1
            if meeting_event.max_attendees and meeting_event.current_attendees_count >= meeting_event.max_attendees:
                meeting_event.is_full = True
            
            # Log the action
            self._log_sync_action(
                user_id=user_id,
                startup_id=startup_id,
                calendar_meeting_id=calendar_meeting.id,
                action="added",
                triggered_by="heart",
                details={
                    "meeting_datetime": meeting_event.meeting_datetime.isoformat(),
                    "meeting_url": meeting_event.meeting_url
                }
            )
            
            self.db.commit()
            
            # Add to external calendar if integrated
            if self._has_external_calendar_integration(user_id):
                external_event_id = self._add_to_external_calendar(
                    user_id, calendar_meeting
                )
                calendar_meeting.calendar_event_id = external_event_id
                self.db.commit()
            
            return {
                "success": True,
                "calendar_meeting_id": calendar_meeting.id,
                "already_exists": False
            }
        
        except Exception as e:
            logger.error(f"Error adding meeting to calendar: {e}")
            self.db.rollback()
            return {
                "success": False,
                "error": str(e)
            }
    
    def _create_pending_meeting_request(
        self,
        user_id: int,
        startup_id: str
    ) -> Dict:
        """
        Create pending meeting request when no time is scheduled yet
        """
        # The heart is recorded in the matching engine
        # This just tracks that user wants a meeting
        
        return {
            "request_id": f"{user_id}_{startup_id}",
            "status": "pending"
        }
    
    def _remove_heart_from_startup(
        self,
        user_id: int,
        startup_id: str
    ):
        """
        Remove heart from startup match
        """
        # Update match record
        match = self.db.query(StartupMatch).filter(
            StartupMatch.user_id == user_id,
            StartupMatch.startup_id == startup_id
        ).first()
        
        if match:
            match.interested = False
        
        # Update progress
        progress = self.db.query(UserMatchingProgress).filter(
            UserMatchingProgress.user_id == user_id
        ).first()
        
        if progress and startup_id in progress.selected_startup_ids:
            progress.selected_startup_ids.remove(startup_id)
            progress.startups_selected_count = len(progress.selected_startup_ids)
            progress.has_selected_goal = progress.startups_selected_count >= progress.startups_selected_goal
        
        # Update popularity
        popularity = self.db.query(StartupPopularity).filter(
            StartupPopularity.startup_id == startup_id
        ).first()
        
        if popularity:
            user_id_str = str(user_id)
            if user_id_str in popularity.hearted_by_user_ids:
                popularity.hearted_by_user_ids.remove(user_id_str)
                popularity.total_hearts = max(0, popularity.total_hearts - 1)
    
    def _log_sync_action(
        self,
        user_id: int,
        startup_id: str,
        calendar_meeting_id: Optional[int],
        action: str,
        triggered_by: str,
        details: Dict
    ):
        """
        Log sync action for audit trail
        """
        log_entry = MeetingSyncLog(
            user_id=user_id,
            startup_id=startup_id,
            calendar_meeting_id=calendar_meeting_id,
            action=action,
            triggered_by=triggered_by,
            details=details
        )
        self.db.add(log_entry)
    
    def _send_meeting_scheduled_notification(
        self,
        user_id: int,
        startup_id: str,
        meeting_event: StartupMeetingEvent
    ):
        """
        Send notification to user about scheduled meeting
        """
        # This would integrate with notification system
        # For now, just log
        logger.info(f"Sending meeting notification to user {user_id} for startup {startup_id}")
    
    def _has_external_calendar_integration(self, user_id: int) -> bool:
        """
        Check if user has external calendar (Google, Outlook) integrated
        """
        # Check user settings for calendar integration
        # For now, return False
        return False
    
    def _add_to_external_calendar(
        self,
        user_id: int,
        calendar_meeting: UserCalendarMeeting
    ) -> Optional[str]:
        """
        Add meeting to external calendar (Google Calendar, Outlook, etc.)
        Returns external event ID
        """
        # This would integrate with Google Calendar API, Outlook API, etc.
        # For now, return None
        return None
    
    def _remove_from_external_calendar(
        self,
        calendar_meeting: UserCalendarMeeting
    ):
        """
        Remove meeting from external calendar
        """
        # This would integrate with calendar APIs
        pass
    
    def get_user_calendar_meetings(
        self,
        user_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict]:
        """
        Get all calendar meetings for user
        """
        query = self.db.query(UserCalendarMeeting).filter(
            UserCalendarMeeting.user_id == user_id,
            UserCalendarMeeting.status == "confirmed"
        )
        
        if start_date:
            query = query.filter(UserCalendarMeeting.meeting_datetime >= start_date)
        
        if end_date:
            query = query.filter(UserCalendarMeeting.meeting_datetime <= end_date)
        
        meetings = query.order_by(UserCalendarMeeting.meeting_datetime).all()
        
        # Format for frontend
        result = []
        for meeting in meetings:
            startup = self.db.query(StartupEnhanced).filter(
                StartupEnhanced.startup_id == meeting.startup_id
            ).first()
            
            result.append({
                "id": meeting.id,
                "startup_id": meeting.startup_id,
                "startup_name": startup.name if startup else "Unknown",
                "startup_logo": startup.logo_url if startup else None,
                "meeting_title": meeting.meeting_title,
                "meeting_datetime": meeting.meeting_datetime.isoformat(),
                "duration_minutes": meeting.duration_minutes,
                "meeting_url": meeting.meeting_url,
                "meeting_location": meeting.meeting_location,
                "status": meeting.status,
                "can_remove": True
            })
        
        return result
```

---

## 🎨 Frontend Components for Calendar Integration

### 1. Enhanced Startup Card with Calendar Sync

```typescript
// components/Matching/StartupCardWithCalendar.tsx

import { useState } from 'react';
import { Heart, Calendar, Check, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';

interface StartupCardProps {
  startup: any;
  onHeartToggle: (startupId: string, isHearted: boolean) => void;
}

export function StartupCardWithCalendar({ startup, onHeartToggle }: StartupCardProps) {
  const [isHearted, setIsHearted] = useState(startup.is_matched);
  const [showMeetingDialog, setShowMeetingDialog] = useState(false);
  const [meetingInfo, setMeetingInfo] = useState(null);
  const [loading, setLoading] = useState(false);
  
  const handleHeartClick = async () => {
    setLoading(true);
    
    try {
      if (!isHearted) {
        // Adding heart - might schedule meeting
        const response = await fetch('/api/calendar/heart', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ startup_id: startup.id })
        });
        
        const data = await response.json();
        
        if (data.success) {
          setIsHearted(true);
          
          if (data.meeting_scheduled) {
            // Meeting was scheduled - show confirmation
            setMeetingInfo({
              datetime: data.meeting_datetime,
              url: data.meeting_url,
              message: data.message
            });
            setShowMeetingDialog(true);
          } else {
            // No meeting yet - show pending message
            showToast('Interest recorded! You\'ll be notified when meeting is scheduled.');
          }
          
          onHeartToggle(startup.id, true);
        }
      } else {
        // Removing heart - will remove meeting
        const confirmed = await confirmRemoveHeart();
        
        if (confirmed) {
          const response = await fetch('/api/calendar/unheart', {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${localStorage.getItem('token')}`,
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({ startup_id: startup.id })
          });
          
          const data = await response.json();
          
          if (data.success) {
            setIsHearted(false);
            
            if (data.meeting_removed) {
              showToast('Meeting removed from your calendar');
            }
            
            onHeartToggle(startup.id, false);
          }
        }
      }
    } catch (error) {
      console.error('Error toggling heart:', error);
      showToast('Error updating. Please try again.');
    } finally {
      setLoading(false);
    }
  };
  
  const confirmRemoveHeart = async (): Promise<boolean> => {
    return window.confirm(
      'Removing your heart will also cancel the scheduled meeting. Continue?'
    );
  };
  
  const showToast = (message: string) => {
    // Implement toast notification
    alert(message);
  };
  
  return (
    <>
      <Card className="p-5">
        {/* Startup card content */}
        
        <div className="grid grid-cols-2 gap-2">
          <Button
            variant={isHearted ? "secondary" : "default"}
            className={isHearted ? "bg-red-100 text-red-800" : ""}
            onClick={handleHeartClick}
            disabled={loading}
          >
            <Heart className={`w-4 h-4 mr-1 ${isHearted ? 'fill-current' : ''}`} />
            {loading ? 'Processing...' : isHearted ? 'Hearted' : 'Heart'}
          </Button>
          
          <Button
            variant="outline"
            onClick={() => window.location.href = `/startup/${startup.id}`}
          >
            View Details
          </Button>
        </div>
      </Card>
      
      {/* Meeting Confirmation Dialog */}
      <Dialog open={showMeetingDialog} onOpenChange={setShowMeetingDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>✅ Meeting Added to Calendar!</DialogTitle>
          </DialogHeader>
          
          {meetingInfo && (
            <div className="space-y-4">
              <div className="flex items-center gap-2 text-green-600">
                <Check className="w-5 h-5" />
                <span className="font-semibold">{meetingInfo.message}</span>
              </div>
              
              <div className="bg-gray-50 p-4 rounded-lg space-y-2">
                <div>
                  <span className="font-semibold">Date & Time:</span>
                  <br />
                  <span>{new Date(meetingInfo.datetime).toLocaleString()}</span>
                </div>
                
                {meetingInfo.url && (
                  <div>
                    <span className="font-semibold">Meeting Link:</span>
                    <br />
                    <a 
                      href={meetingInfo.url} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:underline"
                    >
                      {meetingInfo.url}
                    </a>
                  </div>
                )}
              </div>
              
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
                  onClick={() => setShowMeetingDialog(false)}
                  className="flex-1"
                >
                  Close
                </Button>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </>
  );
}
```

### 2. Calendar View Component

```typescript
// components/Calendar/MeetingsCalendar.tsx

import { useState, useEffect } from 'react';
import { Calendar, Trash2, ExternalLink } from 'lucide-react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';

interface Meeting {
  id: number;
  startup_id: string;
  startup_name: string;
  startup_logo: string;
  meeting_title: string;
  meeting_datetime: string;
  duration_minutes: number;
  meeting_url?: string;
  meeting_location?: string;
  can_remove: boolean;
}

export function MeetingsCalendar() {
  const [meetings, setMeetings] = useState<Meeting[]>([]);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    fetchMeetings();
  }, []);
  
  const fetchMeetings = async () => {
    try {
      const response = await fetch('/api/calendar/meetings', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      const data = await response.json();
      setMeetings(data.meetings);
    } catch (error) {
      console.error('Error fetching meetings:', error);
    } finally {
      setLoading(false);
    }
  };
  
  const handleRemoveMeeting = async (meetingId: number, startupName: string) => {
    const confirmed = window.confirm(
      `Removing this meeting will also remove your heart from ${startupName}. Continue?`
    );
    
    if (!confirmed) return;
    
    try {
      const response = await fetch('/api/calendar/remove-meeting', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ calendar_meeting_id: meetingId })
      });
      
      const data = await response.json();
      
      if (data.success) {
        // Remove from UI
        setMeetings(meetings.filter(m => m.id !== meetingId));
        alert('Meeting cancelled and heart removed');
      }
    } catch (error) {
      console.error('Error removing meeting:', error);
      alert('Error removing meeting. Please try again.');
    }
  };
  
  if (loading) {
    return <div>Loading your meetings...</div>;
  }
  
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold flex items-center gap-2">
          <Calendar className="w-6 h-6" />
          Your Startup Meetings
        </h2>
        <span className="text-gray-600">
          {meetings.length} scheduled meeting{meetings.length !== 1 ? 's' : ''}
        </span>
      </div>
      
      {meetings.length === 0 ? (
        <Card className="p-8 text-center text-gray-500">
          <Calendar className="w-12 h-12 mx-auto mb-4 text-gray-400" />
          <p>No meetings scheduled yet.</p>
          <p className="text-sm mt-2">Heart startups to schedule meetings!</p>
        </Card>
      ) : (
        <div className="space-y-4">
          {meetings.map((meeting) => (
            <Card key={meeting.id} className="p-5">
              <div className="flex items-start gap-4">
                {/* Startup Logo */}
                <div className="flex-shrink-0">
                  <img 
                    src={meeting.startup_logo || '/placeholder-logo.png'}
                    alt={meeting.startup_name}
                    className="w-16 h-16 object-contain rounded"
                  />
                </div>
                
                {/* Meeting Details */}
                <div className="flex-1">
                  <h3 className="font-bold text-lg mb-1">{meeting.meeting_title}</h3>
                  <p className="text-gray-600 mb-2">{meeting.startup_name}</p>
                  
                  <div className="space-y-1 text-sm">
                    <div className="flex items-center gap-2">
                      <Calendar className="w-4 h-4 text-gray-500" />
                      <span className="font-semibold">
                        {new Date(meeting.meeting_datetime).toLocaleString()}
                      </span>
                      <span className="text-gray-500">
                        ({meeting.duration_minutes} min)
                      </span>
                    </div>
                    
                    {meeting.meeting_url && (
                      <div className="flex items-center gap-2">
                        <ExternalLink className="w-4 h-4 text-gray-500" />
                        <a 
                          href={meeting.meeting_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-blue-600 hover:underline"
                        >
                          Join Meeting
                        </a>
                      </div>
                    )}
                    
                    {meeting.meeting_location && (
                      <div className="text-gray-600">
                        📍 {meeting.meeting_location}
                      </div>
                    )}
                  </div>
                </div>
                
                {/* Actions */}
                {meeting.can_remove && (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleRemoveMeeting(meeting.id, meeting.startup_name)}
                    className="text-red-600 hover:text-red-700 hover:bg-red-50"
                  >
                    <Trash2 className="w-4 h-4 mr-1" />
                    Remove
                  </Button>
                )}
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
```

---

## 🔌 API Endpoints for Calendar Integration

```python
# api/main.py - Calendar endpoints

from calendar_sync_engine import CalendarSyncEngine

@app.post("/api/calendar/heart")
async def heart_with_calendar_sync(
    request: schemas.HeartRequest,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Heart a startup and handle calendar synchronization
    """
    # First, record the heart in matching engine
    matching_engine = InsuranceContextMatchingEngine(db)
    match_result = matching_engine.record_heart(current_user.id, request.startup_id)
    
    # Then, handle calendar sync
    calendar_engine = CalendarSyncEngine(db)
    calendar_result = calendar_engine.heart_startup(
        user_id=current_user.id,
        startup_id=request.startup_id,
        user_timezone=request.timezone or "UTC"
    )
    
    return {
        **match_result,
        **calendar_result
    }

@app.post("/api/calendar/unheart")
async def unheart_with_calendar_sync(
    request: schemas.UnheartRequest,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Remove heart and cancel meeting
    """
    calendar_engine = CalendarSyncEngine(db)
    result = calendar_engine.unheart_startup(
        user_id=current_user.id,
        startup_id=request.startup_id
    )
    
    return result

@app.post("/api/calendar/remove-meeting")
async def remove_meeting_and_heart(
    request: schemas.RemoveMeetingRequest,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Remove meeting from calendar and remove heart
    """
    calendar_engine = CalendarSyncEngine(db)
    result = calendar_engine.remove_meeting(
        user_id=current_user.id,
        calendar_meeting_id=request.calendar_meeting_id
    )
    
    return result

@app.get("/api/calendar/meetings")
async def get_user_meetings(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get all user's calendar meetings
    """
    calendar_engine = CalendarSyncEngine(db)
    
    start = datetime.fromisoformat(start_date) if start_date else None
    end = datetime.fromisoformat(end_date) if end_date else None
    
    meetings = calendar_engine.get_user_calendar_meetings(
        user_id=current_user.id,
        start_date=start,
        end_date=end
    )
    
    return {"meetings": meetings}

@app.post("/api/admin/schedule-meeting")
async def schedule_startup_meeting(
    request: schemas.ScheduleMeetingRequest,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Admin/organizer schedules meeting for a startup
    Automatically adds to calendars of all users who hearted
    """
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    calendar_engine = CalendarSyncEngine(db)
    result = calendar_engine.schedule_meeting_for_startup(
        startup_id=request.startup_id,
        meeting_datetime=datetime.fromisoformat(request.meeting_datetime),
        duration_minutes=request.duration_minutes,
        meeting_url=request.meeting_url,
        meeting_location=request.meeting_location,
        meeting_type=request.meeting_type,
        max_attendees=request.max_attendees,
        scheduled_by_user_id=current_user.id
    )
    
    return result
```

---

## 📋 Pydantic Schemas

```python
# schemas.py additions

class HeartRequest(BaseModel):
    startup_id: str
    timezone: Optional[str] = "UTC"

class UnheartRequest(BaseModel):
    startup_id: str

class RemoveMeetingRequest(BaseModel):
    calendar_meeting_id: int

class ScheduleMeetingRequest(BaseModel):
    startup_id: str
    meeting_datetime: str  # ISO format
    duration_minutes: int = 30
    meeting_url: Optional[str] = None
    meeting_location: Optional[str] = None
    meeting_type: str = "virtual"
    max_attendees: Optional[int] = None
```

---

## ✅ User Experience Flow Examples

### Scenario 1: User Hearts Startup with Scheduled Meeting
```
1. User clicks ❤️ on "ClaimsAI" startup
2. System checks - meeting already scheduled for Nov 20, 2pm
3. Meeting automatically added to user's calendar
4. Confirmation dialog shows:
   ✅ "Meeting Added to Calendar!"
   📅 Nov 20, 2024 at 2:00 PM
   🔗 Join Link: zoom.us/j/123456
5. User can view in calendar or close dialog
```

### Scenario 2: User Hearts Startup with No Meeting Yet
```
1. User clicks ❤️ on "PolicyAgent" startup
2. System checks - no meeting scheduled yet
3. Toast notification: "Interest recorded! You'll be notified when meeting is scheduled."
4. Heart badge shows on card
5. Later, when organizer schedules meeting:
   → Notification sent to user
   → Meeting auto-added to calendar
   → Email confirmation sent
```

### Scenario 3: User Removes Heart
```
1. User clicks filled ❤️ to remove heart
2. Confirmation dialog: "Removing your heart will also cancel the scheduled meeting. Continue?"
3. User confirms
4. Meeting removed from calendar
5. Heart badge removed from card
6. Progress counter updates (Selected: 4/5)
```

### Scenario 4: User Deletes Meeting from Calendar
```
1. User goes to Calendar view
2. Clicks "Remove" on "ClaimsAI" meeting
3. Confirmation: "Removing this meeting will also remove your heart from ClaimsAI. Continue?"
4. User confirms
5. Meeting deleted from calendar
6. Heart automatically removed from ClaimsAI card
7. Match status updated
```

---

*End of Enhanced Implementation Plan with Calendar Integration*
