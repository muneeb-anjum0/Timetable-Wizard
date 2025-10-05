"""
APScheduler job that runs nightly at configured local time.
"""
import json
import logging
import os
from datetime import datetime, timedelta
from typing import Dict

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from dateutil import tz

from .gmail_client import get_credentials, build_service, list_messages, get_message_html
from .parser import parse_schedule_html

LOGGER = logging.getLogger(__name__)

WEEKDAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

def _target_day_name(now_local: datetime) -> str:
    # Use the current local day name (previous behaviour looked for 'tomorrow')
    return WEEKDAY_NAMES[now_local.weekday()]

def _build_query(base: str, day_name: str, newer_than_days: int) -> str:
    return f'{base} "for {day_name}" newer_than:{newer_than_days}d -in:trash'

def _save_json(doc: Dict, folder: str = "data/cache") -> str:
    os.makedirs(folder, exist_ok=True)
    date_str = doc.get("for_date") or datetime.now().date().isoformat()
    path = os.path.join(folder, f"schedule_{date_str}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=2, ensure_ascii=False)
    meta_path = os.path.join(folder, "last_checked.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "last_message_id": doc.get("message_id"),
                "last_run_at": datetime.utcnow().isoformat() + "Z",
                "query_used": doc.get("query"),
                "for_day": doc.get("for_day"),
                "for_date": doc.get("for_date"),
                "items_found": len(doc.get("items", [])),
            },
            f,
            indent=2,
            ensure_ascii=False,
        )
    return path

def run_once(user_email: str = "me", show_table: bool = False) -> Dict:
    # Import here to ensure config is loaded first
    from .config import settings
    
    local_tz = tz.gettz(settings.tz)
    now_local = datetime.now(tz=local_tz)
    for_day_name = _target_day_name(now_local)

    query = _build_query(settings.gmail_query_base, for_day_name, settings.newer_than_days)

    LOGGER.info("[bold]Looking for:[/bold] %s  (local: %s)", for_day_name, now_local.strftime("%Y-%m-%d %H:%M"))
    LOGGER.info("[bold]Gmail query:[/bold] %s", query)
    LOGGER.info("[bold]Semesters filter:[/bold] %s", settings.allowed_semesters)
    LOGGER.info("[bold]Settings timezone:[/bold] %s", settings.tz)
    LOGGER.info("[bold]Newer than days:[/bold] %s", settings.newer_than_days)

    creds = get_credentials()
    service = build_service(creds)

    msgs = list_messages(service, user_id=user_email, query=query, max_results=5)
    if not msgs:
        LOGGER.warning("No messages matched the query.")
        doc = {
            "for_day": for_day_name,
            "for_date": now_local.date().isoformat(),
            "query": query,
            "message_id": None,
            "items": [],
            "semesters": settings.allowed_semesters,
            "summary": {
                "total_items": 0,
                "semester_breakdown": {},
                "unique_courses": 0,
                "unique_faculty": 0,
            }
        }
        _save_json(doc)
        return doc

    msg_id = msgs[0]["id"]
    html = get_message_html(service, user_id=user_email, msg_id=msg_id) or ""
    
    LOGGER.info(f"Message ID: {msg_id}")
    LOGGER.info(f"HTML length: {len(html)} characters")
    if html:
        # Show first 500 characters of HTML for debugging
        preview = html[:500].replace('\n', '\\n').replace('\r', '\\r')
        LOGGER.info(f"HTML preview: {preview}...")
    else:
        LOGGER.warning("HTML content is empty or None")

    items = parse_schedule_html(html, settings.allowed_semesters)

    # Create summary statistics
    semester_counts = {}
    for item in items:
        sem = item.get('semester', 'Unknown')
        semester_counts[sem] = semester_counts.get(sem, 0) + 1

    doc = {
        "for_day": for_day_name,
        "for_date": now_local.date().isoformat(),
        "query": query,
        "message_id": msg_id,
        "items": items,
        "semesters": settings.allowed_semesters,
        "summary": {
            "total_items": len(items),
            "semester_breakdown": semester_counts,
            "unique_courses": len(set(item.get('course') for item in items if item.get('course'))),
            "unique_faculty": len(set(item.get('faculty') for item in items if item.get('faculty'))),
        }
    }
    saved = _save_json(doc)
    LOGGER.info("Saved parsed schedule → %s", saved)
    
    # Log summary
    summary = doc.get("summary", {})
    LOGGER.info(f"[bold green]Summary:[/bold green] {summary['total_items']} total items found")
    if summary.get("semester_breakdown"):
        for sem, count in summary["semester_breakdown"].items():
            LOGGER.info(f"  • {sem}: {count} classes")
    LOGGER.info(f"  • {summary['unique_courses']} unique courses, {summary['unique_faculty']} faculty members")
    
    # Display table if requested
    if show_table:
        from ..utils.table_formatter import format_schedule_json
        print()  # Add some spacing
        format_schedule_json(saved)
    
    return doc

def start_scheduler() -> BackgroundScheduler:
    from .config import settings
    
    local_tz = tz.gettz(settings.tz)
    scheduler = BackgroundScheduler(timezone=local_tz)

    trigger = CronTrigger(
        hour=settings.check_hour_local,
        minute=settings.check_minute_local,
        timezone=local_tz,
    )

    scheduler.add_job(
        func=run_once,
        trigger=trigger,
        id="nightly_scrape",
        max_instances=1,
        replace_existing=True,
        kwargs={"user_email": "me"},
    )

    scheduler.start()
    LOGGER.info(
        "Scheduler started. Will run nightly at %02d:%02d (%s).",
        settings.check_hour_local,
        settings.check_minute_local,
        settings.tz,
    )
    return scheduler
