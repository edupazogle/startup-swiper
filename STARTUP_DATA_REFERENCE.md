# Startup Data Quick Reference

## Overview
The startup database now contains **4,374 startups** from SLUSH 2025, up from 2,556.

## Data Sources
1. **slush2_extracted.json** (original): 2,556 startups
2. **slush_full_list.json** (new import): 1,818 additional startups
3. **slush2.json** (enrichment): Used to enhance data quality

## Key Statistics

### By Country
| Country | Count | % |
|---------|-------|---|
| Finland (FI) | 690 | 15.8% |
| Finland (full name) | 328 | 7.5% |
| Germany (DE) | 270 | 6.2% |
| UK (GB) | 256 | 5.9% |
| Germany (full name) | 197 | 4.5% |
| **Total from top 5** | **1,741** | **39.8%** |

### By Maturity
| Stage | Count | % |
|-------|-------|---|
| Undisclosed | 2,456 | 56.1% |
| Startup | 1,631 | 37.3% |
| Scaleup | 187 | 4.3% |
| Emerging | 69 | 1.6% |
| Validating | 26 | 0.6% |
| Deploying | 4 | 0.1% |
| Pre-seed | 1 | 0.0% |

## Data Fields

### Core Fields (Always Present)
- `id` - Unique identifier (44746+ for new imports)
- `name` - Company name
- `description` - Full description
- `shortDescription` - Truncated to 200 chars
- `website` - Company website URL
- `billingCountry` - Country code or full name
- `billingCity` - City name
- `maturity` - Stage (startup/scaleup/etc)
- `featuredLists` - Array with SLUSH 2025 tag
- `topics` - Tags/categories
- `dateCreated` - Import timestamp
- `dateFounded` - Founding year (YYYY-01-01)

### Extended Fields (When Available)
- `linkedin` - LinkedIn company page
- `primary_industry` - Main industry
- `secondary_industry` - Secondary industry
- `focus_industries` - Array of focus areas
- `business_types` - Business model types
- `prominent_investors` - Notable investors
- `profile_link` - External profile URL
- `employees` - Employee count/range
- `totalFunding` - Total funding raised
- `currentInvestmentStage` - Investment stage
- `logoUrl` - Logo image URL
- `tech` - Technology tags

### Empty/Null Fields (Available for Future Use)
- `legalEntity`, `mainContactId`, `technologyReadiness`
- `lastFundingDate`, `lastFunding`, `pricingModel`
- `opportunities`, `leadOpportunities`, `files`
- `qualityChecks`, `lastQualityCheckDate`

## Usage Examples

### Loading Data in Frontend
```typescript
import allStartups from '../../startups/slush2_extracted.json'

// Filter by country
const finnishStartups = allStartups.filter(s => 
  s.billingCountry === 'FI' || s.billingCountry === 'Finland'
)

// Filter by maturity
const scaleups = allStartups.filter(s => 
  s.maturity === 'scaleup'
)

// Search by industry
const aiStartups = allStartups.filter(s => 
  s.topics?.some(t => t.toLowerCase().includes('ai'))
)
```

### Loading Data in Python
```python
import json

with open('startups/slush2_extracted.json', 'r') as f:
    startups = json.load(f)

# Filter by ID range (get only new imports)
new_startups = [s for s in startups if s['id'] >= 44746]

# Group by country
from collections import defaultdict
by_country = defaultdict(list)
for s in startups:
    by_country[s['billingCountry']].append(s)
```

## Maintenance

### Update Startup Data
To add new startups or update existing ones:

1. Add/update source file (slush_full_list.json)
2. Run import script: `cd api && python3 import_startups.py`
3. Verify: `cd app/startup-swipe-schedu && npm run verify-import`
4. Restart app: `./launch.sh`

### Check Data Quality
```bash
# Verify data integrity
npm run verify-import

# Check for duplicates
grep -o '"name":"[^"]*"' startups/slush2_extracted.json | sort | uniq -d

# Count by field
python3 -c "
import json
with open('startups/slush2_extracted.json') as f:
    data = json.load(f)
    print('With websites:', len([s for s in data if s['website']]))
    print('With funding info:', len([s for s in data if s['totalFunding']]))
    print('With logo:', len([s for s in data if s['logoUrl']]))
"
```

## API Integration (Future Enhancement)

To move from JSON files to database storage, see the "Next Steps" section in `STARTUP_IMPORT_SUMMARY.md`.

Recommended approach:
1. Add `Startup` model to `api/models.py`
2. Create CRUD operations in `api/crud.py`
3. Add REST endpoints in `api/main.py`
4. Import JSON data into SQLite/PostgreSQL
5. Update frontend to fetch from API instead of JSON file

## Data Quality Notes

- ✅ All 4,374 startups have valid schema
- ⚠️ 2 duplicate company names (different entries, possibly different locations)
- ⚠️ Country names inconsistent (some use codes like "FI", others use "Finland")
- ⚠️ 56% have "Undisclosed" maturity - consider enriching from external sources
- ✅ All startups tagged with SLUSH 2025 featured list

## Support

For issues or questions:
1. Check verification script: `npm run verify-import`
2. Review import logs in terminal output
3. Validate JSON structure: `python3 -m json.tool startups/slush2_extracted.json > /dev/null`
4. See full documentation: `STARTUP_IMPORT_SUMMARY.md`
