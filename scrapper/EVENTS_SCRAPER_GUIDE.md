# Slush Events Scraper - Usage Guide

## Overview

The `scrape_slush_events.py` script scrapes event/activity information from the Slush platform. It extracts details from:
- Browse page: https://platform.slush.org/slush25/activities/browse
- Individual event pages: https://platform.slush.org/slush25/activities/{event-id}

## Features

✅ **Automated Login** - Uses credentials from .env file
✅ **Smart Scrolling** - Automatically scrolls to load all events
✅ **Comprehensive Data Extraction** - Captures:
  - Event title and description
  - Date/time and location
  - Categories and tags
  - Speakers/hosts
  - Capacity information
  - Full event page content

✅ **Multiple Output Formats**
  - JSON file with structured data
  - SQLite database for easy querying
  - Optional screenshots for debugging

## Prerequisites

### 1. Selenium Chrome Container
The scraper needs a Selenium Grid running on port 4444.

**Start Selenium:**
```bash
sudo docker run -d \
  --name selenium-chrome \
  -p 4444:4444 \
  -p 7900:7900 \
  --shm-size="2g" \
  selenium/standalone-chrome:latest
```

**Check if running:**
```bash
sudo docker ps | grep selenium
```

**Access VNC viewer (optional):**
- URL: http://localhost:7900
- Password: secret

### 2. Python Dependencies
```bash
pip install selenium python-dotenv
```

### 3. Credentials
Make sure your `.env` file contains:
```env
SLUSH_EMAIL=your-email@example.com
SLUSH_PASSWORD=your-password
```

## Usage

### Quick Test (5 events)
```bash
cd /home/akyo/startup_swiper/scrapper
./test_events_scraper.sh
```

### Scrape All Events
```bash
python3 scrape_slush_events.py
```

### Scrape Limited Number
```bash
python3 scrape_slush_events.py --limit 20
```

### With Screenshots (Debug Mode)
```bash
python3 scrape_slush_events.py --limit 10 --screenshots
```

### Custom Output Files
```bash
python3 scrape_slush_events.py \
  --json-output my_events.json \
  --db-output my_events.db
```

### Use Firefox Instead of Chrome
```bash
python3 scrape_slush_events.py --browser firefox
```

### Custom Selenium URL
```bash
python3 scrape_slush_events.py --selenium-url http://remote-server:4444
```

## Command Line Options

| Option | Default | Description |
|--------|---------|-------------|
| `--selenium-url` | http://localhost:4444 | Selenium Grid URL |
| `--browser` | chrome | Browser to use (chrome/firefox) |
| `--limit` | None (all) | Max number of events to scrape |
| `--screenshots` | False | Save debug screenshots |
| `--json-output` | slush_events.json | JSON output filename |
| `--db-output` | slush_events.db | SQLite database filename |

## Output Files

### JSON Output (slush_events.json)
```json
{
  "scraped_at": "2025-11-17T14:30:00",
  "total_events": 42,
  "events": [
    {
      "url": "https://platform.slush.org/slush25/activities/762c3246-...",
      "event_id": "762c3246-0d7a-4054-b963-071591a6a55d",
      "title": "AI in Healthcare Panel",
      "description": "Join industry leaders discussing...",
      "datetime": "Nov 20, 2025 14:00-15:30",
      "location": "Main Stage",
      "categories": ["AI", "Healthcare", "Panel"],
      "speakers": ["John Doe (CEO, HealthAI)", "Jane Smith (CTO, MedTech)"],
      "capacity_info": "150 seats available",
      "scraped_at": "2025-11-17T14:30:15"
    }
  ]
}
```

### SQLite Database (slush_events.db)

**Table: events**

| Column | Type | Description |
|--------|------|-------------|
| event_id | TEXT PRIMARY KEY | Unique event ID from URL |
| url | TEXT | Full event page URL |
| title | TEXT | Event title |
| description | TEXT | Event description |
| datetime | TEXT | Date and time information |
| location | TEXT | Venue/location |
| categories | TEXT | JSON array of categories/tags |
| speakers | TEXT | JSON array of speakers/hosts |
| capacity_info | TEXT | Capacity/attendance info |
| full_text | TEXT | Complete page text (first 5000 chars) |
| scraped_at | TEXT | ISO timestamp |

**Query Examples:**

```bash
# Open database
sqlite3 slush_events.db

# Count total events
SELECT COUNT(*) FROM events;

# List all event titles
SELECT title FROM events;

# Find AI-related events
SELECT title, datetime, location 
FROM events 
WHERE title LIKE '%AI%' OR description LIKE '%AI%';

# Events with speakers
SELECT title, speakers 
FROM events 
WHERE speakers IS NOT NULL AND speakers != '[]';

# Export to CSV
.mode csv
.output events.csv
SELECT * FROM events;
.quit
```

## Troubleshooting

### Issue: Selenium container not running
**Solution:**
```bash
sudo docker start selenium-chrome
# or
sudo docker run -d --name selenium-chrome -p 4444:4444 -p 7900:7900 --shm-size="2g" selenium/standalone-chrome:latest
```

