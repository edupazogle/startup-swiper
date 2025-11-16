# AXA Enhanced Batch Evaluator - Quick Start Guide

## 🚀 Quick Start (5 minutes)

### Step 1: Activate Environment
```bash
cd /home/akyo/startup_swiper
source .venv/bin/activate
```

### Step 2: Test with 5 Startups
```bash
python3 api/axa_enhanced_batch_evaluator.py --limit 5 --batch-size 5 --workers 1
```

**Output**: `downloads/axa_batch_results.jsonl` with 5 evaluated startups

### Step 3: Import Results (Dry Run)
```bash
python3 evaluator/import_batch_results.py --dry-run
```

**Preview**: Shows what would be updated without changing database

### Step 4: Import for Real
```bash
python3 evaluator/import_batch_results.py
```

**Result**: Database updated with new scores and tiers

---

## 📊 Full Evaluation (10-15 minutes)

```bash
# Run batch evaluator
python3 api/axa_enhanced_batch_evaluator.py --batch-size 15 --workers 8

# Monitor in another terminal
watch wc -l downloads/axa_batch_results.jsonl

# When complete, import results
python3 evaluator/import_batch_results.py
```

---

## 📈 Compare Results

### Before (Original V7 Formula)
```
Cognita: 74.0 (Tier 1) - Basic formula-based scoring
```

### After (LLM Intelligent)
```
Cognita: 85.0 (Tier 1) - LLM evaluation with scaling assessment
- Confidence: high
- Scaling Potential: high
- Strengths: Large team, global reach, AI focus
- Concerns: Undisclosed funding, vague insurance fit
```

---

## 🎯 Configuration Presets

### Fast (Fewer API calls, more context)
```bash
python3 api/axa_enhanced_batch_evaluator.py --batch-size 25 --workers 4
```
- 100 API calls for 2676 startups
- ~15-20 minutes
- More LLM context per batch

### Balanced (Default)
```bash
python3 api/axa_enhanced_batch_evaluator.py --batch-size 15 --workers 8
```
- 180 API calls for 2676 startups
- ~10-15 minutes
- Good balance of speed and parallelism

### Parallel (Maximum parallelism)
```bash
python3 api/axa_enhanced_batch_evaluator.py --batch-size 10 --workers 12
```
- 270 API calls for 2676 startups
- ~8-12 minutes
- Maximum parallelism, respects rate limits

---

## 📁 Output Files

### Results: `downloads/axa_batch_results.jsonl`
One JSON object per line:
```json
{
  "startup_id": 2,
  "startup_name": "Cognita",
  "rule": "Rule 1",
  "score": 85,
  "confidence": "high",
  "scaling_potential": "high",
  "strengths": [...]
}
```

### Checkpoint: `downloads/axa_batch_checkpoint.json`
Progress tracking:
```json
{
  "evaluated_ids": [1, 2, 3, ...],
  "processed": 5,
  "failed": 0,
  "batch_count": 1
}
```

---

## ✅ Verification

### Count Results
```bash
wc -l downloads/axa_batch_results.jsonl
```

### Check Specific Startup
```bash
grep '"startup_id": 2' downloads/axa_batch_results.jsonl | python3 -m json.tool
```

### View Database Updates
```bash
python3 << 'EOF'
import sys
sys.path.insert(0, 'api')
from database import SessionLocal
from models_startup import Startup

db = SessionLocal()
startups = db.query(Startup).filter(Startup.id.in_([2,3,4,6,7])).all()

for s in startups:
    print(f"{s.company_name:20s}: {s.axa_overall_score:6.1f} | {s.axa_priority_tier}")

db.close()
EOF
```

---

## 🔄 Resume Interrupted Run

If the evaluator stops mid-run:
```bash
# Automatically resumes from checkpoint
python3 api/axa_enhanced_batch_evaluator.py --batch-size 15 --workers 8
```

The checkpoint tracks evaluated startups, so you won't waste API calls re-evaluating.

---

## 🛠️ Troubleshooting

### "NVIDIA_API_KEY not set"
```bash
cat api/.env | grep NVIDIA_API_KEY
# Should show: NVIDIA_API_KEY=nvapi-...
```

### "timeout waiting for response"
```bash
# Increase timeout
python3 api/axa_enhanced_batch_evaluator.py --timeout 180
```

### "rate limit exceeded"
```bash
# Reduce parallel workers
python3 api/axa_enhanced_batch_evaluator.py --workers 2
```

### "No results generated"
```bash
# Check with dry-run first
python3 api/axa_enhanced_batch_evaluator.py --limit 1 --dry-run
```

---

## 📊 Scoring Scale

| Score | Tier | Meaning |
|-------|------|---------|
| 90-92 | Tier 1 | Exceptional fit |
| 75-89 | Tier 1 | Strong fit |
| 60-74 | Tier 2 | Good fit |
| 45-59 | Tier 3 | Fair fit |
| 30-44 | Tier 4 | Limited fit |

---

## 🎓 Key Differences from V7 Formula

| Aspect | V7 Formula | LLM Batch |
|--------|-----------|-----------|
| **Speed** | Instant | 10-15 min for all |
| **Context** | Basic fields | All database fields |
| **Intelligence** | Rule-based | LLM-based with insurance perspective |
| **Scaling Assessment** | None | Included |
| **Confidence** | N/A | High/Medium/Low |
| **Margins** | Fixed formula | Intelligent adjustments |
| **Realistic** | Moderate | High |

---

## 📚 Full Documentation

- Detailed Guide: `evaluator/BATCH_EVALUATOR_GUIDE.md`
- Implementation Summary: `evaluator/BATCH_EVALUATOR_SUMMARY.md`
- Source Code: `api/axa_enhanced_batch_evaluator.py`

---

## ⏱️ Time Estimates

| Configuration | Time | API Calls |
|---------------|------|-----------|
| Test (5 startups) | 10 sec | 1 |
| Quick (100 startups) | 90 sec | 7 |
| Medium (500 startups) | 5 min | 35 |
| Full (2676 startups) | 10-20 min | 100-270 |

---

**Ready to evaluate? Start with:**
```bash
cd /home/akyo/startup_swiper
source .venv/bin/activate
python3 api/axa_enhanced_batch_evaluator.py --limit 5 --batch-size 5 --workers 1
```
