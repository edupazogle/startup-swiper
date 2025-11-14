# 🚀 Quick Start - Enriched Data API

## 1. Start the API

```bash
cd /home/akyo/startup_swiper
source .venv/bin/activate
uvicorn api/main:app --host 0.0.0.0 --port 8000
```

## 2. Test Endpoints

### Get Stats
```bash
curl http://localhost:8000/startups/enrichment/stats
```

### Search by Technology
```bash
curl -X POST http://localhost:8000/startups/enrichment/by-name \
  -H "Content-Type: application/json" \
  -d '{
    "field_name": "tech",
    "field_value": "React",
    "limit": 10
  }'
```

### Get Startup Details
```bash
curl http://localhost:8000/startups/759_studio/enrichment
```

### Search Enriched Startups
```bash
curl "http://localhost:8000/startups/enriched/search?enrichment_type=tech_stack&limit=5"
```

## 3. View Documentation
- Full Guide: `ENRICHED_DATA_GUIDE.md`
- Status: `ENRICHMENT_COMPLETE.md`
- Examples: `api/enriched_data_examples.py`

## 4. Run Tests
```bash
python3 test_enriched_api.py
```

## 5. Expand Enrichment (Optional)
```bash
# Enrich more startups
python3 api/enrichment_coordinator.py --enrich-all --workers 3 --delay 0.5
```

## Current Status
- **Total Startups**: 4,374
- **Enriched**: 100 (2.3%)
- **With Emails**: 32
- **With Tech Stack**: 49
- **With Social Media**: 50
- **With Team Info**: 16

## API Endpoints
- `GET /startups/enrichment/stats` - Statistics
- `GET /startups/enriched/search` - Search
- `GET /startups/{id}/enrichment` - Details
- `POST /startups/enrichment/by-name` - Field search

Ready to go! 🎉
