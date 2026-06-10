# Spiritual Growth Tracker

## Project context
- **Context**: Personal
- **Notion project page**: https://app.notion.com/p/37547f7425dd8172b6dedee7866aa92c

## Scope
Personal spiritual fruitfulness scorecard and reflection dashboard based on John 15.

**This project IS:**
- Weekly spiritual intention logging
- Spiritual habit tracking (prayer, scripture, worship, fellowship, service, fasting, journaling)
- Fruits of the Spirit self-assessment (Gal 5:22-23)
- Abiding score + reflection journal
- Pruning areas lifecycle tracker (active → growing → pruned)
- Progress charts and habit/abiding correlation

**This project is NOT:**
- A congregational or pastoral care tool (that's church-attendance)
- A multi-tenant SaaS product (single-user for now)
- A devotional content app

## Tech stack
- **Frontend**: Vanilla HTML/CSS/JS (`frontend/index.html`)
- **Backend**: Python FastAPI (`backend/main.py`) — thin proxy, keeps Notion API key server-side
- **Database**: Notion (two databases, both under the Notion project page above)
  - Weekly Entries DB: `7086a5ba-dcd1-4a68-90a0-d48853b1ddeb`
  - Pruning Areas DB:  `d56754d1-cb23-4c7d-82b2-41906c405ba7`

## Running locally
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env   # then add your NOTION_API_KEY
uvicorn main:app --reload
# Open http://localhost:8000
```

## Save preferences
- Code context → this `CLAUDE.md`
- Higher-level decisions and project notes → Notion (see project page above)

## Kickoff decisions (recorded)
- Standalone repo: yes
- Could be shared later: yes (authentication not yet implemented)
- Database: Notion
- Backend: Python FastAPI
