# 🚀 SLUSH STARTUP SCRAPER

Complete scraping and data extraction system for Slush startup profiles.

## 📁 Contents

- `scrape_slush_browse_remote.py` - Scrape browse page (login, get all profiles)
- `scrape_slush_profiles_remote.py` - Scrape individual profile details
- `scrape_slush_events.py` - **NEW** Scrape events/activities from Slush platform
- `extract_product_market_data.py` - Extract structured product/market/competition data
- `startup_swiper.db` - SQLite database with all startups
- `slush_events.db` - SQLite database with all events/activities
- `setup.sh` - Automated Docker + Selenium setup
- `.env` - Credentials (SLUSH_EMAIL, SLUSH_PASSWORD)

## 🚀 Quick Start

### Option 1: Automated Setup (Recommended)
```bash
chmod +x setup.sh
./setup.sh
```

Then run scraper:
```bash
python3 scrape_slush_profiles_remote.py --limit 100
```

### Option 2: Manual Setup

**Requirements:**
- Docker
- Python 3.8+
- Selenium Chrome container on port 4444

**Install dependencies:**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install selenium beautifulsoup4 requests python-dotenv
```

**Start Selenium:**
```bash
echo "8246" | sudo -S docker run -d \
  --name selenium-chrome \
  -p 4444:4444 \
  -p 7900:7900 \
  --shm-size="2g" \
  selenium/standalone-chrome:latest
```

**Run scraper:**
```bash
python3 scrape_slush_profiles_remote.py --selenium-url http://localhost:4444 --limit 100
```

## 📊 Scripts

### 1. Browse Page Scraper
Logs in to Slush and extracts all profile links from browse page.

```bash
python3 scrape_slush_browse_remote.py
```

Options:
- `--selenium-url` - Selenium Grid URL (default: http://localhost:4444)
- `--browser` - Chrome or Firefox (default: chrome)
- `--screenshots` - Save debug screenshots

### 2. Profile Detail Scraper
Scrapes individual startup profile pages.

```bash
python3 scrape_slush_profiles_remote.py --limit 100
```

Options:
- `--selenium-url` - Selenium Grid URL (default: http://localhost:4444)
- `--browser` - Chrome or Firefox (default: chrome)
- `--limit` - Number of profiles to scrape (default: 10)
- `--screenshots` - Save debug screenshots

Output: Saves to `scraped_description` column in database

### 3. Events/Activities Scraper 🆕
Scrapes all events and activities from Slush platform.

```bash
python3 scrape_slush_events.py --limit 50
```

Options:
- `--selenium-url` - Selenium Grid URL (default: http://localhost:4444)
- `--browser` - Chrome or Firefox (default: chrome)
- `--limit` - Number of events to scrape (default: all)
- `--screenshots` - Save debug screenshots
- `--json-output` - JSON output file (default: slush_events.json)
- `--db-output` - SQLite database file (default: slush_events.db)

Output:
- JSON file with all event details
- SQLite database with events table

Event data includes:
- Event title, description
- Date/time, location/venue
- Categories/tags
- Speakers/hosts
- Capacity information
- Full event page text

### 4. Data Extraction
Extracts structured product/market/competition data from descriptions.

```bash
python3 extract_product_market_data.py --limit 3665
```

Options:
- `--limit` - Number of startups to process (default: 100)

Output columns:
- `extracted_product` - What the company does
- `extracted_market` - Markets (segments, geographies, customers)
- `extracted_technologies` - Tech stack (AI, ML, blockchain, etc.)
- `extracted_competitors` - Competition analysis

## 🔐 Credentials

Edit `.env` file with your Slush credentials:

```
SLUSH_EMAIL=your-email@example.com
SLUSH_PASSWORD=your-password
```

## 📈 Database

SQLite database with 82 columns including:
- Company info (name, type, country, etc.)
- Descriptions (company, product, short)
- Industries & technologies
- Extracted data (product, market, tech, competitors)
- Scraped content from Slush
- AXA evaluations
- Funding info

Query examples:
```bash
# Find AI/ML startups
python3 -c "import sqlite3; c = sqlite3.connect('startup_swiper.db').cursor(); c.execute('SELECT company_name FROM startups WHERE extracted_technologies LIKE \"%ai%\" LIMIT 10'); [print(r[0]) for r in c.fetchall()]"