### Issue: Login fails
**Solutions:**
1. Check credentials in `.env` file
2. Verify you can login manually at https://platform.slush.org
3. Run with `--screenshots` to see what's happening:
   ```bash
   python3 scrape_slush_events.py --limit 1 --screenshots
   ```
4. Check screenshots in `slush_events_screenshots/` folder

### Issue: No events found
**Solutions:**
1. Increase wait time (edit script, increase `time.sleep()` values)
2. Check if you need to be logged in to see events
3. Verify URL is correct: https://platform.slush.org/slush25/activities/browse
4. Use VNC viewer to watch browser: http://localhost:7900

### Issue: Scraper is slow
**Solutions:**
1. Use `--limit` to scrape fewer events for testing
2. Reduce `time.sleep()` values in the script (but may cause failures)
3. Use multiple parallel containers (advanced)

## Performance Tips

### Scrape in Batches
```bash
# Scrape 50 events at a time
python3 scrape_slush_events.py --limit 50 --json-output batch1.json
python3 scrape_slush_events.py --limit 50 --json-output batch2.json
```

### Run in Background
```bash
nohup python3 scrape_slush_events.py > scraper.log 2>&1 &
tail -f scraper.log
```

### Schedule Regular Scraping
```bash
# Add to crontab
crontab -e

# Scrape events daily at 2 AM
0 2 * * * cd /home/akyo/startup_swiper/scrapper && python3 scrape_slush_events.py >> daily_scrape.log 2>&1
```

## Integration with Startup Swiper

### Import Events into Main Database
```python
import sqlite3
import json

# Read events
events_db = sqlite3.connect('slush_events.db')
events = events_db.execute('SELECT * FROM events').fetchall()

# Import into main database
main_db = sqlite3.connect('../startup_swiper.db')
# ... your import logic here
```

### Create Calendar Events
The scraped event data can be used to:
- Display in the Startup Swiper calendar
- Send notifications to users
- Match users with relevant events
- Generate meeting schedules

## Data Schema for Integration

### Recommended Events Table Structure
```sql
CREATE TABLE calendar_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id TEXT UNIQUE,
    title TEXT NOT NULL,
    description TEXT,
    event_date DATE,
    event_time TIME,
    location TEXT,
    category TEXT,
    speakers JSON,
    capacity INTEGER,
    url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Advanced Usage

### Custom Selectors
Edit the script to add more specific CSS selectors for your needs:

```python
# In scrape_event_details() method
# Add custom selectors for specific data
registration_link = self.driver.find_element(By.CSS_SELECTOR, "[class*='register']")
event_data["registration_url"] = registration_link.get_attribute("href")
```

### Export to Different Formats

**CSV Export:**
```bash
sqlite3 slush_events.db <<EOF
.mode csv
.output slush_events.csv
SELECT * FROM events;
EOF
```

**Excel Export (requires pandas):**
```python
import sqlite3
import pandas as pd

conn = sqlite3.connect('slush_events.db')
df = pd.read_sql_query("SELECT * FROM events", conn)
df.to_excel('slush_events.xlsx', index=False)
```

## Monitoring & Logging

### Check Logs
```bash
# Real-time monitoring
python3 scrape_slush_events.py 2>&1 | tee events_scrape.log

# Filter for errors
grep "ERROR\|Failed" events_scrape.log
```

### Screenshot Analysis
When `--screenshots` is enabled, screenshots are saved to `slush_events_screenshots/`:
- `01_login_page.png` - Initial login page
- `02_credentials_entered.png` - After entering credentials
- `03_after_login.png` - After login attempt
- `events_browse_page_loaded.png` - Browse page
- `events_browse_scroll_10.png` - After 10 scrolls
- `error_*.png` - Any errors encountered

## Support & Maintenance

### Update Selectors
If Slush changes their website structure, you may need to update CSS selectors in the script:
- Search for `CSS_SELECTOR` in the code
- Test with `--screenshots` to see what elements are available
- Use browser DevTools to inspect the page

### Version Control
Keep track of what works:
```bash
git add scrape_slush_events.py
git commit -m "Working version for Slush 2025"
git tag events-scraper-v1.0
```

## Examples

### Full Production Run
```bash
# 1. Start Selenium
sudo docker start selenium-chrome

# 2. Run scraper with all events
python3 scrape_slush_events.py \
  --json-output slush_events_$(date +%Y%m%d).json \
  --db-output slush_events_$(date +%Y%m%d).db \
  2>&1 | tee scrape_$(date +%Y%m%d).log

# 3. Verify results
sqlite3 slush_events_$(date +%Y%m%d).db "SELECT COUNT(*) FROM events;"
```

### Quick Data Check
```bash
# Count events by category
sqlite3 slush_events.db <<EOF
SELECT json_extract(value, '$') as category, COUNT(*) as count
FROM events, json_each(events.categories)
GROUP BY category
ORDER BY count DESC;
EOF
```

---

**Created:** November 17, 2025  
**Last Updated:** November 17, 2025  
**Version:** 1.0  
**Author:** Startup Swiper Team
