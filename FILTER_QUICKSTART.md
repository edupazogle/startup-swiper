# AXA Filter Scripts - Quick Start Guide

## Files

### Original Filter
```
api/filter_axa_startups.py
```
- Fixed version with field mapping corrections
- Keyword-based rule matching
- **Output**: 707 startups (score >= 40)

### Enhanced Filter ⭐ RECOMMENDED
```
api/filter_axa_startups_enhanced.py
```
- Funding and company size prioritization
- MCP/NVIDIA NIM integration ready
- **Output**: 18 startups (score >= 60) or 124 startups (score >= 35)

## Quick Run Commands

### Tier 1 & 2 Only (Highest Priority)
```bash
python3 api/filter_axa_startups_enhanced.py \
  --input docs/architecture/ddbb/slush_full_list.json \
  --output downloads/axa_tier12.json \
  --min-score 60 \
  --stats
```
**Result**: 18 startups (3 Tier 1, 15 Tier 2)

### All Qualified Startups
```bash
python3 api/filter_axa_startups_enhanced.py \
  --input docs/architecture/ddbb/slush_full_list.json \
  --output downloads/axa_all.json \
  --min-score 35 \
  --stats
```
**Result**: 124 startups (all funding tiers)

### With CSV Export
```bash
python3 api/filter_axa_startups_enhanced.py \
  --input docs/architecture/ddbb/slush_full_list.json \
  --output downloads/axa_results.json \
  --min-score 50 \
  --csv \
  --stats
```

### Split by Tier
```bash
python3 api/filter_axa_startups_enhanced.py \
  --input docs/architecture/ddbb/slush_full_list.json \
  --split-by-tier \
  --output-dir downloads/axa_tiers/ \
  --min-score 35 \
  --stats
```

### With NVIDIA NIM Analysis (when NVIDIA_API_KEY set)
```bash
export NVIDIA_API_KEY="your_key"
python3 api/filter_axa_startups_enhanced.py \
  --input docs/architecture/ddbb/slush_full_list.json \
  --output downloads/axa_nim_enhanced.json \
  --min-score 50 \
  --include-llm-analysis \
  --stats
```

## Output Files

### Generated Files
```
downloads/axa_enhanced_results.json       # 14 startups (score >= 50)
downloads/axa_enhanced_all.json           # 124 startups (score >= 35)
downloads/axa_enhanced_all.csv            # CSV for spreadsheet use
```

## Scoring Breakdown

```
Rule Score (0-35 points)      Keyword matching against 5 AXA rules
Multi-Rule Bonus (+10)         If matches 2+ rules
Funding Score (0-40 points)    Amount of capital raised ⭐ NEW
Size Score (0-30 points)       Number of employees ⭐ NEW
Maturity Score (0-10 points)   Company stage
─────────────────────────────
TOTAL: 0-100 (normalized)
```

## Key Results

### Top Startups (Score >= 60)
| Rank | Company | Score | Funding | Employees | Rules |
|---|---|---|---|---|---|
| 1 | ICEYE | 80 | $864M | 500 | Satellite data + Insurance |
| 2 | Matillion | 72 | $307M | 500 | Data integration platform |
| 3 | M-Files | 64 | $146M | 500 | AI document management |

### Summary Statistics (Score >= 35)
- **Total**: 124 startups (3.4% of 3,664)
- **Funded**: 99 (79.8%)
- **Average Funding**: $44.6M
- **10+ Employees**: 58 (46.8%)
- **50+ Employees**: 9 (7.3%)

## Rule Distribution

| Rule | Count | Type |
|---|---|---|
| Rule 1: Platform Enablers | 108 | AI/MLOps infrastructure |
| Rule 4: Health Innovations | 38 | Healthcare solutions |
| Rule 3: Insurance Solutions | 19 | Direct insurance products |
| Rule 2: Service Providers | 9 | Enterprise automation |
| Rule 5: Dev & Legacy | 7 | Code tools & modernization |

## Tier Assignments

```
Tier 1: Must Meet (3)        Score >= 80 OR (Funding >= $100M AND 2+ Rules)
  └─ ICEYE, Matillion, M-Files
  
Tier 2: High Priority (15)   Score 60-79 OR (Funding >= $50M OR (Funding >= $10M AND 2+ Rules))
  └─ Yazen, Qare, Prewave, varmo, Gamma Meon, Hyphorest, Superscript, ...
  
Tier 3: Medium Priority (52) Score 40-59
  
Tier 4: Low Priority (54)    Score 20-39
```

## Command Reference

```bash
# Show help
python3 api/filter_axa_startups_enhanced.py --help

# Basic filtering
--min-score 50              # Default: 50 (Tier 2+)
--min-score 60              # Tier 1+2 only
--min-score 35              # All qualified

# Output options
--output FILE.json          # Single JSON file
--output-dir DIR/           # Split by tier into separate files
--csv                       # Also generate CSV file
--stats                     # Show statistics

# Advanced
--include-llm-analysis      # Use NVIDIA NIM (requires API key)
--local-only                # Skip MCP/LLM, use local scoring only

# Filtering
--rule N                    # Only Rule N matches (1-5)
```

## Integration with MCP Server

The enhanced filter is designed to work with:
- `api/mcp_startup_server.py` - Provides database query tools
- `api/mcp_client.py` - Client interface
- `api/ai_concierge.py` - LLM-powered startup analysis

Future enhancement:
```bash
# Query with MCP for enriched data
python3 api/filter_axa_startups_enhanced.py \
  --use-mcp \
  --output downloads/axa_enriched.json
```

## Documentation Files

- **ENHANCED_FILTER_GUIDE.md** - Detailed feature documentation
- **FILTER_COMPARISON.md** - Original vs Enhanced comparison
- **AXA_FILTER_RESULTS.md** - Original filter results summary

## Next Steps

1. **Review Top 3** (Tier 1) with AXA leadership
2. **Validate Tier 2** (15 startups) for fit
3. **Plan Outreach** using funded/sized startups
4. **Enable MCP** to get enriched company data
5. **Deploy NIM** when NVIDIA API key is available

## Troubleshooting

### Script fails with "NVIDIA_API_KEY not set"
✅ **Normal** - This is optional; script works without it

### No results returned
- Check min-score threshold (try `--min-score 35`)
- Verify input file exists (`docs/architecture/ddbb/slush_full_list.json`)
- Run with `--stats` to see filtering breakdown

### CSV not generated
- Add `--csv` flag to command
- CSV file will be named based on output filename

### Want original filter results
```bash
python3 api/filter_axa_startups.py \
  --input docs/architecture/ddbb/slush_full_list.json \
  --output downloads/axa_original.json \
  --min-score 40 \
  --stats
```

## Key Metrics Explained

### Funding Score
- Metric: Total funding raised (in millions)
- Importance: Well-funded companies have staying power
- Tier Impact: $100M+ triggers Tier 1 classification

### Size Score  
- Metric: Number of full-time employees
- Importance: Larger teams = more professional organization
- Tier Impact: 50+ employees indicates enterprise readiness

### Rule Matches
- 5 strategic rules evaluated
- Matching 2+ rules = "multi-rule bonus" (+10 points)
- Better fit = higher quality match

## Support

For questions about:
- **Script Usage**: See command examples above
- **Scoring Logic**: Read ENHANCED_FILTER_GUIDE.md
- **Results Analysis**: See FILTER_COMPARISON.md
- **Rule Definitions**: Check rule_keywords in filter script

---

**Updated**: November 15, 2025
**Status**: Ready for production use
**Recommended**: Use Enhanced Filter with score >= 60 for immediate outreach
