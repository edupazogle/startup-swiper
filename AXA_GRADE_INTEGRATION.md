# AXA Grade and Grade Explanation - Database Integration

## Summary
Successfully implemented and integrated `axa_grade` and `axa_grade_explanation` fields into the main database for platform use.

## Changes Made

### 1. Database Model Update
**File**: `api/models_startup.py`

Added two new columns to the `Startup` model:
```python
axa_grade = Column(String, index=True)
# AXA Partnership Grade (A+, A, A-, B+, B, B-, C+, C, C-, D, F)

axa_grade_explanation = Column(Text)
# Creative short phrase explaining the grade
```

### 2. Database Migration
**File**: `api/migrate_add_grade_fields.py`

Created migration script that:
- ✅ Adds `axa_grade` column (VARCHAR with index)
- ✅ Adds `axa_grade_explanation` column (TEXT)
- ✅ Creates index on `axa_grade` for fast filtering
- ✅ Handles multiple database locations

**Status**: Columns already exist in database - ready to use

### 3. Score Calculation Update
**File**: `evaluator/recalculate_scores.py`

Updated to generate and save both fields:
```python
grade, score, reasoning, grade_explanation = calculate_startup_grade(startup, verbose=args.verbose)

# Save to database
if not args.dry_run:
    startup.axa_overall_score = score
    startup.axa_grade = grade.value           # NEW
    startup.axa_grade_explanation = explanation  # NEW
```

### 4. Grade Explanation Function
**Location**: `evaluator/recalculate_scores.py` (lines 397-469)

Implemented `get_grade_explanation(grade, profile)` that returns:
- **5 options per grade** (randomizable)
- **Context-aware modifiers** based on startup profile
- **Examples**:
  - "Enterprise powerhouse" → A+
  - "Solid growth trajectory" → A
  - "Good partnership fit" → A-
  - "Workable solution (underfunded)" → B
  - "Early stage challenges" → C+

## Database Schema

### Startup Table (startups)
```sql
axa_grade VARCHAR (indexed)
  Values: A+, A, A-, B+, B, B-, C+, C, C-, D, F
  
axa_grade_explanation TEXT
  Values: Creative phrases like "Enterprise powerhouse", "Good partnership fit", etc.
```

## Data Flow

```
recalculate_scores.py
    ↓
calculate_startup_grade()
    ↓
get_grade_explanation()
    ↓
Startup Model
    ↓
axa_grade + axa_grade_explanation
    ↓
Database (startup_swiper.db)
```

## Platform Usage

The fields are now available for:
1. **Dashboard Display** - Show grades with creative explanations
2. **Filtering** - Filter by axa_grade (A, B, C, etc.)
3. **Sorting** - Sort by grade or create custom sorts
4. **Reporting** - Include in startup reports and exports
5. **API Endpoints** - Return grades in API responses

## TypeScript Types

Update in `app/startup-swipe-schedu/src/lib/types.ts`:
```typescript
interface Startup {
  // ... existing fields
  axa_grade?: string;           // "A+", "A", "B", etc.
  axa_grade_explanation?: string; // "Enterprise powerhouse", etc.
}
```

## Frontend Integration Examples

### Display in Dashboard
```tsx
{startup.axa_grade && (
  <div className="grade-section">
    <span className="grade-badge">{startup.axa_grade}</span>
    <p className="explanation">{startup.axa_grade_explanation}</p>
  </div>
)}
```

### Filter by Grade
```tsx
const gradeFilter = ['A+', 'A', 'A-']; // Premium grades
const filtered = startups.filter(s => gradeFilter.includes(s.axa_grade));
```

### Grade Badge Styling
```css
.grade-a-plus { background-color: #10b981; color: white; }  /* Green */
.grade-a      { background-color: #06b6d4; color: white; }  /* Cyan */
.grade-b-plus { background-color: #f59e0b; color: white; }  /* Amber */
.grade-c      { background-color: #ef4444; color: white; }  /* Red */
.grade-f      { background-color: #6b7280; color: white; }  /* Gray */
```

## Running Grade Recalculation

### Full Recalculation
```bash
python3 evaluator/recalculate_scores.py
```

