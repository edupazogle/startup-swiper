# Selenium Testing - Quick Reference

## 🚀 Get Started in 3 Steps

```bash
# 1. Setup (first time only)
cd /home/akyo/startup_swiper/tests
./setup_selenium.sh

# 2. Start the app (if not running)
cd .. && ./launch.sh

# 3. Run tests
cd tests && ./run_tests.sh
```

## 📝 Command Cheat Sheet

### Test Runner (Easiest)
```bash
./run_tests.sh                 # Full test with GUI
./run_tests.sh --headless      # No GUI (for servers)
./run_tests.sh --basic         # Quick navigation test
./run_tests.sh --url http://localhost:3000  # Custom URL
```

### Direct Python Scripts
```bash
# Basic navigation
python3 selenium_navigation_test.py

# Full exploration
python3 selenium_full_exploration.py

# With options
python3 selenium_full_exploration.py --headless --email user@test.com
```

## 🎯 What Gets Tested

| View | Feature | Status |
|------|---------|--------|
| 🎴 Swipe | Startup cards, Like/Dislike | ✅ |
| 🚀 Dashboard | Analytics, Metrics | ✅ |
| 💡 Insights | Meeting insights | ✅ |
| 📅 Calendar | Events scheduling | ✅ |
| 🤖 AI | Chat interface | ✅ |
| 👤 Admin | Admin panel | ✅ |

## 📸 Output Locations

```
tests/
├── selenium_screenshots/          # All screenshots (timestamped)
└── selenium_test_*.log           # Test logs
```

## ⚡ Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| ChromeDriver not found | `sudo apt install chromium-chromedriver` |
| App not running | `cd .. && ./launch.sh` |
| Selenium not installed | `pip3 install -r requirements.txt` |
| Elements not found | Check if app UI changed, view screenshots |

## 📊 Read Results

```bash
# View latest log
tail -f selenium_test_*.log

# Count screenshots
ls selenium_screenshots/*.png | wc -l

# View specific screenshot
eog selenium_screenshots/tab_swipe.png
```

## 🔧 Common Options

| Option | Description | Example |
|--------|-------------|---------|
| `--headless` | No GUI | `./run_tests.sh --headless` |
| `--url URL` | Custom base URL | `--url http://localhost:3000` |
| `--email EMAIL` | Login email | `--email test@example.com` |
| `--password PWD` | Login password | `--password secret123` |
| `--basic` | Quick test | `./run_tests.sh --basic` |
| `--full` | Full test | `./run_tests.sh --full` |

## 📚 File Guide

| File | Purpose |
|------|---------|
| `selenium_navigation_test.py` | Basic tab navigation |
| `selenium_full_exploration.py` | Full test with login |
| `run_tests.sh` | Easy test runner |
| `setup_selenium.sh` | Environment setup |
| `requirements.txt` | Python dependencies |
| `README.md` | Full documentation |

## 💡 Pro Tips

1. **First run always takes longer** - WebDriver initialization
2. **Headless is faster** - Use for automation/CI
3. **Screenshots show what happened** - Check them if tests fail
4. **Logs have timestamps** - Easy to track what went wrong
5. **App must be running** - Start with `./launch.sh`

## 🆘 Get Help

```bash
# Show test runner help
./run_tests.sh --help

# Check Python script help
python3 selenium_full_exploration.py --help

# Read full docs
cat README.md
```

## 🎓 Learn More

- Full docs: `tests/README.md`
- Summary: `SELENIUM_TESTS_SUMMARY.md`
- Selenium docs: https://selenium-python.readthedocs.io/

---

**Quick Start:** `cd tests && ./setup_selenium.sh && ./run_tests.sh`
