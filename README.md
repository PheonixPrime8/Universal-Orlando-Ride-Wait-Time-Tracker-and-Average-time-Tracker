# Universal Orlando Ride Wait Time Tracker

Flask web app that pulls live ride wait times for all three Universal Orlando parks and stores history in SQLite to show both current and average waits.

## Features

- Current wait times across parks, lands, and rides
- Average wait times by park and ride
- Manual refresh route for live updates
- Local SQLite storage for history
- Park logo styling and wait-time severity colors

## Tech Stack

- Python 3.12+
- Flask
- Requests
- SQLite

## Setup

1. Create and activate a virtual environment (recommended):
   - Windows PowerShell:
     - `py -3.12 -m venv .venv`
     - `.venv\Scripts\Activate.ps1`
2. Install dependencies:
   - `py -3.12 -m pip install -r requirements.txt`

## Run

- Start the app:
  - `py -3.12 app.py`
- Open in browser:
  - `http://127.0.0.1:5000`

## Routes

- `/` - Current wait times
- `/averages` - Average wait times
- `/refresh` - Pull live data and redirect to home (rate-limited)

## Notes

- Debug mode is off by default; set `FLASK_DEBUG=1` to enable it locally.
- Local database files are intentionally ignored in git.
- Automatic background refresh runs every 10 minutes by default.

## Environment Variables

- `FLASK_DEBUG` (default: `0`)
- `PORT` (default: `5000`)
- `DB_NAME` (default: `wait_times.db`)
- `REFRESH_COOLDOWN_SECONDS` (default: `60`)
- `AUTO_REFRESH_INTERVAL_SECONDS` (default: `600`)
- `REQUEST_TIMEOUT_SECONDS` (default: `10`)
