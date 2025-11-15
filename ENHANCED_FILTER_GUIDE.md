# Enhanced AXA Startup Filter - Documentation

## Overview

The **enhanced AXA startup filter** (`api/filter_axa_startups_enhanced.py`) improves upon the original filter by:

1. **Prioritizing Funding** - Startups with substantial capital are ranked higher
2. **Prioritizing Company Size** - Larger, more established teams score better
3. **MCP Integration Ready** - Can leverage the existing MCP server for smarter querying
4. **NVIDIA NIM Support** - Optional AI-powered rule assessment with DeepSeek-R1
5. **Better Scoring Algorithm** - Normalized scoring with funding as primary differentiator

## Comparison: Original vs Enhanced

### Original Filter Results (score >= 40)
- **Total startups**: 3,664
- **Filtered**: 707 (19.3%)
- **Tier 1**: 3
- **Tier 2**: 72
- **Tier 3**: 632

**Issue**: Many underfunded or very early-stage startups included, reducing quality of matches

### Enhanced Filter Results (score >= 35)
- **Total startups**: 3,664
- **Filtered**: 124 (3.4%)
- **Tier 1**: 3
- **Tier 2**: 15
- **Tier 3**: 52
- **Tier 4**: 54

**Advantage**: 80% of results are funded, 47% have 10+ employees, 7% have 50+ employees

## Key Improvements

### 1. Funding Score (0-40 points)
Startups with more capital are better positioned to evaluate and adopt AXA's offerings:

| Funding Level | Points | Reasoning |
|---|---|---|
| >= $500M | 40 | Late-stage/mega-funded |
| >= $100M | 35 | Growth-stage |
| >= $50M | 30 | Series B+ |
| >= $20M | 25 | Series A/B |
| >= $10M | 20 | Solid seed/Series A |
| >= $5M | 15 | Early seed |
| >= $1M | 10 | Pre-seed/Seed |
| > $0 | 5 | Minimal funding |
| $0 | 0 | Unfunded |

### 2. Company Size Score (0-30 points)
Larger teams indicate business maturity and ability to handle enterprise relationships:

| Employee Count | Points | Category |
|---|---|---|
| >= 1000 | 30 | Enterprise |
| >= 500 | 28 | Large |
| >= 200 | 26 | Medium-Large |
| >= 100 | 24 | Medium |
| >= 50 | 22 | Small-Medium |
| >= 30 | 20 | Small |
| >= 10 | 12 | Micro |
| > 0 | 5 | Tiny |
| 0 | 0 | Unknown |

### 3. Maturity Score (0-10 points)
Startup vs Scaleup designation provides stage context:

| Stage | Points |
|---|---|
| Scaleup | 10 |
| Startup | 7 |
| Validating/Deploying | 5 |
| Emerging | 3 |
| Unknown | 2 |

## New Scoring Formula

```
Rule Score (0-35)     Base matching against 5 AXA rules
Multi-rule Bonus (+10) If matches 2+ rules
Funding Score (0-40)  Amount of capital raised
Size Score (0-30)     Number of employees
Maturity Score (0-10) Company stage
─────────────────────
Raw Score (0-125)     Sum of all components

Normalized = min(100, Raw Score × 100 / 125)
```

## Tier Assignment Logic

### Tier 1: Must Meet (Score >= 80 OR [Funding >= $100M AND 2+ Rules])
Companies with exceptional fit and resources - **highest priority**

**Top Tier 1 Startups**:
- **ICEYE** ($864M, 500 employees) - Satellite data platform
- **Matillion** ($307M, 500 employees) - Data integration
- **M-Files** ($146M, 500 employees) - AI document management

### Tier 2: High Priority (Score 60-79 OR [Funding >= $50M OR (Funding >= $10M AND 2+ Rules)])
Well-funded companies with proven product-market fit

**Sample Tier 2**:
- Yazen ($29M) - Health analytics
- Qare ($30M) - Telemedicine
- Prewave ($37M) - Supply chain visibility

### Tier 3: Medium Priority (Score 40-59)
Interesting startups with some traction but less funding/size

### Tier 4: Low Priority (Score 20-39)
Early-stage companies matching our criteria but limited resources

## Usage Examples

### Basic Usage (Funded Startups Only)
```bash
python3 api/filter_axa_startups_enhanced.py \
  --input docs/architecture/ddbb/slush_full_list.json \
  --output downloads/axa_tier1_tier2.json \
  --min-score 60 \
  --stats
```

