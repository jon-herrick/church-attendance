# Church Attendance — Pastoral Care Dashboard

## Scope

This project is a **pastoral care tool** for tracking congregation attendance and follow-up. It is strictly limited to:

- Attendance tracking and history
- Sunday scan simulation
- Visitor logging
- Follow-up list management for absent members

**Do not add** personal spiritual formation, devotional, or discipleship features here. Those belong in separate standalone projects.

## Project decisions

- Single-file static app (`index.html`) — no build step, no backend, no framework
- All data is in-memory (resets on page reload)
- Max-width 860px container, responsive via CSS Grid/Flexbox

## Save preferences

- Code context → this `CLAUDE.md`
- Higher-level project notes and decisions → Notion
