# Workflow

1) Nightly check (23:00 Asia/Karachi, configurable)
   - Determine 'tomorrow' (weekday name).
   - Build Gmail query to fetch only recent messages (e.g., newer_than:1d or 2d).

2) Gmail fetch (recent-only)
   - Query subjects like "Class Schedule for Monday/Tuesday/..."
   - Prefer the latest message only.
   - Download/parse HTML body.

3) Parsing
   - Extract only the rows/lines matching configured semesters (e.g., BSSE-5C).
   - Normalize fields: course code/title, time, room, instructor.

4) Output
   - Save JSON under data/cache/schedule_YYYY-MM-DD.json
   - Update data/cache/last_checked.json with metadata (messageId, time checked).

5) Frontend (next phase)
   - A tiny API or static JSON feed the React UI can read.