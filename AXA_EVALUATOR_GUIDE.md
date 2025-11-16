# AXA Comprehensive Startup Evaluator - User Guide

## Overview

This system uses **NVIDIA NIM (DeepSeek-R1 LLM)** to comprehensively evaluate all startups in your database across **12 strategic categories** relevant to AXA's business needs.

### 🎯 Categories Evaluated

1. **Agentic Platform Enablers** - Infrastructure for building AI agents (LangChain, vector DBs, etc.)
2. **Agentic Solution Providers** - Ready-to-use AI agent applications
3. **Workflow Automation** - Business process automation (RPA, BPA, iPaaS)
4. **Sales Training & Coaching** - AI sales enablement and coaching platforms
5. **Insurance Solutions** - General insurtech (policy admin, claims, underwriting)
6. **Underwriting Triage** - Automated risk assessment and underwriting
7. **Claims Recovery & Subrogation** - Claims automation and fraud detection
8. **Coding Automation** - Developer tools and AI coding assistants
9. **Health & Wellness** - Digital health platforms for employee benefits
10. **AI Evals & Testing** - LLM evaluation and testing frameworks
11. **LLM Observability** - Monitoring and debugging for AI systems
12. **Contact Center Solutions** - AI for customer service and support

## 🚀 Quick Start

### Run Full Evaluation (ALL 238 Startups)

```bash
# Navigate to project root
cd /home/akyo/startup_swiper

# Run evaluation (takes ~15-30 minutes)
./run_axa_evaluation.sh
```

### Resume from Checkpoint

If evaluation is interrupted, resume where you left off:

```bash
./run_axa_evaluation.sh --resume
```

### Test with Limited Startups

Test on a smaller set first:

```bash
cd /home/akyo/startup_swiper
source .venv/bin/activate
python3 api/axa_comprehensive_evaluator_fast.py --max-startups 10
```

## 📊 Output Files

After evaluation completes, you'll get:

1. **`downloads/axa_evaluation_results.json`** - Full detailed results
   - Every startup with all category evaluations
   - Confidence scores and reasoning
   - Priority tiers

2. **`downloads/axa_evaluation_results_analysis.json`** - Statistical analysis
   - Category match counts
   - Top opportunities
   - Multi-category startups

3. **`downloads/axa_evaluation_results_report.md`** - Human-readable markdown report

4. **`downloads/axa_evaluation_checkpoint.json`** - Progress checkpoint (for resuming)

## 🔍 Understanding the Results

### Priority Tiers

- **Tier 1: Critical Priority** - High confidence (≥75%) + matches 2+ categories
- **Tier 2: High Priority** - Good confidence (≥60%) OR matches 2+ categories
- **Tier 3: Medium Priority** - Moderate confidence (≥40%) OR matches 1 category
- **Tier 4: Low Priority** - Low or no matches

### Confidence Scores

- **80-100%**: Strong match, highly recommended for AXA
- **60-79%**: Good match, worth exploring
- **40-59%**: Moderate match, potential fit
- **0-39%**: Weak or no match

### Example Result

```json
{
  "startup_id": 123,
  "startup_name": "Cognita",
  "evaluation_date": "2025-11-16T00:58:00Z",
  "categories_matched": [
    {
      "category": "agentic_solutions",
      "matches": true,
      "confidence": 90,
      "reasoning": "Cognita explicitly develops AI agents and intelligent assistants for process automation, directly aligning with AXA's need for agent-based solutions."
    },
    {
      "category": "workflow_automation",
      "matches": true,
      "confidence": 85,
      "reasoning": "The startup focuses on automating processes and workflow orchestration, suitable for AXA's business automation needs."
    }
  ],
  "overall_score": 87.5,
  "priority_tier": "Tier 1: Critical Priority",
  "axa_fit_summary": "Matches 2 categories: agentic_solutions, workflow_automation. Overall confidence: 88%."
}
```

