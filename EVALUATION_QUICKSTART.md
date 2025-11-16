# AXA Startup Evaluator - Quick Start

## ⚡ Run Full Evaluation (Fastest Way)

```bash
cd /home/akyo/startup_swiper
./run_axa_evaluation.sh
```

**Time:** ~15-30 minutes for all 238 startups

## 📊 View Results

```bash
# View markdown report
cat downloads/axa_evaluation_results_report.md | less

# View top 20 opportunities
cat downloads/axa_evaluation_results_report.md | grep "^[0-9]\." | head -20
```

## 🎯 What You Get

1. **Full results JSON** - `downloads/axa_evaluation_results.json`
2. **Analysis JSON** - `downloads/axa_evaluation_results_analysis.json`
3. **Markdown report** - `downloads/axa_evaluation_results_report.md`

## 📈 Categories Evaluated

✅ **Agentic Platform** - AI agent infrastructure  
✅ **Agentic Solutions** - Ready-to-use AI agents  
✅ **Workflow Automation** - RPA, BPA, process automation  
✅ **Sales Training** - Sales coaching and enablement  
✅ **Insurance** - Insurtech (policy, claims, underwriting)  
✅ **Underwriting** - Risk assessment and triage  
✅ **Claims** - Claims automation and fraud detection  
✅ **Coding** - Developer tools and AI coding  
✅ **Health** - Digital health and wellness  
✅ **AI Evals** - LLM evaluation frameworks  
✅ **LLM Observability** - AI monitoring and tracing  
✅ **Contact Center** - Customer service AI  

## 🔧 Options

```bash
# Resume from checkpoint
./run_axa_evaluation.sh --resume

# Test with limited startups
python3 api/axa_comprehensive_evaluator_fast.py --max-startups 10

# Custom output location
python3 api/axa_comprehensive_evaluator_fast.py --output custom/path.json
```

## 📖 Full Documentation

See **`AXA_EVALUATOR_GUIDE.md`** for:
- Detailed usage instructions
- How to analyze results
- Troubleshooting
- Advanced features
- Export to Excel

## 🎯 Key Features

- ⚡ **Fast** - Optimized batch evaluation
- 🎯 **Smart** - Pre-filters relevant categories
- 💾 **Resumable** - Checkpoint system
- 📊 **Comprehensive** - 12 strategic categories
- 🤖 **AI-Powered** - NVIDIA NIM (DeepSeek-R1)
- 📈 **Actionable** - Priority tiers and confidence scores

## 🚀 Ready to Start?

```bash
cd /home/akyo/startup_swiper
./run_axa_evaluation.sh
```

Then check `downloads/axa_evaluation_results_report.md` for results!
