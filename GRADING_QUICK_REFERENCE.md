# AXA Grading System - Quick Reference

## What Each Grade Means

```
A+  → Exceptional - PURSUE IMMEDIATELY
      Scaling platform, Series C+, EU-based, 3+ use cases, Topic 1 AI
      
A   → Excellent - ACTIVELY EVALUATE  
      Proven growth, Series B-C, EU, 2-3 use cases, strong AI
      
A-  → Very Good - STRONG CANDIDATE
      Good growth, Series A-B, EU, multiple use cases, AI-capable
      
B+  → Good - EVALUATE FOR FIT
      Growing, Series A+, EU preferred, 1-2 use cases, AI present
      
B   → Acceptable - CONSIDER WITH RESEARCH
      Early growth, Seed-A, flexible location, one good use case
      
B-  → Marginal - REVISIT IN 12 MONTHS
      Early stage, limited funding, location/focus concerns
      
C+  → Basic - MONITOR ONLY
      Pre-growth, minimal funding, EU not required
      
C   → Limited - NOT SUITABLE NOW
      Very early, seed-only, weak market fit
      
C-  → Weak - NOT SUITABLE
      Prototype, no funding, misaligned
      
D   → Poor - SKIP
      Unvalidated, minimal traction
      
F   → Unsuitable - DO NOT PURSUE
      Fundamental misalignment with AXA
```

## How Grades Are Calculated

### The Components (160 points total)

| Category | Points | What Matters |
|----------|--------|-------------|
| **Market Fit** | 0-25 | Customer traction, funding proof |
| **Scalability** | 0-25 | Already deployed at scale? |
| **Innovation** | 0-25 | AI/agentic capabilities |
| **Financial Health** | 0-25 | Funding stage, sustainability |
| **Corporate Experience** | 0-20 | Enterprise clients? Implementation track record? |
| **Use Case Breadth** | 0-20 | How many business problems can it solve? |
| **Geographic Fit** | 0-20 | EU-based? GDPR compliant? |
| **Risk Penalties** | -0-15 | Early stage? No funding? Wrong location? |

**Formula**: Total these up (max 160) → Divide by 1.6 → Get 0-100 score → Map to A+ through F

### Quick Scoring Shortcuts

**High scores on...**
- **Market Fit**: Company raised $20M+ or more (shows market validated their idea)
- **Scalability**: Already scaling or in growth stage with 2+ use cases
- **Innovation**: Topic 1 (Agentic) = 24/25 | Topic 2-5 (AI-focused) = 20/25
- **Financial Health**: Series C or Series D (shows investor confidence)
- **Corporate Experience**: Currently used by multiple enterprise customers
- **Use Case Breadth**: 3-4 different business problems the product solves
- **Geographic Fit**: Based in Germany, France, Spain, or other EU core (20/20)

**What kills a grade...**
- No external funding = -8 points
- Prototype stage = -5 points  
- Outside EU with data concerns = -3 points
- Single narrow use case = Can't exceed B-

## When to Pitch to Which Grade

### A+ / A Startups (Top Tier)
→ **Schedule partnership conversations immediately**
→ These are the ones AXA should be integrating with NOW
→ Have proven market fit, funding, and enterprise experience

### B+ / B Startups (Good Fit)
→ **Evaluate for specific business unit alignment**
→ "Does this solve one of our key business problems?"
→ Strong product, may need customization for AXA

### B- / C+ Startups (Monitoring)
→ **Stay in touch, review quarterly**
→ Good product-market fit, but not yet partnership-ready
→ Could become A/B tier in 12-24 months as they grow

### C / C- / D / F Startups (Skip)
→ **Not suitable for partnership right now**
→ Come back in 12+ months if they show significant traction
→ Focus energy on A/B tiers

## The Three Key AXA Priorities (Baked Into Grades)

### 1. EU Location Matters
- **Core EU (Germany, France, Spain, Italy, Netherlands, Belgium)**: 20/20 points
- **Other EU or Switzerland**: 17-19/20 points
- **US/Canada**: 8/20 points
- **Asia/other**: 0-6/20 points

Why? AXA is EU-headquartered. Data transfer regulations favor EU partners.