## 🎯 Finding Key Opportunities

### Top Overall Opportunities

View startups with highest scores:

```bash
# View top 20 in markdown report
cat downloads/axa_evaluation_results_report.md | grep "^[0-9]\." | head -20
```

### Multi-Category Startups

These are strategic - they can serve multiple AXA needs:

```bash
# Extract from JSON
python3 -c "
import json
with open('downloads/axa_evaluation_results_analysis.json') as f:
    data = json.load(f)
print('Multi-Category Startups:')
for s in data['multi_category_startups'][:10]:
    print(f\"  {s['startup_name']}: {s['categories_count']} categories - {', '.join(s['categories'])}\")
"
```

### Category-Specific Leaders

Find top startups for a specific category:

```bash
# Example: Top agentic platform providers
python3 -c "
import json
with open('downloads/axa_evaluation_results_analysis.json') as f:
    data = json.load(f)
cat = data['category_matches']['agentic_platform']
print(f\"{cat['count']} Agentic Platform matches:\")
for s in cat['startups'][:10]:
    print(f\"  {s['startup_name']}: {s['confidence']}% - {s['reasoning']}\")
"
```

## ⚡ Performance & Optimizations

### Speed Improvements

The **fast version** (`axa_comprehensive_evaluator_fast.py`) includes:

1. **Smart Pre-filtering** - Only evaluates relevant categories per startup
2. **Batch Evaluation** - Multiple categories in one LLM call (5-10x faster)
3. **Checkpoint System** - Resume from any point
4. **Optimized Prompts** - Faster, more focused prompts

### Expected Performance

- **Full evaluation (238 startups)**: 15-30 minutes
- **Per startup**: ~3-5 seconds (vs 30-60 seconds with old version)
- **Rate**: 10-15 startups/minute

### Adjusting Batch Size

For even faster evaluation (less detailed):

```bash
# Larger batches = faster but potentially less accuracy
python3 api/axa_comprehensive_evaluator_fast.py --batch-size 15
```

## 🔧 Advanced Usage

### Evaluate Specific Categories Only

```bash
# Only evaluate insurance-related categories
python3 api/axa_comprehensive_evaluator_fast.py \
  --categories insurance,underwriting,claims,health
```

### Custom Output Location

```bash
python3 api/axa_comprehensive_evaluator_fast.py \
  --output results/custom_evaluation.json
```

### Disable NVIDIA NIM (Use Fallback)

```bash
python3 api/axa_comprehensive_evaluator_fast.py --no-nvidia
```

## 📈 Analyzing Results

### Export to Excel

```python
import json
import pandas as pd

# Load results
with open('downloads/axa_evaluation_results.json') as f:
    results = json.load(f)

# Convert to DataFrame
rows = []
for r in results:
    matched_cats = [c['category'] for c in r['categories_matched'] if c['matches']]
    rows.append({
        'Startup': r['startup_name'],
        'Overall Score': r['overall_score'],
        'Tier': r['priority_tier'],
        'Categories Matched': len(matched_cats),
        'Categories': ', '.join(matched_cats),
        'Summary': r['axa_fit_summary']
    })

df = pd.DataFrame(rows)
df = df.sort_values('Overall Score', ascending=False)
df.to_excel('downloads/axa_evaluation.xlsx', index=False)
```

### Generate Custom Reports

```python
import json

with open('downloads/axa_evaluation_results.json') as f:
    results = json.load(f)

# Find all insurance-related startups
insurance_startups = []
for r in results:
    for cat in r['categories_matched']:
        if cat['matches'] and 'insurance' in cat['category'] or 'claims' in cat['category']:
            insurance_startups.append({
                'name': r['startup_name'],
                'category': cat['category'],
                'confidence': cat['confidence'],
                'reasoning': cat['reasoning']
            })
            break

print(f"Found {len(insurance_startups)} insurance-related startups")
for s in sorted(insurance_startups, key=lambda x: x['confidence'], reverse=True)[:10]:
    print(f"  {s['name']}: {s['confidence']}% - {s['reasoning']}")
```

