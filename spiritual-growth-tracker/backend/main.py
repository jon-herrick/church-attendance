import pathlib
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

load_dotenv()

from notion_service import NotionService  # noqa: E402 — import after dotenv


notion: NotionService | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global notion
    notion = NotionService()
    yield


app = FastAPI(lifespan=lifespan)


# ── Pydantic models ───────────────────────────────────────────────────────────


class WeekEntry(BaseModel):
    weekDate: str
    abidingScore: float | None = None
    reflection: str | None = None
    intentions: list[str] = []
    # habits
    prayer: float | None = None
    scripture: float | None = None
    worship: float | None = None
    fellowship: float | None = None
    service: float | None = None
    fasting: float | None = None
    journaling: float | None = None
    # fruits
    love: float | None = None
    joy: float | None = None
    peace: float | None = None
    patience: float | None = None
    kindness: float | None = None
    goodness: float | None = None
    faithfulness: float | None = None
    gentleness: float | None = None
    selfControl: float | None = None


class PruningArea(BaseModel):
    area: str
    status: str = "active"
    notes: str = ""
    startDate: str | None = None


class PruningStatusUpdate(BaseModel):
    status: str
    notes: str | None = None


# ── API routes ────────────────────────────────────────────────────────────────


@app.get("/api/weeks")
def get_weeks():
    try:
        return notion.get_all_weeks()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/weeks")
def save_week(entry: WeekEntry):
    try:
        return notion.upsert_week(entry.model_dump())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/pruning")
def get_pruning():
    try:
        return notion.get_all_pruning()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/pruning")
def create_pruning(area: PruningArea):
    try:
        return notion.create_pruning_area(area.model_dump())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.patch("/api/pruning/{page_id}")
def update_pruning(page_id: str, update: PruningStatusUpdate):
    try:
        return notion.update_pruning_status(page_id, update.status, update.notes)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Static files (must come last) ─────────────────────────────────────────────

frontend_dir = pathlib.Path(__file__).parent.parent / "frontend"
app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="static")
