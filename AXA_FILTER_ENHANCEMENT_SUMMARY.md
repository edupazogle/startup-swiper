# AXA Provider Filter - Enhancement Summary ✅

## What Was Enhanced

The `filter_axa_startups_enhanced.py` script was enhanced to better identify startups that can realistically be used as **providers/vendors** for AXA, rather than just companies matching AXA's industry interests.

### New Filtering Criteria Added

#### 1. **Business Model Validation**
```python
AXA_PROVIDER_EXCLUSIONS['business_model'] = [
    'b2c', 'consumer', 'retail', 'marketplace', 'peer-to-peer'
]
```
- Filters out B2C companies (AXA needs B2B/enterprise vendors)
- Excludes consumer-focused platforms
- Removes marketplace models that don't provide services to AXA

#### 2. **Industry Suitability**
```python
AXA_PROVIDER_EXCLUSIONS['industries_excluded'] = [
    'gaming', 'entertainment', 'food', 'hospitality', 'dating',
    'luxury', 'fashion', 'beauty', 'wellness'
]
```
- Excludes sectors that don't have operational relevance to insurance
- Removes consumer-oriented industries

#### 3. **Geographic Scope**
```python
AXA_PROVIDER_EXCLUSIONS['geographic_focus'] = [
    'asia only', 'china only', 'southeast asia only'
]
```
- Filters out companies with limited geographic reach
- AXA prefers global or EU/NA coverage providers

#### 4. **Company Viability**
```python
AXA_PROVIDER_EXCLUSIONS['keywords_excluded'] = [
    'early stage only', 'seed only', 'pre-revenue', 'vc-dependent'
]
```
- Checks minimum team size (>5 people for early stage)
- Verifies funding presence
- Identifies pre-revenue startups as risky providers

### New Functions Added

#### `can_be_axa_provider(startup: Dict) -> Tuple[bool, str]`
- Validates if a startup can be a viable provider/vendor for AXA
- Returns (is_viable, exclusion_reason)
- Checks:
  - Business model alignment
  - Industry suitability
  - Geographic reach
  - Company maturity/viability

#### Updated `should_exclude(startup: Dict) -> bool`
- Now calls `can_be_axa_provider()` in addition to standard exclusions
- Provides detailed exclusion reasons

#### Updated `calculate_axa_score_enhanced()`
- Captures exclusion reasons in scoring response
- Helps understand why startups were filtered

## Results

### Before Enhancement
- Would have included any company matching AXA's 5 strategic rules
- No validation that companies could actually serve as providers
- Potential false positives (e.g., B2C companies in AI space)

### After Enhancement
- **8 qualified provider candidates** (filtered from 3,664 startups, 0.2%)
- All have:
  - B2B/enterprise business models
  - Relevant industries (AI, insurance, logistics, data)
  - Adequate funding ($4M - $864M)
  - Established teams (5-500+ employees)

### Top Tier 1 Candidates (Must Meet)

1. **ICEYE** (Finland)
   - Score: 80/100
   - Funding: $864M
   - Team: 500 employees
   - Rules: Platform Enablers + Insurance Solutions
   - Business: Satellite-based monitoring for insurance & defense

2. **Matillion** (UK)
   - Score: 72/100  
   - Funding: $307M
   - Team: 500 employees
   - Rules: Platform Enablers
   - Business: Cloud-native data integration platform

### Tier 2 Candidates (High Priority)

3. **M-Files** (Finland)
   - Score: 64/100
   - Funding: $146M
   - Business: Knowledge work automation platform

4. **Prewave** (Austria)
   - Score: 55/100
   - Funding: $37M
   - Business: Supply chain management & resilience

## Filtering Breakdown

From 3,664 startups:
- **3,172** excluded by keywords (business model/industry)
- **479** excluded by score threshold
- **5** excluded for not matching any rules
- **8** qualified as potential AXA providers

## Key Improvements

✅ **Better Provider Fit**: Only B2B/enterprise vendors considered
✅ **Geographic Validation**: Ensures global or major market coverage  
✅ **Viability Checks**: Confirms companies have team + funding
✅ **Detailed Reasoning**: Each exclusion has a reason (tracked in output)
✅ **Reduced False Positives**: Fewer companies that look good but can't actually provide services

## Usage

```bash
# Run enhanced filter with provider criteria
python3 api/filter_axa_startups_enhanced.py --min-score 50 --stats --output downloads/axa_enhanced_filtered.json

# Show results
ls -lh downloads/axa_enhanced_filtered.json
```

## Output

File: `downloads/axa_enhanced_filtered.json`
- 8 qualified AXA provider candidates
- Full scoring breakdown for each
- Business details and website
- Rule matching information
- Funding and team size data

## Next Steps

1. **Contact Tier 1 candidates** (ICEYE, Matillion) first
2. **Verify Tier 2 candidates** can support AXA's use cases
3. **Evaluate integration requirements** with AXA systems
4. **Run pilots** with top 2-3 candidates
5. **Expand to Tier 3** if high-priority options show promise
