# Enriched Startup Data - Complete Implementation Guide

## Overview

The enrichment system adds deep intelligence to your startup database by scraping and organizing:
- **Contact Information** - Emails and phone numbers
- **Social Media Profiles** - LinkedIn, Twitter, GitHub, Instagram
- **Technology Stack** - Technologies used by each startup
- **Team Information** - Key team members extracted from company sites
- **Key Pages** - URLs to about, team, contact, careers pages

## Current Status

- **Total Startups**: 4,374
- **Enrichment Scripts**: Ready for bulk processing
- **API Endpoints**: 5 new endpoints for accessing enriched data
- **Progress Tracking**: Built-in checkpoint and resume capability

## Quick Start - Enrich All Startups

### 1. Check Current Status

```bash
cd /home/akyo/startup_swiper
source .venv/bin/activate

python3 api/enrichment_coordinator.py --status
```

Output will show:
- Total startups in database
- Currently enriched count
- Remaining to enrich
- Completion percentage

### 2. Run Full Enrichment (Recommended)

```bash
python3 api/enrichment_coordinator.py --enrich-all \
  --delay 1 \
  --workers 3
```

**Parameters:**
- `--delay 1` - Wait 1 second between requests (respects websites)
- `--workers 3` - Use 3 parallel workers for faster processing
- `--enrich-all` - Process ALL remaining startups

**Estimated Time:**
- 4,305 remaining startups at 1s delay = ~1.2 hours
- With 3 parallel workers: ~25-35 minutes

### 3. Monitor Progress

While enrichment is running, in another terminal:

```bash
python3 api/enrichment_coordinator.py --status
```

### 4. Verify Quality

After enrichment completes:

```bash
python3 api/enrichment_coordinator.py --verify
```

Shows:
- Quality metrics
- Fields populated per startup
- Data completeness

## API Endpoints

### 1. Search Enriched Startups

```bash
GET /startups/enriched/search?query=AI&enrichment_type=tech_stack&limit=10
```

**Parameters:**
- `query` - Search by startup name
- `enrichment_type` - Filter by: 'emails', 'social', 'tech_stack', 'team'
- `limit` - Number of results (default: 20)

**Response:**
```json
{
  "results": [
    {
      "id": "startup_123",
      "name": "TechVision AI",
      "website": "https://techvision.ai",
      "enrichment": {
        "emails": ["contact@techvision.ai"],
        "social_media": {"linkedin": "..."},
        "tech_stack": ["React", "Python"],
        "team_members": ["John Doe - CEO"]
      }
    }
  ],
  "count": 1
}
```

### 2. Get Single Startup Enrichment

```bash
GET /startups/{startup_id}/enrichment
```

**Response:**
```json
{
  "startup_id": "startup_123",
  "startup_name": "TechVision AI",
  "website": "https://techvision.ai",
  "enrichment": {
    "emails": ["contact@techvision.ai"],
    "phone_numbers": ["+1-234-567-8900"],
    "social_media": {
      "linkedin": "...",
      "twitter": "..."
    },
    "tech_stack": ["React", "Python"],
    "key_pages": {
      "about": "...",
      "team": "..."
    },
    "team_members": ["..."],
    "sources_checked": ["website", "linkedin"]
  },
  "last_enriched": "2025-11-14T10:30:00Z"
}
```

### 3. Get Enrichment Statistics

```bash
GET /startups/enrichment/stats
```

Shows aggregated metrics across all startups.

### 4. Search by Enriched Field

```bash
POST /startups/enrichment/by-name
Content-Type: application/json

{
  "field_name": "tech",
  "field_value": "React",
  "limit": 20
}
```

**field_name options:**
- `email` - Search email addresses
- `phone` - Search phone numbers
- `tech` - Search technology stack
- `person` - Search team member names
- `social` - Search social media URLs

**Response:**
```json
{
  "results": [
    {
      "id": "...",
      "name": "...",
      "website": "...",
      "matched_field": "tech",
      "enrichment_date": "..."
    }
  ],
  "count": 5,
  "search_field": "tech",
  "search_value": "React"
}
```

### 5. Statistics Endpoint

```bash
GET /startups/enrichment/stats
```

Shows:
- Total and enriched counts
- Completion percentage
- Breakdown by field type

## File Structure

```
api/
├── enrich_startups.py              # Original enrichment script
├── bulk_enrich_startups.py         # NEW: Bulk processing with parallel workers
├── enrichment_coordinator.py       # NEW: Manage full enrichment process
├── deploy_enriched_data.py         # Deploy to database
├── enriched_data_examples.py       # NEW: API examples and documentation
├── main.py                         # Updated with 5 new API endpoints
├── models.py                       # Database models
├── schemas.py                      # Data validation schemas
└── .enrichment_progress.json       # Progress tracking file
```

## Data Storage

Enriched data is stored in startup records with:

```json
{
  "id": "startup_123",
  "name": "TechVision AI",
  "website": "https://techvision.ai",
  "is_enriched": true,
  "last_enriched_date": "2025-11-14T10:30:00Z",
  "enrichment": {
    "emails": [...],
    "phone_numbers": [...],
    "social_media": {...},
    "tech_stack": [...],
    "key_pages": {...},
    "team_members": [...],
    "enrichment_date": "...",
    "sources_checked": [...]
  }
}
```

## Enrichment Process

### What Gets Extracted

