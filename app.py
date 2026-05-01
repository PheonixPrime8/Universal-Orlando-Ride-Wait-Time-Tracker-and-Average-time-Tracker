import os
import time
from flask import Flask, abort, render_template, redirect, url_for
from database import create_database, get_connection
from fetch_wait_times import fetch_and_save_wait_times

app = Flask(__name__)
REFRESH_COOLDOWN_SECONDS = 60
_last_refresh_ts = 0.0


@app.route("/")
def index():
    conn = get_connection()
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
    conn.close()

    return render_template("index.html", rides=rides)


@app.route("/averages")
def averages():
    conn = get_connection()
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
    conn.close()

    return render_template("averages.html", averages=averages)


@app.route("/refresh")
def refresh():
    global _last_refresh_ts
    now = time.time()
    if now - _last_refresh_ts < REFRESH_COOLDOWN_SECONDS:
        abort(429, description="Refresh is rate-limited. Please wait a minute.")

    fetch_and_save_wait_times()
    _last_refresh_ts = now
    return redirect(url_for("index"))


if __name__ == "__main__":
    create_database()
    fetch_and_save_wait_times()
    # Default to safe settings; enable debug only when explicitly requested.
    app.run(debug=os.getenv("FLASK_DEBUG", "0") == "1")
