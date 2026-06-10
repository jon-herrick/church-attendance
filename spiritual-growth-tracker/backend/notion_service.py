import json
import os
from notion_client import Client

HABIT_PROPS = {
    "prayer": "Prayer Days",
    "scripture": "Scripture Days",
    "worship": "Worship Days",
    "fellowship": "Fellowship Days",
    "service": "Service Days",
    "fasting": "Fasting Days",
    "journaling": "Journaling Days",
}

FRUIT_PROPS = {
    "love": "Love",
    "joy": "Joy",
    "peace": "Peace",
    "patience": "Patience",
    "kindness": "Kindness",
    "goodness": "Goodness",
    "faithfulness": "Faithfulness",
    "gentleness": "Gentleness",
    "selfControl": "Self-Control",
}


class NotionService:
    def __init__(self):
        self.client = Client(auth=os.environ["NOTION_API_KEY"])
        self.weeks_db = os.environ["NOTION_WEEKS_DB_ID"]
        self.pruning_db = os.environ["NOTION_PRUNING_DB_ID"]

    # ── helpers ──────────────────────────────────────────────────────────────

    def _rich_text(self, text: str) -> list:
        return [{"type": "text", "text": {"content": str(text)}}]

    def _get_rich_text(self, prop) -> str:
        items = prop.get("rich_text", [])
        return items[0]["plain_text"] if items else ""

    def _get_title(self, prop) -> str:
        items = prop.get("title", [])
        return items[0]["plain_text"] if items else ""

    def _get_number(self, prop) -> float | None:
        return prop.get("number")

    def _get_select(self, prop) -> str:
        sel = prop.get("select")
        return sel["name"] if sel else ""

    def _get_date(self, prop) -> str:
        d = prop.get("date")
        return d["start"] if d else ""

    def _parse_week_page(self, page: dict) -> dict:
        props = page["properties"]
        entry = {
            "pageId": page["id"],
            "weekDate": self._get_title(props.get("Week Date", {})),
            "abidingScore": self._get_number(props.get("Abiding Score", {})),
            "reflection": self._get_rich_text(props.get("Reflection", {})),
            "intentions": [],
        }
        raw_intentions = self._get_rich_text(props.get("Intentions JSON", {}))
        if raw_intentions:
            try:
                entry["intentions"] = json.loads(raw_intentions)
            except json.JSONDecodeError:
                pass
        for key, notion_name in HABIT_PROPS.items():
            entry[key] = self._get_number(props.get(notion_name, {}))
        for key, notion_name in FRUIT_PROPS.items():
            entry[key] = self._get_number(props.get(notion_name, {}))
        return entry

    def _parse_pruning_page(self, page: dict) -> dict:
        props = page["properties"]
        return {
            "pageId": page["id"],
            "area": self._get_title(props.get("Area", {})),
            "status": self._get_select(props.get("Status", {})),
            "notes": self._get_rich_text(props.get("Notes", {})),
            "startDate": self._get_date(props.get("Start Date", {})),
        }

    # ── weeks ─────────────────────────────────────────────────────────────────

    def get_all_weeks(self) -> list:
        results = []
        cursor = None
        while True:
            kwargs = {
                "database_id": self.weeks_db,
                "sorts": [{"property": "Week Date", "direction": "descending"}],
            }
            if cursor:
                kwargs["start_cursor"] = cursor
            resp = self.client.databases.query(**kwargs)
            results.extend(self._parse_week_page(p) for p in resp["results"])
            if not resp.get("has_more"):
                break
            cursor = resp["next_cursor"]
        return results

    def upsert_week(self, entry: dict) -> dict:
        week_date = entry["weekDate"]
        resp = self.client.databases.query(
            database_id=self.weeks_db,
            filter={"property": "Week Date", "title": {"equals": week_date}},
        )
        properties = {
            "Week Date": {"title": self._rich_text(week_date)},
            "Abiding Score": {"number": entry.get("abidingScore")},
            "Reflection": {"rich_text": self._rich_text(entry.get("reflection", ""))},
            "Intentions JSON": {
                "rich_text": self._rich_text(
                    json.dumps(entry.get("intentions", []))
                )
            },
        }
        for key, notion_name in HABIT_PROPS.items():
            properties[notion_name] = {"number": entry.get(key)}
        for key, notion_name in FRUIT_PROPS.items():
            properties[notion_name] = {"number": entry.get(key)}

        if resp["results"]:
            page_id = resp["results"][0]["id"]
            page = self.client.pages.update(page_id=page_id, properties=properties)
        else:
            page = self.client.pages.create(
                parent={"database_id": self.weeks_db},
                properties=properties,
            )
        return self._parse_week_page(page)

    # ── pruning ───────────────────────────────────────────────────────────────

    def get_all_pruning(self) -> list:
        results = []
        cursor = None
        while True:
            kwargs = {"database_id": self.pruning_db}
            if cursor:
                kwargs["start_cursor"] = cursor
            resp = self.client.databases.query(**kwargs)
            results.extend(self._parse_pruning_page(p) for p in resp["results"])
            if not resp.get("has_more"):
                break
            cursor = resp["next_cursor"]
        return results

    def create_pruning_area(self, data: dict) -> dict:
        properties = {
            "Area": {"title": self._rich_text(data["area"])},
            "Status": {"select": {"name": data.get("status", "active")}},
            "Notes": {"rich_text": self._rich_text(data.get("notes", ""))},
        }
        if data.get("startDate"):
            properties["Start Date"] = {"date": {"start": data["startDate"]}}
        page = self.client.pages.create(
            parent={"database_id": self.pruning_db},
            properties=properties,
        )
        return self._parse_pruning_page(page)

    def update_pruning_status(self, page_id: str, status: str, notes: str) -> dict:
        properties = {"Status": {"select": {"name": status}}}
        if notes is not None:
            properties["Notes"] = {"rich_text": self._rich_text(notes)}
        page = self.client.pages.update(page_id=page_id, properties=properties)
        return self._parse_pruning_page(page)
