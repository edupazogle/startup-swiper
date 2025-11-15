# AXA Startup Filter Results

## Summary

The `api/filter_axa_startups.py` script filters the **3,664 SLUSH 2025 startups** based on AXA's strategic criteria.

### Key Findings

| Metric | Count | Percentage |
|--------|-------|-----------|
| **All Startups** | 3,664 | 100% |
| **Score >= 40** (Default) | **707** | **19.3%** |
| **Score >= 60** (High Priority) | **75** | **2.0%** |

## Tier Breakdown (Score >= 40)

| Tier | Count | Criteria |
|------|-------|----------|
| **Tier 1: Must Meet** | 3 | Score >= 80 |
| **Tier 2: High Priority** | 72 | Score 60-79 |
| **Tier 3: Medium Priority** | 632 | Score 40-59 |

## Rule Matches (Score >= 40)

The script evaluates startups against 5 AXA-specific rules:

| Rule | Count | Description |
|------|-------|-------------|
| **Rule 1: Platform Enablers** | 548 | Agentic platform infrastructure (observability, MLOps, agent frameworks) |
| **Rule 4: Health Innovations** | 166 | Healthcare solutions applicable to insurance |
| **Rule 3: Insurance Solutions** | 70 | Direct insurance/claims/underwriting solutions |
| **Rule 2: Service Providers** | 52 | Agentic enterprise solutions (non-insurance) |
| **Rule 5: Dev & Legacy** | 27 | Development tooling and legacy modernization |

## Top 10 Highest Scoring Startups

1. **Earthian AI** (Score: 88) - Rule 1, Rule 3
2. **co.brick** (Score: 82) - Rule 1, Rule 2
3. **anyconcept** (Score: 82) - Rule 2, Rule 5
4. **Leida** (Score: 79) - Rule 1, Rule 4
5. **Salute360** (Score: 78) - Rule 1, Rule 4
6. **Possibia AS** (Score: 77) - Rule 1, Rule 4
7. **Aadrila Technologies Private Limited** (Score: 77) - Rule 1, Rule 3
8. **Datawhisper LTD** (Score: 77) - Rule 1, Rule 2
9. **RAE.** (Score: 76) - Rule 1, Rule 3
10. **Solace Care** (Score: 76) - Rule 1, Rule 3

## Filtering Criteria

The script scores startups on:

- **Rule Matching** (base 30-40 points per rule)
- **Traction** (0-25 points): Fortune 500 customers, enterprise size
- **Innovation** (0-15 points): AI, ML, automation keywords
- **Stage** (0-10 points): Scaleup > Startup > Emerging
- **Geography** (0-5 points): EU > US > Other
- **Data Quality** (0-5 points): Enrichment status, website, description

## Files Generated

```bash
# Default filter (score >= 40)
downloads/axa_filtered_test.json       # 707 startups

# High priority filter (score >= 60)
downloads/axa_high_priority_test.json  # 75 startups
```

## Usage Examples

```bash
# Default: score >= 40
python3 api/filter_axa_startups.py --input docs/architecture/ddbb/slush_full_list.json --output downloads/axa_filtered.json --stats

# High priority: score >= 60
python3 api/filter_axa_startups.py --input docs/architecture/ddbb/slush_full_list.json --output downloads/axa_high.json --min-score 60 --stats

# Split by tier
python3 api/filter_axa_startups.py --input docs/architecture/ddbb/slush_full_list.json --split-by-tier --output-dir downloads/axa_tiers/

# With CSV export
python3 api/filter_axa_startups.py --input docs/architecture/ddbb/slush_full_list.json --output downloads/axa_filtered.json --csv --stats
```

## Bug Fixes Applied

The script had field name mismatches. Fixed references from:
- `s['description']` → `s['company_description']`
- `s['name']` → `s['company_name']`
- `s['billingCountry']` → `s['company_country']`

All fixes maintain backward compatibility with fallback handling.