**Output**: 18 startups (Tier 1 + 2)

### All Matched Startups
```bash
python3 api/filter_axa_startups_enhanced.py \
  --input docs/architecture/ddbb/slush_full_list.json \
  --output downloads/axa_all_matched.json \
  --min-score 35 \
  --stats
```

**Output**: 124 startups (Tiers 1-4)

### With CSV Export
```bash
python3 api/filter_axa_startups_enhanced.py \
  --input docs/architecture/ddbb/slush_full_list.json \
  --output downloads/axa_results.json \
  --min-score 50 \
  --csv \
  --stats
```

Generates both JSON and CSV files.

### Split by Tier
```bash
python3 api/filter_axa_startups_enhanced.py \
  --input docs/architecture/ddbb/slush_full_list.json \
  --split-by-tier \
  --output-dir downloads/axa_tiers_enhanced/ \
  --min-score 35 \
  --stats
```

Creates separate files:
- `axa_tier1_enhanced.json`
- `axa_tier2_enhanced.json`
- `axa_tier3_enhanced.json`
- `axa_tier4_enhanced.json`

## MCP Integration (Future)

The script is designed to work with the MCP server for:

1. **Richer Startup Data** - Query enriched startup profiles for better analysis
2. **Company Network** - Understand startup ecosystems
3. **Intelligent Filtering** - Use LLM to assess strategic fit beyond keyword matching
4. **Trend Analysis** - Identify emerging categories and market trends

To enable MCP analysis:
```bash
python3 api/filter_axa_startups_enhanced.py \
  --input docs/architecture/ddbb/slush_full_list.json \
  --output downloads/axa_with_mcp.json \
  --include-llm-analysis \
  --stats
```

## NVIDIA NIM Integration (Optional)

When NVIDIA_API_KEY is configured, the script can use DeepSeek-R1 for:

1. **Semantic Rule Matching** - LLM assessment of whether startup truly fits rules
2. **Confidence Weighting** - LLM provides confidence scores for matches
3. **Nuance Detection** - Identifies false positives in keyword matching

Set up NIM:
```bash
export NVIDIA_API_KEY="your_api_key_from_build.nvidia.com"
python3 api/filter_axa_startups_enhanced.py \
  --include-llm-analysis \
  --output downloads/axa_nim_enhanced.json \
  --stats
```

## Results Interpretation

### Funding Distribution
- **100%** of Tier 1-2 startups are funded (vs ~30% in general population)
- **Average funding**: $223.8M (Tier 1-2) vs $44.6M (all matched)
- **Focus**: Late-stage companies with proven business models

### Company Size Distribution
- **57%** of matched startups have 10+ employees
- **43%** have 50+ employees in Tier 1-2
- **Implication**: Mature operations, not just founders

### Rule Distribution
- **Rule 1** (Platform Enablers): 108 matches - AI/MLOps infrastructure
- **Rule 4** (Health): 38 matches - Insurance-applicable healthcare
- **Rule 3** (Insurance): 19 matches - Direct insurance solutions
- **Rule 2** (Services): 9 matches - Enterprise automation
- **Rule 5** (Dev): 7 matches - Code and legacy modernization

## Data Quality

The enhanced filter ensures:

1. **Funded Startups** - 79.8% have disclosed funding
2. **Mature Teams** - 46.8% have confirmed employee counts
3. **Documented Fit** - 100% match at least one AXA strategic rule
4. **Quality Over Quantity** - 3.4% pass vs 19.3% in original (5.6x more selective)

## Configuration Files

Default input: `docs/architecture/ddbb/slush_full_list.json`
- Contains 3,664 SLUSH 2025 startups
- Includes funding, company type, description, topics
- Pre-enriched with maturity classification

## Next Steps

1. **Validate Tier 1** - Review top 3-18 startups with AXA stakeholders
2. **Request Meetings** - Prioritize by funding × employee count
3. **Run MCP Analysis** - Get enriched data on top 50
4. **Deploy NIM** - Get LLM scoring when NVIDIA key is available
5. **Monitor Results** - Track which startups convert to partnerships

## Testing

Generated files:
- `downloads/axa_enhanced_results.json` - Tier 1-3 (14 startups, score >= 50)
- `downloads/axa_enhanced_all.json` - Tiers 1-4 (124 startups, score >= 35)
- `downloads/axa_enhanced_all.csv` - CSV export for Excel analysis
