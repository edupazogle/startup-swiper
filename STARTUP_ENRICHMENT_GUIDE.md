# Startup Data Enrichment - Analysis & Implementation Guide

## Current Database Analysis

### Company: 759 Studio (First Entry)
- **ID**: 43732
- **Website**: https://www.759studio.com/
- **Location**: Belgrade, RS
- **Founded**: 2022
- **Completeness**: 44.7% (21/47 fields filled)

### Empty Fields Requiring Enrichment

**Location Details (5 fields)**
- ❌ billing_state
- ❌ billing_street  
- ❌ billing_postal_code

**Funding Information (6 fields)**
- ❌ last_funding_date
- ❌ last_funding
- ❌ original_total_funding
- ❌ original_total_funding_currency
- ❌ funding_is_undisclosed

**Metadata (1 field)**
- ❌ technology_readiness

**Custom Fields from slush_full_list (7 fields)**
- ❌ linkedin
- ❌ primary_industry
- ❌ secondary_industry
- ❌ focus_industries
- ❌ business_types
- ❌ prominent_investors
- ❌ profile_link

## 📊 Enrichment Opportunities

### Priority 1: High-Value Data (Easily Scrapable)

| Field | Source | Method | Value |
|-------|--------|--------|-------|
| **Social Media Links** | Company Website | Scrape footer/header | High |
| LinkedIn URL | Footer links | Extract href | High |
| Twitter URL | Footer links | Extract href | Medium |
| Facebook URL | Footer links | Extract href | Medium |
| **Contact Information** | Contact Page | Parse contact section | High |
| Email addresses | Contact/Footer | Regex extraction | High |
| Phone numbers | Contact page | Regex extraction | Medium |
| **Company Information** | About Page | Text extraction | High |
| Full description | About Us | Scrape <div> content | High |
| Team members | Team page | Extract names | Medium |
| Founders | About/Team page | Extract names | High |
| **Technology Stack** | Website Source | Analyze HTML/JS | Medium |
| Frontend framework | Script tags | Detect React/Vue/Angular | Medium |
| Analytics tools | Script tags | Detect GA/GTM | Low |

### Priority 2: Medium-Value Data (Requires API/Database)

| Field | Source | Method | Complexity |
|-------|--------|--------|------------|
| **Funding Data** | Crunchbase API | API call | High |
| Total funding | Crunchbase | JSON response | High |
| Last funding round | Crunchbase | JSON response | High |
| Investors list | Crunchbase | JSON response | High |
| **Business Intelligence** | LinkedIn Company | Web scraping | High |
| Company size | LinkedIn | Parse employees count | Medium |
| Growth rate | LinkedIn | Historical data | High |
| Job postings | LinkedIn | Count open positions | Medium |
| **Tech Stack** | BuiltWith API | API call | Medium |
| Technologies used | BuiltWith | JSON response | Medium |
| Hosting provider | BuiltWith | JSON response | Low |

### Priority 3: Advanced Data (Requires Multiple Sources)

| Field | Sources | Complexity |
|-------|---------|------------|
| Market segments | Website + LinkedIn | High |
| Target customers | Website content analysis | High |
| Competitive analysis | Multiple databases | Very High |
| Revenue estimates | Public filings + estimates | Very High |
| Growth metrics | Historical snapshots | Very High |

## 🛠️ Implementation

### Phase 1: Basic Web Scraping (Implemented)

**Script**: `api/enrich_startups.py`

**Capabilities**:
- ✅ Extract email addresses from website
- ✅ Extract phone numbers
- ✅ Find social media links (LinkedIn, Twitter, Facebook, etc.)
- ✅ Identify key website pages (About, Team, Contact, etc.)
- ✅ Extract meta descriptions and titles
- ✅ Detect technology stack (React, Vue, Analytics)
- ✅ Scrape About Us content
- ✅ Extract team member names

**Usage**:
```bash
# Test on first company
python3 api/enrich_startups.py --limit 1

# Process first 10 companies
python3 api/enrich_startups.py --limit 10

# Process specific company
python3 api/enrich_startups.py --company "759 Studio"

# Process all (with delay for rate limiting)
python3 api/enrich_startups.py --delay 2
```

### Phase 2: API Integration (To Be Implemented)

**Crunchbase Integration**:
```python
def enrich_from_crunchbase(company_name):
    api_key = os.getenv('CRUNCHBASE_API_KEY')
    url = f"https://api.crunchbase.com/api/v4/entities/organizations/{company_slug}"
    response = requests.get(url, headers={'X-cb-user-key': api_key})
    data = response.json()
    
    return {
        'total_funding': data['properties']['total_funding_usd'],
        'last_funding_type': data['properties']['last_funding_type'],
        'number_of_funding_rounds': data['properties']['num_funding_rounds'],
        'investors': [inv['name'] for inv in data['investors']]
    }
```

**LinkedIn Company Data**:
```python
def enrich_from_linkedin(linkedin_url):
    # Using LinkedIn API or scraping with Selenium
    return {
        'employee_count': company_data['staff Count'],
        'industries': company_data['industries'],
        'specialties': company_data['specialties'],
        'followers': company_data['followersCount']
    }
```

### Phase 3: Advanced Enrichment

**Email Discovery** (Hunter.io):
```python
def find_emails(domain):
    api_key = os.getenv('HUNTER_API_KEY')
    url = f"https://api.hunter.io/v2/domain-search?domain={domain}"
    response = requests.get(url, params={'api_key': api_key})
    return response.json()['data']['emails']
```