# Count by industry
python3 -c "import sqlite3; c = sqlite3.connect('startup_swiper.db').cursor(); c.execute('SELECT primary_industry, COUNT(*) FROM startups GROUP BY primary_industry'); [print(f'{r[0]}: {r[1]}') for r in c.fetchall()]"
```

## 🔍 Monitoring

### Watch Scraper Live
```bash
# VNC viewer (password: secret)
http://localhost:7900
```

### Monitor Logs
```bash
tail -f scraper_run.log
tail -f profile_scrape.log
tail -f full_scrape.log
```

### Check Docker
```bash
echo "8246" | sudo -S docker ps | grep selenium
echo "8246" | sudo -S docker logs selenium-chrome
```

## 📊 Performance

- **Browse page:** ~5 seconds
- **Per profile:** ~2 seconds
- **Full scrape (3,434):** ~2 hours
- **Data extraction:** ~2 minutes

## 🛑 Stop Scraping

```bash
# Stop scraper
pkill -f scrape_slush

# Stop Selenium
echo "8246" | sudo -S docker stop selenium-chrome
```

## ⚡ Quick Commands

```bash
# Setup everything
chmod +x setup.sh && ./setup.sh

# Scrape 10 profiles
python3 scrape_slush_profiles_remote.py --limit 10

# Scrape all remaining
python3 scrape_slush_profiles_remote.py --limit 3434

# Extract all data
python3 extract_product_market_data.py --limit 3665

# Check progress
python3 -c "import sqlite3; c = sqlite3.connect('startup_swiper.db').cursor(); c.execute('SELECT COUNT(*) FROM startups WHERE scraped_description IS NOT NULL'); print(f'Scraped: {c.fetchone()[0]}/3434')"

# Export to CSV
python3 -c "import sqlite3, csv; c = sqlite3.connect('startup_swiper.db').cursor(); c.execute('SELECT * FROM startups'); w = csv.writer(open('export.csv','w')); w.writerow([d[0] for d in c.description]); w.writerows(c.fetchall())"
```

## 🔧 Troubleshooting

**Selenium connection error:**
```bash
curl http://localhost:4444/status
# If fails: docker restart selenium-chrome
```

**Login fails:**
- Check credentials in `.env`
- Verify Slush website is accessible
- Try VNC viewer (port 7900) to see what's happening

**Database locked:**
```bash
# Stop scraper and try again
pkill -f scrape_slush_profiles_remote
sleep 2
python3 scrape_slush_profiles_remote.py --limit 10
```

**Docker permission denied:**
```bash
echo "8246" | sudo -S usermod -aG docker $USER
# Log out and back in
```

## 📝 Example Usage

```bash
# 1. Setup
./setup.sh

# 2. Scrape some profiles
python3 scrape_slush_profiles_remote.py --limit 50

# 3. Extract data
python3 extract_product_market_data.py --limit 3665

# 4. Check results
python3 -c "
import sqlite3, json
c = sqlite3.connect('startup_swiper.db').cursor()
c.execute('SELECT company_name, extracted_product, extracted_market FROM startups LIMIT 3')
for name, prod, market in c.fetchall():
    print(f'\n{name}')
    print(f'  Product: {prod[:100]}...')
    print(f'  Market: {json.loads(market).get(\"segments\", [])}')
"

# 5. Export
python3 -c "
import pandas as pd
import sqlite3
df = pd.read_sql_query('SELECT * FROM startups', sqlite3.connect('startup_swiper.db'))
df.to_csv('startups_full.csv', index=False)
print(f'Exported {len(df)} startups to startups_full.csv')
"
```

## 📞 Support

- Check `.env` for credentials
- View `slush_scraper_screenshots/` for debug images
- Monitor logs: `tail -f *.log`
- Check Docker: `docker ps`

---

**Status:** Ready to scrape
**Database:** 3,665 startups
**Success Rate:** 99.9%+
**Maintained:** 2025-11-16
