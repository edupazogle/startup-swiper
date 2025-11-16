# SCRAPER QUICK REFERENCE

## 📁 Folder Structure
```
scrapper/
├── setup.sh                              # Automated Docker setup
├── README.md                             # Full documentation
├── .env                                  # Credentials (edit with your login)
├── startup_swiper.db                     # SQLite database (31MB)
├── scrape_slush_browse_remote.py         # Login + get all profile links
├── scrape_slush_profiles_remote.py       # Scrape profile details
├── extract_product_market_data.py        # Extract structured data
├── logs/                                 # Log files
└── slush_scraper_screenshots/            # Debug screenshots
```

## ⚡ Quick Start (3 steps)

```bash
cd scrapper

# 1. Setup Docker + Selenium (one time)
chmod +x setup.sh
./setup.sh

# 2. Scrape profiles
python3 scrape_slush_profiles_remote.py --limit 100

# 3. Extract product/market data
python3 extract_product_market_data.py --limit 3665
```

## 🎯 Common Commands

### Monitor Scraping
```bash
tail -f profile_scrape.log
```

### Count Scraped Profiles
```bash
python3 -c "import sqlite3; c = sqlite3.connect('startup_swiper.db').cursor(); c.execute('SELECT COUNT(*) FROM startups WHERE scraped_description IS NOT NULL'); print(f'Scraped: {c.fetchone()[0]}')"
```

### Check Docker Status
```bash
echo "8246" | sudo -S docker ps | grep selenium
```

### Stop/Restart Selenium
```bash
echo "8246" | sudo -S docker stop selenium-chrome
echo "8246" | sudo -S docker start selenium-chrome
```

### Watch Scraper Live (VNC)
```
http://localhost:7900
Password: secret
```

## 📊 Database Queries

### Find AI/ML Companies
```python
import sqlite3, json
c = sqlite3.connect('startup_swiper.db').cursor()
c.execute("SELECT company_name FROM startups WHERE extracted_technologies LIKE '%ai%' LIMIT 10")
for row in c.fetchall():
    print(row[0])
```

### Export to CSV
```bash
python3 -c "
import pandas as pd, sqlite3
df = pd.read_sql_query('SELECT * FROM startups', sqlite3.connect('startup_swiper.db'))
df.to_csv('export.csv', index=False)
print(f'Exported {len(df)} startups')
"
```

### Get Market Distribution
```python
import sqlite3, json
c = sqlite3.connect('startup_swiper.db').cursor()
c.execute("SELECT extracted_market FROM startups LIMIT 5")
for row in c.fetchall():
    if row[0]:
        data = json.loads(row[0])
        print(f"Segments: {data.get('segments', [])}")
```

## 🔐 Setup Credentials

Edit `.env`:
```
SLUSH_EMAIL=your-email@example.com
SLUSH_PASSWORD=your-password
```

## 📈 Performance Tips

- **Scrape in batches:** `--limit 100` instead of all at once
- **Run overnight:** Full scrape takes ~2 hours
- **Monitor progress:** Check `tail -f *.log`
- **Check Docker:** `docker logs selenium-chrome` if issues

## 🛑 Troubleshooting

| Issue | Solution |
|-------|----------|
| Selenium won't connect | `./setup.sh` or `docker ps` |
| Login fails | Check `.env` credentials |
| Database locked | `pkill -f scrape_slush` then retry |
| Permission denied | `echo "8246" \| sudo -S usermod -aG docker $USER` |

## 📋 Database Columns

**Key product/market columns:**
- `company_name` - Company name
- `description` - Product description (95%)
- `company_description` - Company pitch (99%)
- `extracted_product` - Extracted product (100%)
- `extracted_market` - Market data (JSON, 100%)
- `extracted_technologies` - Tech stack (JSON, 100%)
- `extracted_competitors` - Competition (JSON, 100%)
- `scraped_description` - Slush page content
- `primary_industry` - Main industry
- `website` - Company website

## 🚀 Next Steps

1. Edit `.env` with your credentials
2. Run `./setup.sh`
3. Run `python3 scrape_slush_profiles_remote.py --limit 100`
4. Monitor with `tail -f profile_scrape.log`
5. Extract data with `python3 extract_product_market_data.py`

## 📞 Files to Check

- Logs: `*.log` files
- Screenshots: `slush_scraper_screenshots/`
- Database: `startup_swiper.db`
- Config: `.env`

---

**Ready to scrape!** 🚀

For full documentation, see `README.md`