### 2. Agentic AI Wins
- **Topic 1 (Agentic Platforms)**: 24/25 points - Highest innovation score
- **Topics 2-5 (AI-focused)**: 20/25 points - Strong AI
- **Topics 6-9 (Specialty)**: 12/25 points - Some AI
- **Others**: 5/25 points - No AI advantage

Why? Agentic systems can autonomously handle complex processes - exactly what AXA needs for insurance automation.

### 3. Enterprise-Ready Matters More Than Cutting Edge
- Already selling to enterprises (provider status): 18/20 points
- Otherwise: 0/20 points

Why? AXA is a mega-enterprise. Products need proven enterprise implementation experience.

## Example Grades

### A+ Example: European Agentic Platform
```
Company: RoboProcess AI (Germany)
Funding: Series C ($35M raised)
Stage: Scaling
Use Cases: Claims automation, underwriting, customer service (3 use cases)
Innovation: Topic 1 (Agentic) 
Clients: Deutsche Bank, Allianz, KPMG (enterprise provider)

Scoring:
Market Fit: 19 (proof from $35M + Series C status)
Scalability: 23 (scaling + 3 use cases)
Innovation: 24 (Topic 1 agentic)
Financial Health: 22 (Series C)
Corporate Experience: 20 (actively used by Allianz)
Use Case Breadth: 14 (3 use cases)
Geographic Fit: 20 (Germany/EU core)
Penalties: 0 (no red flags)

Total: 162 points → 101 normalized → A+ GRADE
```

### B+ Example: Growing AI Solutions
```
Company: ClaimsAI (UK)
Funding: Series A ($4M raised)
Stage: Growth
Use Cases: Claims triage, fraud detection (2 use cases)
Innovation: Topic 3 (Claims AI)
Clients: 3 mid-market insurance companies

Scoring:
Market Fit: 12 (early stage, modest funding)
Scalability: 17 (growth stage + 2 use cases)
Innovation: 20 (Topic 3, AI-focused)
Financial Health: 8 (Series A)
Corporate Experience: 8 (used by 3 insurance companies)
Use Case Breadth: 8 (only 2 use cases)
Geographic Fit: 19 (Switzerland-adjacent regulation concern)
Penalties: 0

Total: 92 points → 57.5 normalized → B+ GRADE
```

### C+ Example: Early-Stage Specialty
```
Company: VisionHealth (India)
Funding: Seed ($800K raised)
Stage: Validating
Use Cases: Medical imaging AI (1 use case)
Innovation: Topic 6 (Health)
Clients: None yet

Scoring:
Market Fit: 4 (seed stage, minimal funding)
Scalability: 2 (early stage)
Innovation: 12 (Topic 6, specialty)
Financial Health: 2 (Seed)
Corporate Experience: 0 (no enterprise clients)
Use Case Breadth: 3 (single use case)
Geographic Fit: 0 (outside EU, data concerns)
Penalties: 5 (prototype/early stage) + 8 (no funding) + 3 (location)

Total: 30 - 16 = 14 points → 8.75 normalized → C+ GRADE
```

## Database Fields Updated

When you run the grading script, it updates:

```python
startup.axa_overall_score = 87.3  # Normalized 0-100 score
startup.axa_priority_tier = "Tier 1: Critical Priority"  # A+/A/A- → Tier 1, etc
startup.axa_fit_summary = "Grade: A | Exceptional: Scalable platform, strong funding..."
```

This maintains backward compatibility while adding the new grade system.

## Validation Checklist

When reviewing grades, use this checklist:

- [ ] **Does A+ startup have Series C+ OR $20M+?** If not, check funding score
- [ ] **Is A/A- startup EU-based?** Check geographic fit component
- [ ] **Is B+ startup enterprise provider?** Check corporate experience
- [ ] **Do B-/C startups have <2 use cases?** Explains lower grade
- [ ] **Is C startup seed-stage or prototype?** Expected for C grade
- [ ] **Is D/F startup outside EU?** Geographic risk + early stage = low grade

---

**Last Updated**: 2024
**Script Location**: `evaluator/recalculate_scores.py`
**Documentation**: `GRADING_SYSTEM.md`
