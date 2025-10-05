# TimeTable Scraper

A robust, automated tool for extracting, parsing, and displaying university class schedules directly from Gmail. Designed for reliability, configurability, and beautiful output.

---

## Features

- **Automated Gmail scraping** for schedule emails (configurable query, robust OAuth2 flow)
- **HTML and plain text parsing** (tolerant to odd formats)
- **Configurable semester filtering** (via `.env` or environment variables)
- **Nightly scheduling** (using APScheduler)
- **Rich, beautiful CLI output** (tables, logs)
- **Health checks and config info**
- **JSON output for further use**

---

## Libraries Used

- `google-api-python-client`, `google-auth-httplib2`, `google-auth-oauthlib` – Gmail API access
- `beautifulsoup4`, `lxml` – HTML parsing
- `python-dotenv` – Environment/config loading
- `pydantic` – Type-safe config
- `APScheduler` – Scheduling
- `rich` – Beautiful CLI output/logging
- `python-dateutil` – Date/time handling
- `requests`, `urllib3` – HTTP utilities

---

## Project Structure

```
requirements.txt
stuff.txt
credentials/
    client_secret.json
src/
    scraper/
        main.py           # CLI entrypoint
        config.py         # Loads settings from .env
        gmail_client.py   # Gmail API logic
        parser.py         # Schedule parsing
        scheduler.py      # Nightly job logic
    utils/
        logging_config.py # Rich logging setup
        table_formatter.py# Table display for JSON
    ...
data/
    cache/
        schedule_YYYY-MM-DD.json
        last_checked.json
```

---

## Setup Instructions (A-Z)

### 1. Clone & Install

```sh
# Clone the repo
# cd timetable_scraper_scaffold
python -m venv .venv
.venv\Scripts\activate  # On Windows
pip install -r requirements.txt
```

### 2. Google API Credentials

- Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
- Create OAuth 2.0 Client ID (Desktop)
- Download `client_secret.json` and place in `credentials/client_secret.json`

### 3. Configure Environment

Create a `.env` file in the root (see `.env.example` if present):

```
TZ=Asia/Karachi
GMAIL_QUERY_BASE=subject:("Class Schedule" OR schedule) in:inbox
CHECK_HOUR_LOCAL=23
CHECK_MINUTE_LOCAL=0
NEWER_THAN_DAYS=2
ALLOWED_SEMESTERS=BS (SE) - 5C, BS (CS) - 7A
```

- Adjust semesters, timezone, etc. as needed.

### 4. First Run & Authentication

```sh
python -m src.scraper.main --once
```
- On first run, browser will open for Gmail OAuth. Approve access.
- Token is saved as `token.json` for future runs.

### 5. Nightly Scheduler (Background)

```sh
python -m src.scraper.main --run-scheduler
```
- Runs every night at configured time, saves JSON to `data/cache/`

### 6. Display JSON as Table

```sh
python -m src.scraper.main --show-json data/cache/schedule_YYYY-MM-DD.json
```

### 7. Health Check & Config Info

```sh
python -m src.scraper.main --health-check
python -m src.scraper.main --config-info
```

---

## How It Works

1. **Scheduler** triggers at night (or run manually)
2. **Gmail Client** fetches latest schedule email
3. **Parser** extracts schedule rows for allowed semesters
4. **Output** is saved as JSON and can be displayed as a table
5. **Logs** and errors are shown with rich formatting

---

## Troubleshooting

- **OAuth issues:** Delete `token.json` and re-run for fresh auth
- **No schedule found:** Check Gmail query and semester config
- **Parsing errors:** Adjust `ALLOWED_SEMESTERS` or parsing settings in `.env`
- **Scheduler not running:** Ensure time zone and hour/minute are correct

---

## Contributing

- Fork, branch, and PR as usual
- Add tests if possible

---

## Credits

- Built with ❤️ using Python, Google APIs, and open-source libraries
