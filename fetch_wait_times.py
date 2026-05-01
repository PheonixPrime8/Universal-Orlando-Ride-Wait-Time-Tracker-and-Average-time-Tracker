import requests
from datetime import datetime
import logging
from database import get_connection
from config import REQUEST_TIMEOUT_SECONDS

LOGGER = logging.getLogger(__name__)

PARKS = {
    "Islands of Adventure": 64,
    "Universal Studios Florida": 65,
    "Epic Universe": 334
}


def fetch_and_save_wait_times():
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with get_connection() as conn:
        cursor = conn.cursor()

        for park_name, park_id in PARKS.items():
            url = f"https://queue-times.com/parks/{park_id}/queue_times.json"

            try:
                response = requests.get(url, timeout=REQUEST_TIMEOUT_SECONDS)
                response.raise_for_status()
                data = response.json()

                for land in data.get("lands", []):
                    land_name = land.get("name", "Unknown Land")

                    for ride in land.get("rides", []):
                        ride_id = ride.get("id")
                        ride_name = ride.get("name")
                        if ride_id is None or ride_name is None:
                            continue

                        wait_time_raw = ride.get("wait_time", 0)
                        if isinstance(wait_time_raw, int) and wait_time_raw >= 0:
                            wait_time = wait_time_raw
                        else:
                            wait_time = 0
                        is_open = 1 if ride.get("is_open") else 0

                        cursor.execute("""
                        INSERT OR REPLACE INTO rides
                        (ride_id, ride_name, park_name, land_name)
                        VALUES (?, ?, ?, ?)
                        """, (ride_id, ride_name, park_name, land_name))

                        cursor.execute("""
                        INSERT INTO wait_times
                        (ride_id, wait_time, is_open, recorded_at)
                        VALUES (?, ?, ?, ?)
                        """, (ride_id, wait_time, is_open, timestamp))

                LOGGER.info("Saved wait times for %s", park_name)

            except (requests.RequestException, ValueError, TypeError, KeyError) as error:
                LOGGER.warning("Error fetching %s: %s", park_name, error)
