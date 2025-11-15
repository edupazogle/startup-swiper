# Startup Data Loading - Technical Documentation

## Overview

The application loads **2,556 unique startups** from the Slush 2025 event. All startups are now consolidated in a single file (`startups/slush2_extracted.json`) with consistent structure.

## Data Sources

### Single Consolidated File: `startups/slush2_extracted.json`
- **Count:** 2,556 startups
- **Structure:** Unified format with all available fields
- **Source:** Merged from two original sources:
  - First 100 startups: Enhanced with topics, tech, maturity scores
  - Remaining 2,456: Migrated from slush2.json with consistent structure

### Original Source Files (for reference)
- `startups/slush2.json` - Original 2,520 startups
- These were merged into slush2_extracted.json using the merge script

## Data Structure

Each startup in `slush2_extracted.json` follows this structure:
```typescript
## Data Structure

Each startup in `slush2_extracted.json` follows this structure:

```json
{
  "id": number,
  "name": string,
  "shortDescription": string,
  "description": string,
  "website": string,
  "topics": string[],
  "tech": string[],
  "maturity": string,
  "maturity_score": number,
  "logoUrl": string | null,
  "billingCity": string,
  "billingCountry": string,
  "employees": string,
  "totalFunding": string,
  "currentInvestmentStage": string,
  "dateFounded": string,
  "files": array,
  "featuredLists": array,
  // ... additional metadata fields
}
```

## Merging Process

The startup data was consolidated using the `merge-startups.js` script:

1. **Load both source files**
   - slush2_extracted.json (100 enhanced startups)
   - slush2.json (2,520 total startups)

2. **Identify missing startups**
   - Compare IDs to find startups in slush2.json not in slush2_extracted.json
   - Result: 2,456 unique startups to merge

3. **Map to consistent structure**
   - Apply the slush2_extracted.json format to all startups
   - Extract logo URLs from files array when needed
   - Provide sensible defaults for missing fields

4. **Combine without duplicates**
   - Keep original 100 enhanced startups first
   - Append 2,456 newly mapped startups
   - Total: 2,556 unique startups

### Running the Merge

```bash
npm run merge-startups
```

This script will:
- Preserve existing entries in slush2_extracted.json
- Add missing startups from slush2.json
- Use the extracted file's parameter structure
- Verify no duplicate IDs exist

## Loading Strategy

The application now uses a simplified loading approach:

```typescript
import allStartups from '../../startups/slush2_extracted.json'

console.log(`🚀 Loading all startups from Slush 2025:`)
console.log(`  ✅ Total startups: ${allStartups.length}`)

export const initialStartups: Omit<Startup, 'id'>[] = allStartups.map(...)
```

- **Single source file:** slush2_extracted.json
- **Total startups:** 2,556 unique entries
- **No runtime deduplication needed** - already handled during merge

### Field Mapping

The application maps JSON data to the `Startup` interface with intelligent fallbacks:

```typescript
{
  name: startup.name || '',
  shortDescription: startup.shortDescription || startup.description?.substring(0, 200) || '',
  description: startup.description || startup.shortDescription || '',
  logoUrl: extractLogoUrl(startup), // Extracts from files array if needed
  website: startup.website || undefined,
  topics: startup.topics || [],
  tech: startup.tech || [],
  maturity: startup.maturity || 'Undisclosed',
  // ... additional fields
}
```

### Logo Extraction

The `extractLogoUrl` helper function provides intelligent logo URL extraction:

```typescript
const extractLogoUrl = (startup: any): string | undefined => {
  if (startup.logoUrl) return startup.logoUrl
  if (startup.files && Array.isArray(startup.files)) {
    const logoFile = startup.files.find((f: any) => f.type === 'Logo')
    if (logoFile?.url) return logoFile.url
  }
  return undefined
}
```

## Data Quality

### Field Coverage Across All Startups
- **name:** 100% (2,556/2,556)
- **description or shortDescription:** ~99% 
- **topics:** First 100 have 100% coverage, rest have limited coverage
- **tech:** First 100 have 100% coverage, rest have limited coverage
- **maturity:** First 100 have 100% coverage, rest default to "Undisclosed"
- **logoUrl:** ~3% (extracted from files array where available)

### Enhanced Startups (First 100)
These startups have complete metadata:
- **name:** 100% (100/100)
- **shortDescription:** 100% (100/100)
- **description:** 99% (99/100)
- **topics:** 100% (100/100)
- **tech:** 100% (100/100)
- **maturity:** 100% (100/100)
- **logoUrl:** 61% (61/100)

## User Interface Display

### Dashboard View
Shows a banner with total startup count:
```
┌─────────────────────────────────────────┐
│ 🚀 Total Startups Available             │
│    All startups from Slush 2025         │
│                               2,556     │
└─────────────────────────────────────────┘
```

### Swipe View
Progress indicator shows:
- Current position (e.g., "150 of 2,556")
- Remaining count (e.g., "2,406 remaining")
- Progress bar visualization

## Filtering & Organization

The application provides multiple filtering dimensions:

1. **Topics** - Categorized topics from the startup domain
2. **Technology** - Tech stack used by the startup
3. **Maturity** - Development stage (1-Emerging, 2-Growth, etc.)
4. **Location** - City and country
5. **Funding Stage** - Investment stage

## Implementation Files

- **Consolidated Data:** `startups/slush2_extracted.json` (2,556 startups)
- **Data Loading:** `src/lib/initialStartups.ts`
- **Type Definitions:** `src/lib/types.ts`
- **Dashboard Display:** `src/components/DashboardView.tsx`
- **Swipe Interface:** `src/components/SwipeView.tsx`
- **Merge Script:** `merge-startups.js`
- **Verification Script:** `verify-startups.js`
- **Test Script:** `test-enhancement.js`

## Available Scripts

```bash
# Merge missing startups from slush2.json to slush2_extracted.json
npm run merge-startups

# Verify startup data and show statistics
npm run verify-startups

# Run comprehensive enhancement tests
npm run test-enhancement
```

## Console Output

When the application starts, you'll see:

```
🚀 Loading all startups from Slush 2025:
  ✅ Total startups: 2556
```

## Architecture Benefits

The consolidated approach provides several advantages:

1. **Simpler Code** - Single import, no runtime deduplication
2. **Faster Loading** - One file to parse instead of two
3. **Consistent Structure** - All startups follow the same schema
4. **Easier Maintenance** - Single source of truth
5. **Better Performance** - Reduced memory usage and processing time

## Future Enhancements

Potential improvements:
1. Add more enhanced data to slush2.json startups
2. Implement lazy loading for better performance
3. Add search functionality across all fields
4. Enable custom sorting options
5. Add export functionality for filtered results