### Preview Only (Dry Run)
```bash
python3 evaluator/recalculate_scores.py --dry-run
```

### Verbose Mode (See Reasoning)
```bash
python3 evaluator/recalculate_scores.py --verbose
```

### Limit for Testing
```bash
python3 evaluator/recalculate_scores.py --limit 50
```

### All Options
```bash
python3 evaluator/recalculate_scores.py \
  --limit 500 \
  --verbose \
  --dry-run
```

## Sample Data Output

After running recalculation:
```json
{
  "startup_id": 42,
  "startup_name": "Pandatron",
  "axa_grade": "B",
  "axa_grade_explanation": "Workable solution (underfunded)",
  "axa_overall_score": 75.5,
  "axa_priority_tier": "Tier 2: High Priority"
}
```

## API Endpoint Enhancement

Update API responses to include:
```python
@app.get("/api/startups/{id}")
def get_startup(id: int):
    startup = db.query(Startup).filter(Startup.id == id).first()
    return {
        "id": startup.id,
        "company_name": startup.company_name,
        "axa_overall_score": startup.axa_overall_score,
        "axa_grade": startup.axa_grade,           # NEW
        "axa_grade_explanation": startup.axa_grade_explanation,  # NEW
        # ... other fields
    }
```

## Grade Distribution (Example)

After processing:
```
A+  [████████░░░░░░░░░░░░░░░░░░░░]   12 startups (4.5%)
A   [████████████░░░░░░░░░░░░░░░░]   28 startups (10.5%)
A-  [██████████████░░░░░░░░░░░░░░]   35 startups (13.1%)
B+  [████████████████░░░░░░░░░░░░]   42 startups (15.7%)
B   [████████████████░░░░░░░░░░░░]   45 startups (16.8%)
B-  [██████████░░░░░░░░░░░░░░░░░░]   28 startups (10.5%)
C+  [████░░░░░░░░░░░░░░░░░░░░░░░░]   18 startups (6.7%)
C   [███░░░░░░░░░░░░░░░░░░░░░░░░░░]   14 startups (5.2%)
C-  [██░░░░░░░░░░░░░░░░░░░░░░░░░░░░]   10 startups (3.7%)
D   [█░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░]   4 startups (1.5%)
F   [░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░]   1 startup (0.4%)
```

## Files Modified Summary

| File | Change | Status |
|------|--------|--------|
| `api/models_startup.py` | Added axa_grade, axa_grade_explanation columns | ✅ Done |
| `evaluator/recalculate_scores.py` | Updated to generate and save both fields | ✅ Done |
| `api/migrate_add_grade_fields.py` | Created migration script | ✅ Done |
| `startup_swiper.db` | Added columns to table | ✅ Done |
| `app/startup-swipe-schedu/src/lib/types.ts` | Add types (TO DO) | ⏳ Pending |
| `app/startup-swipe-schedu/src/components/SwipeableCard.tsx` | Display grade explanation (TO DO) | ⏳ Pending |

## Next Steps for Frontend

1. Update TypeScript types to include new fields
2. Add grade badge component with explanation tooltip
3. Add filtering by grade in dashboard
4. Update API integration to fetch both fields
5. Add grade column to startup list view
6. Create grade-based color coding scheme

## Verification Commands

```bash
# Check database schema
python3 << 'EOF'
import sqlite3
conn = sqlite3.connect('startup_swiper.db')
cursor = conn.cursor()
cursor.execute("PRAGMA table_info(startups)")
for col in cursor.fetchall():
    if 'axa_grade' in col[1]:
        print(f"✅ {col[1]}: {col[2]}")
conn.close()
EOF

# Check a startup record
python3 << 'EOF'
from api.database import SessionLocal
from api.models_startup import Startup
db = SessionLocal()
s = db.query(Startup).filter(Startup.axa_grade.isnot(None)).first()
if s:
    print(f"✅ {s.company_name}: {s.axa_grade} - {s.axa_grade_explanation}")
db.close()
EOF
```

## Complete! 🎉

The grade and grade_explanation fields are now:
- ✅ In the database model
- ✅ In the actual database schema
- ✅ Generated by the recalculation script
- ✅ Saved to the database
- ⏳ Ready for platform integration