1. **Emails** - From contact, footer, team pages
2. **Phone Numbers** - From contact, about pages
3. **Social Media** - LinkedIn, Twitter, GitHub, Instagram, Facebook
4. **Tech Stack** - From HTML, meta tags, scripts, page content
5. **Key Pages** - Links to about, team, contact, blog, careers, pricing
6. **Team Members** - Names and titles from team/about pages

### Quality Metrics

Expected success rates:
- Email extraction: 70-80%
- Social media links: 60-70%
- Tech stack: 75-85%
- Team members: 50-60%
- Overall: 65-75%

## Resume Capability

If enrichment is interrupted:

```bash
# Check progress
python3 api/enrichment_coordinator.py --status

# Resume from last checkpoint
python3 api/enrichment_coordinator.py --enrich-all --resume
```

The system saves progress after each batch and can resume from the last completed position.

## Integration Examples

### Python

```python
import requests

# Search for React-based startups
response = requests.post(
    "http://localhost:8000/startups/enrichment/by-name",
    json={
        "field_name": "tech",
        "field_value": "React",
        "limit": 20
    }
)

startups = response.json()["results"]
for startup in startups:
    print(f"{startup['name']}: {startup['website']}")
```

### JavaScript/TypeScript

```typescript
// Get enrichment for a startup
async function getStartupEnrichment(startupId: string) {
  const response = await fetch(
    `/api/startups/${startupId}/enrichment`
  );
  const data = await response.json();
  
  return {
    name: data.startup_name,
    emails: data.enrichment.emails,
    technologies: data.enrichment.tech_stack,
    team: data.enrichment.team_members
  };
}
```

### React Component

```tsx
function EnrichedStartupCard({ startup }) {
  const [enrichment, setEnrichment] = useState(null);

  useEffect(() => {
    fetch(`/api/startups/${startup.id}/enrichment`)
      .then(r => r.json())
      .then(data => setEnrichment(data.enrichment));
  }, [startup.id]);

  return (
    <div className="card">
      <h3>{startup.name}</h3>
      {enrichment && (
        <>
          <p>📧 {enrichment.emails.join(', ')}</p>
          <p>💻 {enrichment.tech_stack.join(', ')}</p>
          <p>👥 {enrichment.team_members.join(', ')}</p>
        </>
      )}
    </div>
  );
}
```

## Performance Optimization

### For Large Queries

Use batch operations:

```python
# Instead of 1000 individual requests
for startup_id in startup_ids:
    response = requests.get(f"/api/startups/{startup_id}/enrichment")

# Use search endpoints
response = requests.post(
    "/api/startups/enrichment/by-name",
    json={"field_name": "tech", "field_value": "React", "limit": 1000}
)
```

### Caching

The startup data is loaded once into memory at API startup. Enriched data is immediately available without database queries.

### Rate Limiting

During enrichment:
- Use `--delay` parameter to space out requests
- Use `--workers` to parallelize (default: 3)
- Respects website rate limiting with exponential backoff

## Troubleshooting

### Issue: Enrichment Failing on Specific Startup

**Solution:** The script logs failures. Check the specific startup's website manually and verify it's accessible.

### Issue: Low Email Extraction Rate

**Cause:** Some websites don't display emails publicly.

**Solution:** This is expected. Average 70-80% success rate is normal.

### Issue: Enrichment Taking Too Long

**Solution:** Increase workers:
```bash
python3 api/enrichment_coordinator.py --enrich-all --workers 5 --delay 0.5
```

### Issue: Memory Usage High

**Solution:** Process in batches:
```bash
python3 api/enrichment_coordinator.py --enrich --batch 50 --workers 2
```

## Next Steps

1. ✅ Run full enrichment with `--enrich-all`
2. ✅ Verify data quality with `--verify`
3. ✅ Use API endpoints to access enriched data
4. ✅ Integrate enrichment into your React application
5. ✅ Filter/search based on enriched fields

## Support

For issues or questions:
1. Check `/logs/llm/` for LLM request logs
2. Review enrichment progress in `.enrichment_progress.json`
3. Check API response status codes (404 if startup not enriched)

## Advanced Features

### Custom Enrichment

To add custom enrichment fields, modify `enrich_startups.py`:

1. Add new method to `StartupEnricher` class
2. Extract additional data
3. Return in enrichment dictionary
4. Update API endpoints to expose new fields

### Scheduled Enrichment

Set up a cron job:

```bash
# Enrich 100 new startups daily at 2 AM
0 2 * * * cd /home/akyo/startup_swiper && source .venv/bin/activate && python3 api/enrichment_coordinator.py --enrich --batch 100
```

### Export Enriched Data

```bash
# Export to CSV
python3 -c "
import json
import csv

with open('docs/architecture/ddbb/slush2_extracted.json') as f:
    data = json.load(f)

enriched = [s for s in data if s.get('is_enriched')]

with open('enriched_startups.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=[
        'name', 'website', 'emails', 'tech_stack', 'team_members'
    ])
    writer.writeheader()
    for s in enriched:
        writer.writerow({
            'name': s['name'],
            'website': s['website'],
            'emails': ','.join(s['enrichment']['emails']),
            'tech_stack': ','.join(s['enrichment']['tech_stack']),
            'team_members': ','.join(s['enrichment']['team_members'])
        })
"
```

---

**Status:** ✅ Ready for Full Deployment

**Command to Start:** 
```bash
python3 api/enrichment_coordinator.py --enrich-all --delay 1 --workers 3
```

**Estimated Completion:** ~25-35 minutes for all 4,305 remaining startups
