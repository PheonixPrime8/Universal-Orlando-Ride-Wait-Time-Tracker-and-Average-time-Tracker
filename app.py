import logging
import os
import threading
import time
from flask import Flask, abort, render_template, redirect, url_for
from database import create_database, get_connection
from fetch_wait_times import fetch_and_save_wait_times
from config import (
    APP_PORT,
    AUTO_REFRESH_INTERVAL_SECONDS,
    FLASK_DEBUG,
    REFRESH_COOLDOWN_SECONDS,
)

app = Flask(__name__)
_last_refresh_ts = 0.0
_refresh_lock = threading.Lock()
_auto_refresh_stop_event = threading.Event()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
LOGGER = logging.getLogger(__name__)


def fetch_wait_times_safe(source):
    with _refresh_lock:
        try:
            fetch_and_save_wait_times()
            LOGGER.info("Wait times refreshed (%s).", source)
            return True
        except Exception as error:
            LOGGER.exception("Wait time refresh failed (%s): %s", source, error)
            return False


def get_last_updated_timestamp():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(recorded_at) FROM wait_times")
        row = cursor.fetchone()
    return row[0] if row and row[0] else "No data yet"


def _auto_refresh_worker():
    while not _auto_refresh_stop_event.wait(AUTO_REFRESH_INTERVAL_SECONDS):
        fetch_wait_times_safe("auto-refresh")


@app.route("/")
def index():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        SELECT
            r.park_name,
            r.land_name,
            r.ride_name,
            w.wait_time,
            w.is_open,
            w.recorded_at
        FROM wait_times w
        JOIN rides r ON w.ride_id = r.ride_id
        WHERE w.id IN (
            SELECT MAX(id)
            FROM wait_times
            GROUP BY ride_id
        )
        ORDER BY r.park_name, r.land_name, r.ride_name
        """)
        rides = cursor.fetchall()

    return render_template("index.html", rides=rides, last_updated=get_last_updated_timestamp())


@app.route("/averages")
def averages():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        SELECT
            r.park_name,
            r.ride_name,
            ROUND(AVG(w.wait_time), 1) AS average_wait
        FROM wait_times w
        JOIN rides r ON w.ride_id = r.ride_id
        WHERE w.is_open = 1
        GROUP BY r.park_name, r.ride_name
        ORDER BY r.park_name, average_wait DESC
        """)
        averages = cursor.fetchall()

    return render_template(
        "averages.html",
        averages=averages,
        last_updated=get_last_updated_timestamp(),
    )


@app.route("/refresh")
def refresh():
    global _last_refresh_ts
    now = time.time()
    if now - _last_refresh_ts < REFRESH_COOLDOWN_SECONDS:
        abort(429, description="Refresh is rate-limited. Please wait a minute.")

    fetch_wait_times_safe("manual-refresh")
    _last_refresh_ts = now
    return redirect(url_for("index"))


@app.errorhandler(429)
def too_many_requests(error):
    return (
        render_template(
            "429.html",
            message=getattr(error, "description", "Please wait before refreshing again."),
            retry_after=REFRESH_COOLDOWN_SECONDS,
        ),
        429,
    )


@app.errorhandler(500)
def internal_server_error(_error):
    return (
        render_template(
            "500.html",
            message="Something went wrong while loading data. Please try again shortly.",
        ),
        500,
    )


if __name__ == "__main__":
    create_database()
    fetch_wait_times_safe("startup")

    if not FLASK_DEBUG or os.getenv("WERKZEUG_RUN_MAIN") == "true":
        threading.Thread(target=_auto_refresh_worker, daemon=True).start()
        LOGGER.info(
            "Auto-refresh enabled every %s seconds.",
            AUTO_REFRESH_INTERVAL_SECONDS,
        )

    app.run(debug=FLASK_DEBUG, port=APP_PORT)
