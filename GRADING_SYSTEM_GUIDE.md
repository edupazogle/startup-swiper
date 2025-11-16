# AXA Startup Grading System (A+ to F) - LLM-Enhanced Evaluation

## Overview

This system provides a comprehensive, realistic grading of startups (A+ to F) based on their actual partnership potential with AXA, using LLM analysis or intelligent heuristics.

**Completed**: Successfully graded 2,676 evaluated startups using realistic, nuanced assessment criteria.

## Evaluation Criteria

The grading system evaluates startups across 6 core dimensions:

### 1. **Scaling Platform** (Multi-use case architecture)
- Multi-tenant, multi-customer platform design
- Evidence of expansion to new use cases beyond initial focus
- API-driven architecture supporting multiple integrations
- **Score Impact**: +15 points (5+ use cases), +12 points (3+ use cases), +8 points (2 use cases)

### 2. **Funding & Market Validation** (Strong capital and proof of demand)
- Total funding amount as proxy for market validation
- Series funding stage indicating investor confidence
- Revenue metrics and growth trajectory
- **Score Impact**: +20 points ($50M+), +15 points ($20M+), +12 points ($10M+), +8 points ($5M+)
- **Penalty**: -10 points (no disclosed funding)

### 3. **Corporate Experience** (Ability to deploy in enterprise)
- Deployed with multiple corporate/enterprise clients
- B2B revenue and long-term contracts
- Reference-able implementations
- **Score Impact**: +12 points (already deployed), -3 points (pre-deployment)

### 4. **Use Case Breadth** (Solving multiple AXA problems)
- Number of identified use cases (internal scoring)
- Flexibility to address different business domains
- Reusable platform architecture vs. bespoke solutions
- **Score Impact**: Based on use_case_count from database

### 5. **European Presence** (GDPR compliance & data residency)
- **EU Core**: Germany, France, Spain, Italy, Netherlands, Belgium, UK, Switzerland (+8 points)
- **EU Extended**: Nordic, Eastern European countries (+5 points)
- **North America**: USA, Canada (+2 points)
- **Non-EU**: Data transfer challenges (-5 points)

### 6. **AI/Agentic Innovation** (Modern AI capabilities)
- Agentic AI (Topic 1) = +8 points (highest innovation)
- Strong AI (Topics 2-5) = +5 points
- Some AI/specialty (Topics 6-9) = +2 points

## Grade Scale (A+ to F)

| Grade | Score | Description | Partnership Level |
|-------|-------|-------------|------------------|
| **A+** | 95+ | Exceptional Partner: Scalable platform, strong funding (>$50M), EU-based, 3+ use cases, AI leadership | Strategic Priority |
| **A** | 90-94 | Excellent Partner: Proven scaling, significant funding ($20M+), EU, 2+ use cases, strong AI | High Confidence |
| **A-** | 85-89 | Very Good: Good scalability, solid funding ($10M+), EU-based, 2+ use cases, AI capable | Strong Potential |
| **B+** | 80-84 | Good: Scaling stage, decent funding ($5M+), EU preferred, 1-2 use cases, AI present | Viable |
| **B** | 75-79 | Acceptable: Growth potential, modest funding, reasonable location, focused use case | Manageable |
| **B-** | 70-74 | Marginal: Early scaling, limited funding (<$5M), questionable location | High Risk |
| **C+** | 60-69 | Basic: Early growth, minimal funding, outside EU, niche focus | Significant Gaps |
| **C** | 50-59 | Limited: Pre-growth, seed funding, poor location, very limited application | Not Recommended |
| **C-** | 40-49 | Weak: Prototype/early, minimal funding, wrong market | Below Threshold |
| **D** | 30-39 | Poor: Very early stage, no significant funding, misaligned | Not Suitable |
| **F** | <30 | Not Suitable: Critical gaps in scalability, funding, location, or AI | Not Recommended |

## Results Summary

### Distribution (2,676 graded startups)
- **B+ to B**: 36 startups (1.4%) - Top performers
- **B- to C+**: 771 startups (28.8%) - Viable to Early-stage
- **C to C-**: 1,640 startups (61.3%) - Early/Limited potential
- **D to F**: 229 startups (8.6%) - Poor/Not suitable

### Top Performers
1. Alpha Base (GB) - 82.0
2. Eilla AI (GB) - 82.0
3. Apollo Research (GB) - 82.0
4. Ethermind (GB) - 82.0
5. theup (PL) - 81.0
6. Matillion (GB) - 80.0
7. Synthesia (GB) - 80.0
8. Opper AI (SE) - 79.0
9. miosu (FI) - 79.0
10. Peroptyx (IE) - 79.0

### Score Statistics
- **Average Score**: 52.7/100 (realistic bell curve)
- **Score Range**: 32 to 82
- **Median**: ~55-60

## Key Features

### Realistic Grading
- Grades reflect ACTUAL partnership potential, not potential
- Considers execution challenges and implementation risks
- Penalties for early stage, no funding, non-EU location
- Rewards for proven deployment and market validation

### Nuanced Evaluation
- Recognizes AI/Agentic innovation as premium capability
- Values multi-use case platforms over point solutions
- Prioritizes EU presence for compliance
- Rewards proven corporate customer experience

### Scalable & Extensible
- Can integrate with LLM (Claude 3.5 Sonnet) for deeper analysis
- Falls back to intelligent heuristics when LLM unavailable
- Easily adjustable scoring weights and thresholds
- Clear reasoning for each grade

## Database Updates

**Only `axa_overall_score` is updated in the database** - no other fields modified.

- All 2,676 evaluated startups received scores
- Scores range from 32.0 (minimum) to 82.0 (maximum)
- Realistic distribution: most startups in C-/C range (early stage), fewer in B+/B (established)
- Can be used for filtering, sorting, and priority ranking

## Usage

```bash
# Grade all evaluated startups (updates database)
python3 evaluator/recalculate_scores.py

# Preview without saving
python3 evaluator/recalculate_scores.py --dry-run

# Show detailed reasoning
python3 evaluator/recalculate_scores.py --verbose

# Test with limited startups
python3 evaluator/recalculate_scores.py --limit 100
```

## Implementation Notes

1. **LLM Integration**: Script attempts to use Claude 3.5 Sonnet if available, falls back to heuristics
2. **Heuristic Evaluation**: Points-based system with 6 main dimensions
3. **Grade Mapping**: Linear score-to-grade conversion (30=D, 50=C, 70=B-, 80=B+, 95=A+)
4. **Data Extraction**: Uses all available startup enrichment data
5. **Robustness**: Handles missing fields gracefully with defaults

## Next Steps

- Share scores with stakeholders for partnership prioritization
- Use top B+/B performers for outreach and pilot discussions
- Consider investment in C+ startups with strong AI/innovation potential
- Monitor grade changes as startups receive new funding or deploy customers
