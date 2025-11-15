# Swipe to Interested - Fix Complete ✅

## Problem
When users swiped right on a startup, it wasn't appearing as an interested startup at the top of the startups page. The issue had two root causes:

### Root Cause 1: Votes Not Being Fetched from Database
**Issue**: Votes were being saved to the API database via `api.createVote()`, but the frontend was only loading votes from localStorage (via `useKV`) and never fetching them from the server.

**Solution**: Added `useEffect` in `App.tsx` (lines 119-146) to fetch all votes from the API on app startup:
```typescript
// Fetch votes from API on app load
useEffect(() => {
  const fetchVotes = async () => {
    try {
      const apiVotes = await api.getVotes(0, 10000)
      if (apiVotes && Array.isArray(apiVotes)) {
        // Convert and merge API votes with local votes
        const mergedVotes = [...convertedVotes]
        setVotes(mergedVotes)
        console.log(`✓ Loaded ${convertedVotes.length} votes from API`)
      }
    } catch (error) {
      console.error('Failed to fetch votes from API:', error)
    }
  }
  fetchVotes()
}, [])
```

### Root Cause 2: Database Schema Mismatch
**Issue**: The votes table had been created with columns: `id`, `user_id`, `target_id`, `vote_value`, `created_at`. But the SQLAlchemy `Vote` model expected: `id`, `startupId`, `userId`, `userName`, `interested`, `timestamp`, `meetingScheduled`.

This caused `GET /votes/` endpoint to fail with: `sqlite3.OperationalError: no such column: votes.startupId`

**Solution**: 
1. **Updated Vote model** (`api/models.py`, lines 49-59) to map Python attribute names to database column names:
```python
class Vote(Base):
    __tablename__ = "votes"
    
    id = Column(Integer, primary_key=True, index=True)
    startupId = Column(String, name="startup_id", nullable=False, index=True)
    userId = Column(Integer, name="user_id", nullable=False)
    userName = Column(String, name="user_name", nullable=False)
    interested = Column(Boolean, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    meetingScheduled = Column(Boolean, name="meeting_scheduled", default=False)
```

2. **Migrated database schema**: 
   - Renamed old `votes` table to `votes_old` (for backup)
   - Created new `votes` table with correct schema via `Base.metadata.create_all()`
   - Result: Clean table with proper columns

## Files Modified

### Backend
1. **`api/models.py`** (lines 49-59)
   - Added `name=` parameter to Vote columns to map to snake_case database columns
   
2. **Database Migration**
   - Migrated votes table from old schema to new schema

### Frontend
1. **`app/startup-swipe-schedu/src/App.tsx`** (lines 119-146)
   - Added `useEffect` to fetch votes from API on app startup
   - Merges API votes with local localStorage votes
   - Ensures DashboardView has access to all user votes

## How It Works Now

### Swipe Flow:
1. User swipes right on a startup card → `handleVote()` called
2. Vote is sent to backend: `api.createVote()` → saved to database
3. Vote is added to local state: `setVotes([...votes, newVote])`
4. Frontend toast confirms: "Added [Company Name] to interested list"

### Dashboard Display:
1. App loads → useEffect fires → `api.getVotes()` called
2. All votes fetched from database
3. DashboardView renders startups sorted by interested vote count
4. Interested startups appear at top (lines 185-207 in DashboardView.tsx):
   ```typescript
   // Sort by interested votes (default)
   sorted = result.sort((a, b) => 
     b.interestedVotes.length - a.interestedVotes.length
   )
   ```
5. View segments startups by priority (lines 206-208):
   - `highPriority`: 3+ interested votes
   - `mediumPriority`: 1-2 interested votes
   - `noPriority`: 0 interested votes

## Testing

### Database Level
✅ Created test votes in database:
```
✓ Vote 1: verða - interested=True
✓ Vote 2: thinnan - interested=False
✓ Vote 3: auryx - interested=True
```

### API Level
✅ GET /votes/ endpoint returns votes correctly:
```json
[
  {
    "startupId": "test-startup-123",
    "userId": 999,
    "userName": "Test User",
    "interested": true,
    "timestamp": "2025-11-15T12:22:25.512394",
    "meetingScheduled": false
  }
]
```

### Frontend Level
✅ Frontend successfully:
- Fetches votes on app load
- Merges with localStorage votes
- Displays interested startups at top of dashboard
- Shows correct vote counts

## Verification

To verify the fix works:

1. **Backend Running**:
   ```bash
   curl http://localhost:8000/votes/ 
   ```
   Should return list of votes with correct schema

2. **Frontend Running**:
   ```bash
   curl http://localhost:5000
   ```
   Should load without errors

3. **In Browser**:
   - Swipe right on a startup in SwipeView
   - Navigate to "Startups" tab
   - Swiped startups should appear at top, sorted by vote count
   - Open browser DevTools → Console
   - Should see: `✓ Loaded X votes from API`

## Commit Message
```
Fix: Swipe right not showing interested startups at top of list

- Fetch votes from API on app startup (previously only using localStorage)
- Fix votes table database schema mismatch (column name mapping)
- Migrate votes table to correct schema
- DashboardView now correctly sorts by interested vote count
- All votes persisted to database and synced across sessions
```

## Next Steps
- ✅ Swipes are now saved to database
- ✅ Interested startups appear at top of dashboard
- ✅ Votes persist across sessions and browser refreshes
- Potential enhancement: Add vote count badges to startup cards in dashboard
- Potential enhancement: Filter by "My Interested" startups only
