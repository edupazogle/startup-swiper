# Selenium Automation Tests for Startup Swiper

Comprehensive Selenium-based automation scripts for testing navigation and functionality of the Startup Swiper application.

## 📁 Files

### Test Scripts
1. **`selenium_navigation_test.py`** - Basic navigation testing
2. **`selenium_full_exploration.py`** - Full exploration with login support

### Setup Files
- **`requirements.txt`** - Python dependencies
- **`setup_selenium.sh`** - Automated setup script
- **`README.md`** - This file

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Run the setup script (installs everything)
./setup_selenium.sh

# Or manually install
pip3 install -r requirements.txt
```

### 2. Start the Application

Make sure the application is running:
```bash
cd /home/akyo/startup_swiper
./launch.sh
```

The app should be accessible at `http://localhost:5173`

### 3. Run Tests

**Basic Navigation Test:**
```bash
python3 selenium_navigation_test.py
```

**Full Exploration (with login):**
```bash
python3 selenium_full_exploration.py
```

**With Custom Options:**
```bash
# Run in headless mode
python3 selenium_full_exploration.py --headless

# Custom URL
python3 selenium_full_exploration.py --url http://localhost:3000

# Custom credentials
python3 selenium_full_exploration.py --email user@example.com --password mypassword
```

## 📋 What Gets Tested

### Navigation Elements
- ✅ **Swipe View** - Startup swiping interface
- ✅ **Dashboard View** - Analytics and metrics
- ✅ **Insights View** - Meeting insights
- ✅ **Calendar View** - Event scheduling
- ✅ **AI Assistant View** - AI chat interface
- ✅ **Admin View** - Admin panel (if accessible)

### UI Elements
- ✅ Header buttons and logos
- ✅ Navigation tabs
- ✅ Side menu elements
- ✅ Interactive buttons
- ✅ Forms and inputs
- ✅ Cards and content areas

### Features Tested
- 🔐 Login functionality (if present)
- 🧭 Navigation between views
- 🎯 Interactive elements (buttons, forms)
- 📸 Screenshot capture at each step
- 📝 Detailed logging

## 📊 Output

### Screenshots
Screenshots are saved in the `selenium_screenshots/` directory with timestamps:
- `00_initial_load.png` - First page load
- `01_after_login.png` - After login attempt
- `tab_swipe.png` - Swipe view
- `tab_dashboard.png` - Dashboard view
- `tab_insights.png` - Insights view
- `tab_calendar.png` - Calendar view
- `tab_ai.png` - AI Assistant view
- `final_state.png` - Final state

### Log Files
Log files are saved as `selenium_test_YYYYMMDD_HHMMSS.log` containing:
- Timestamps for all actions
- Success/failure messages
- Error details
- Screenshot locations

## ⚙️ Configuration

### Command Line Options

**For `selenium_navigation_test.py`:**
```bash
--url URL       Base URL (default: http://localhost:5173)
--headless      Run without GUI
```

**For `selenium_full_exploration.py`:**
```bash
--url URL       Base URL (default: http://localhost:5173)
--api URL       API URL (default: http://localhost:8000)
--headless      Run without GUI
--email EMAIL   Login email (default: test@example.com)
--password PWD  Login password (default: testpassword123)
```

### Environment Configuration

You can also set environment variables:
```bash
export TEST_BASE_URL=http://localhost:5173
export TEST_API_URL=http://localhost:8000
export TEST_EMAIL=user@example.com
export TEST_PASSWORD=mypassword
```

## 🛠️ Troubleshooting

### Chrome/ChromeDriver Issues

**Problem:** ChromeDriver not found
```bash
sudo apt-get update
sudo apt-get install -y chromium-browser chromium-chromedriver
```

**Problem:** Chrome version mismatch
```bash
# Check versions
google-chrome --version
chromedriver --version

# Update ChromeDriver
pip3 install --upgrade selenium webdriver-manager
```

### Application Not Running

**Problem:** Connection refused to localhost:5173
```bash
# Start the application
cd /home/akyo/startup_swiper
./launch.sh

# Verify it's running
curl http://localhost:5173
```

### Headless Mode Issues

**Problem:** Screenshots are blank in headless mode
```bash
# Run with visible browser for debugging
python3 selenium_full_exploration.py  # without --headless
```

### Element Not Found

**Problem:** Elements not loading fast enough
- The scripts have built-in waits (10 seconds default)
- Increase timeout in the script if needed
- Check if the app UI has changed

## 📝 Script Details

### selenium_navigation_test.py

**Purpose:** Basic navigation testing
- Tests all main tabs
- Captures screenshots
- Logs all actions
- Suitable for quick checks

**Key Features:**
- Simple navigation flow
- Minimal configuration
- Fast execution
- Good for CI/CD

### selenium_full_exploration.py

**Purpose:** Comprehensive testing with login
- Attempts login
- Explores all menu elements
- Tests interactive features
- Deep content exploration

**Key Features:**
- Login support
- Side menu exploration
- Content interaction
- Detailed logging
- Custom credentials

## 🔧 Customization

### Adding New Tests

Edit the script and add new methods:

```python
def test_my_feature(self):
    """Test my custom feature"""
    self.log("Testing my feature...")
    
    # Your test code here
    element = self.wait_for_clickable(By.ID, "my-button")
    if element:
        element.click()
        self.take_screenshot("my_feature")
        self.log("✓ My feature works")
```

Then call it in `run_full_exploration()`:

```python
def run_full_exploration(self):
    # ... existing code ...
    self.test_my_feature()
```

### Modifying Selectors

Update selectors if the UI changes:

```python
# In the script, find the selector:
tab = self.wait_for_clickable(By.XPATH, "//button[@value='swipe']")

# Update to match new UI:
tab = self.wait_for_clickable(By.CSS_SELECTOR, ".nav-button-swipe")
```

## 📈 Integration with CI/CD

### GitHub Actions Example

```yaml
name: Selenium Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.x'
      
      - name: Install dependencies
        run: |
          cd tests
          pip install -r requirements.txt
          sudo apt-get install -y chromium-browser chromium-chromedriver
      
      - name: Start application
        run: |
          ./launch.sh &
          sleep 10
      
      - name: Run tests
        run: |
          cd tests
          python3 selenium_full_exploration.py --headless
      
      - name: Upload screenshots
        uses: actions/upload-artifact@v2
        if: always()
        with:
          name: selenium-screenshots
          path: tests/selenium_screenshots/
```

## 📚 Resources

- [Selenium Documentation](https://www.selenium.dev/documentation/)
- [WebDriver API](https://www.selenium.dev/selenium/docs/api/py/)
- [Chrome DevTools Protocol](https://chromedevtools.github.io/devtools-protocol/)

## 🤝 Contributing

To add new tests:
1. Create a new method in the test class
2. Follow the existing pattern (log, screenshot, verify)
3. Add it to the test suite
4. Update this README

## 📄 License

Part of the Startup Swiper project.

## 🆘 Support

For issues:
1. Check the log file for detailed errors
2. Review screenshots to see what the browser saw
3. Try running without `--headless` to watch the test
4. Verify the application is running and accessible

---

**Created:** 2025-11-14
**Last Updated:** 2025-11-14
