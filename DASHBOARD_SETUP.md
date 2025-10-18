# Dashboard Setup Instructions

## Overview
Your wild west themed dashboard is ready! This includes:
- **Morning Brief** overlay (shows automatically on page load)
- **EOD Report** overlay (accessible via button)
- **Historical Briefs** tab for past reports
- **Live Portfolio Dashboard** with wild west styling
- **Supabase Integration** for storing briefs

## Database Setup

### 1. Run the Migration
First, apply the briefs table migration:

```bash
cd kopitiam-kapital
# If using Supabase CLI
supabase db push

# Or run the migration manually via Supabase dashboard
# Copy content from: supabase/migrations/20250118000000_create_briefs.sql
```

### 2. Seed Sample Data
To populate the database with sample briefs:

```bash
cd apps/web
npm install tsx --save-dev
npx tsx scripts/seed-briefs.ts
```

Or manually via API:
```bash
curl -X POST http://localhost:3000/api/briefs \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "YOUR_USER_ID",
    "type": "morning",
    "date": "2025-01-18",
    "content": {
      "summary": "Your brief summary...",
      "market_overview": "Market analysis...",
      "key_points": ["Point 1", "Point 2"],
      "recommendations": ["Rec 1"]
    }
  }'
```

## Features

### Morning Brief Overlay
- **Auto-shows on page load** (after a small delay)
- Displays:
  - Daily market summary
  - Market overview
  - Key points to watch
  - AI-generated trading opportunities
- Wild west theme with golden sunrise colors
- Re-accessible via header button: ☀️ Morning Brief

### EOD Report Overlay
- Accessible via header button: 🌙 EOD Report
- Displays:
  - Daily portfolio summary
  - Market close analysis
  - Key points from the day
  - Portfolio P&L breakdown
- Dark theme with evening colors

### History Tab
- View all past morning briefs and EOD reports
- Click any historical brief to view in overlay
- Shows last 30 days of briefs
- Sorted by date (newest first)

### Dashboard Tab
- **Portfolio Overview**: Total value, daily P&L, open positions
- **Active Positions**: Real-time position tracking with P&L
- **Today's Opportunities**: AI-generated trading ideas
- Wild west theme throughout with:
  - Wood texture overlays
  - Brown/tan color palette
  - Western-style fonts (Bowlby One)
  - Cowboy emoji in corner 🤠

## Dummy Data
The dashboard currently shows dummy data if:
- No user ID is found in localStorage
- API calls fail
- Database is not set up

This allows you to preview the design immediately without setup.

## API Endpoints

### GET /api/briefs
Fetch briefs for a user:
```bash
GET /api/briefs?userId=USER_ID_HERE
```

Returns:
```json
{
  "morningBrief": { ... },
  "eodBrief": { ... },
  "historical": [ ... ]
}
```

### POST /api/briefs
Create or update a brief:
```bash
POST /api/briefs
Content-Type: application/json

{
  "userId": "USER_ID",
  "type": "morning", // or "eod"
  "date": "2025-01-18",
  "content": {
    "summary": "Brief summary...",
    "market_overview": "Market analysis...",
    "key_points": ["Point 1", "Point 2"],
    "recommendations": ["Rec 1"] // optional, for morning briefs
    "portfolio_summary": { ... } // optional, for EOD reports
  }
}
```

## Environment Variables
Make sure these are set in your `.env.local`:

```bash
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
```

## Integration with AI Agent
To have your AI agent generate briefs:

1. Call the POST endpoint from your Python AI service
2. Generate content using your LLM
3. Store in Supabase via the API
4. Frontend automatically fetches and displays

Example integration:
```python
import requests

def create_morning_brief(user_id: str, date: str):
    # Generate content with your AI
    content = generate_brief_content()
    
    # Store via API
    response = requests.post(
        'http://localhost:3000/api/briefs',
        json={
            'userId': user_id,
            'type': 'morning',
            'date': date,
            'content': content
        }
    )
    return response.json()
```

## Styling Notes
All styling follows the wild west theme from your onboarding page:
- Background: Cream/tan gradients (#FFF8DC, #FFE4B5, #FFDAB9)
- Accents: Brown tones (#CD853F, #D2691E, #8B4513)
- Morning briefs: Golden/orange (#FFD700, #FFA500)
- EOD reports: Dark gray/blue (#2C3E50, #4A5568)
- Font: Bowlby One for headers, Inter for body

## Troubleshooting

### Morning brief not showing on load
- Check browser console for errors
- Verify user ID exists in localStorage
- Check if brief data is being fetched

### Database errors
- Verify migration was applied
- Check Supabase dashboard for table structure
- Ensure environment variables are correct

### Styling issues
- Make sure Bowlby One font is loaded in layout.tsx
- Check Tailwind config includes custom colors
- Verify framer-motion is installed

## Next Steps
1. Connect to your Python AI service
2. Schedule morning brief generation (7 AM daily)
3. Schedule EOD report generation (5 PM daily)
4. Add audio briefing functionality
5. Add push notifications for briefs