## 🛠️ Troubleshooting

### Evaluation is Too Slow

- Use the **fast version**: `axa_comprehensive_evaluator_fast.py`
- Check your internet connection (API calls to NVIDIA)
- Try increasing `--batch-size`

### NVIDIA NIM Not Working

```bash
# Check configuration
cd api
python3 -c "from llm_config import is_nvidia_nim_configured; print(is_nvidia_nim_configured())"

# Verify API key in .env
cat .env | grep NVIDIA_API_KEY
```

### Out of Memory / Crashes

- Reduce batch size
- Process in smaller chunks using `--max-startups 50`
- Use `--resume` to continue from checkpoint

### LLM Returns Invalid JSON

The system handles this automatically. Check logs:

```bash
tail -100 logs/llm/$(ls -t logs/llm/ | head -1)
```

## 📝 Best Practices

### 1. Start with a Test Run

```bash
# Test on 10 startups first
python3 api/axa_comprehensive_evaluator_fast.py --max-startups 10
```

### 2. Use Checkpoints

Always enable checkpoints (default). If interrupted, resume:

```bash
./run_axa_evaluation.sh --resume
```

### 3. Review Results Iteratively

- Check top 20 opportunities first
- Look for multi-category matches
- Verify confidence scores align with expectations

### 4. Validate Top Results

For critical matches, manually verify:
- Visit startup website
- Check LinkedIn
- Review product documentation

### 5. Export for Team Review

```bash
# Generate Excel for easy sharing
python3 -c "
import json, pandas as pd
with open('downloads/axa_evaluation_results.json') as f:
    results = json.load(f)
# ... (see Excel export above)
"
```

## 🎓 Understanding the AI Evaluation

### What the LLM Considers

For each startup, the AI evaluates:

1. **Direct Alignment** - Does the product/service directly match the category?
2. **AXA Usability** - Can AXA leverage this as a provider/vendor?
3. **Specific Capabilities** - What concrete features align with the category?
4. **Enterprise Readiness** - Is it B2B/enterprise-focused?
5. **Maturity** - Funding, team size, stage

### Evaluation Criteria

- **B2B/B2G Focus** - B2C startups get lower scores
- **Domain Expertise** - Insurance/enterprise experience valued
- **Specific Features** - Generic AI gets lower scores than domain-specific
- **Maturity** - Well-funded startups with teams score higher

## 📞 Support

For issues or questions:

1. Check logs: `logs/llm/`
2. Review checkpoint: `downloads/axa_evaluation_checkpoint.json`
3. Test with `--max-startups 5` to isolate issues

## 🔄 Updating the Evaluation

To re-evaluate with new criteria:

1. Delete checkpoint: `rm downloads/axa_evaluation_checkpoint.json`
2. Run fresh evaluation
3. Compare results with previous run

## 📊 Example Workflow

```bash
# 1. Test on a few startups
python3 api/axa_comprehensive_evaluator_fast.py --max-startups 10

# 2. Review test results
cat downloads/axa_evaluation_results_report.md | head -100

# 3. Run full evaluation
./run_axa_evaluation.sh

# 4. Generate Excel for team
python3 scripts/export_to_excel.py  # (create this script)

# 5. Review top opportunities
cat downloads/axa_evaluation_results_report.md | grep "Tier 1"

# 6. Deep dive on specific categories
python3 -c "import json; ..." # (see examples above)
```

## 🎉 What's Next?

After evaluation:

1. **Review Top 30 Opportunities** - Focus on Tier 1 & 2
2. **Verify Multi-Category Matches** - High strategic value
3. **Research Top Startups** - Visit websites, check product docs
4. **Schedule Demos** - Contact high-confidence matches
5. **Track in CRM** - Import results for ongoing evaluation

---

**Happy Evaluating!** 🚀