**Tech Stack** (BuiltWith):
```python
def get_tech_stack(domain):
    api_key = os.getenv('BUILTWITH_API_KEY')
    url = f"https://api.builtwith.com/v18/api.json?KEY={api_key}&LOOKUP={domain}"
    response = requests.get(url)
    return response.json()['Results'][0]['Technologies']
```

## 📈 Expected Enrichment Results

### Per Company Data Points:

**From Website Scraping (5-15 fields)**:
- 2-5 email addresses
- 1-3 phone numbers  
- 3-7 social media links
- 1 full company description
- 5-10 team member names
- 2-4 key website sections
- 3-5 technology identifications

**From API Integration (10-20 fields)**:
- Funding: 5-7 fields
- LinkedIn: 4-6 fields
- Business info: 3-5 fields
- Contact discovery: 2-4 fields

**Total Potential**: 15-35 new fields per startup

### Database Improvement:
- Current: 44.7% completeness
- After Phase 1: ~60-65% completeness
- After Phase 2: ~75-80% completeness
- After Phase 3: ~85-90% completeness

## 🚀 Quick Start

### 1. Install Dependencies
```bash
cd /home/akyo/startup_swiper
source .venv/bin/activate  # If using venv
pip install beautifulsoup4 lxml requests
```

### 2. Test on First Company
```bash
python3 api/enrich_startups.py --limit 1 --company "759 Studio"
```

### 3. Review Results
```bash
# Check enriched data
cat docs/architecture/ddbb/slush2_enriched.json | head -100
```

### 4. Process All Startups
```bash
# Run with rate limiting (2 seconds between requests)
python3 api/enrich_startups.py --delay 2 --start 0 --limit 100

# Continue from where you left off
python3 api/enrich_startups.py --delay 2 --start 100 --limit 100
```

## 📋 Output Format

### Enriched Startup Structure:
```json
{
  "id": 43732,
  "name": "759 Studio",
  "website": "https://www.759studio.com/",
  ...existing fields...,
  "enrichment": {
    "enrichment_date": "2025-11-14T08:53:34",
    "enrichment_success": true,
    "sources_checked": ["company_website"],
    "emails": ["contact@759studio.com", "info@759studio.com"],
    "phone_numbers": ["+381 11 123 4567"],
    "social_media": {
      "linkedin": "https://linkedin.com/company/759studio",
      "instagram": "https://instagram.com/759studio",
      "facebook": "https://facebook.com/759studio"
    },
    "key_pages": {
      "about": "https://www.759studio.com/about",
      "team": "https://www.759studio.com/team",
      "contact": "https://www.759studio.com/contact",
      "products": "https://www.759studio.com/products"
    },
    "tech_stack": ["React", "Google Analytics"],
    "page_title": "759 Studio - Sustainable Architecture",
    "meta_description": "Provider of sustainable architecture services...",
    "about_text": "759 Studio specializes in...",
    "team_members": ["John Doe", "Jane Smith"]
  }
}
```

## ⚠️ Important Considerations

### Rate Limiting
- **Delay between requests**: 2-5 seconds recommended
- **Respect robots.txt**: Check site permissions
- **Error handling**: Graceful failures, continue processing
- **Progress saving**: Save every 10 companies

### Legal & Ethical
- ✅ Public website data only
- ✅ No authentication bypass
- ✅ Respect robots.txt
- ✅ Rate limiting to avoid overload
- ❌ Don't scrape private/protected data
- ❌ Don't violate terms of service

### Data Quality
- **Validation**: Verify emails, phone formats
- **Deduplication**: Remove duplicate contacts
- **Confidence scores**: Rate data reliability
- **Source attribution**: Track where data came from

## 🔄 Integration with Database

### Update Existing Records:
```python
# Merge enriched data back into main database
def update_database(enriched_file):
    with open('slush2_enriched.json') as f:
        enriched = json.load(f)
    
    with open('slush2_extracted.json') as f:
        original = json.load(f)
    
    # Create ID lookup
    enriched_by_id = {s['id']: s for s in enriched}
    
    # Merge data
    for startup in original:
        if startup['id'] in enriched_by_id:
            enriched_data = enriched_by_id[startup['id']].get('enrichment', {})
            
            # Add new fields
            if enriched_data.get('emails'):
                startup['contact_emails'] = enriched_data['emails']
            if enriched_data.get('social_media', {}).get('linkedin'):
                startup['linkedin'] = enriched_data['social_media']['linkedin']
            # ... etc
    
    # Save updated database
    with open('slush2_extracted.json', 'w') as f:
        json.dump(original, f, indent=2)
```

## 📊 Progress Tracking

Create a tracking file to monitor enrichment:
```json
{
  "total_startups": 4374,
  "processed": 150,
  "successful": 142,
  "failed": 8,
  "last_processed_id": 43882,
  "completion_percentage": 3.4,
  "fields_enriched": {
    "emails": 134,
    "social_media": 128,
    "phone_numbers": 67,
    "team_members": 89
  }
}
```

## 🎯 Success Metrics

- **Enrichment Success Rate**: Target 80%+ websites successfully scraped
- **Data Quality**: 90%+ valid emails/phones
- **Coverage**: 50%+ startups with social media links
- **Completeness**: 75%+ database fields filled
- **Processing Speed**: 100-200 startups per hour

---

**Created**: 2025-11-14
**Script**: `api/enrich_startups.py`
**Documentation**: This file
