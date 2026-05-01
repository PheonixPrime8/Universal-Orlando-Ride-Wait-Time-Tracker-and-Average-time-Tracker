import requests
from datetime import datetime
from database import get_connection

PARKS = {
    "Islands of Adventure": 64,
    "Universal Studios Florida": 65,
    "Epic Universe": 334
}


def fetch_and_save_wait_times():
    conn = get_connection()
    cursor = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for park_name, park_id in PARKS.items():
        url = f"https://queue-times.com/parks/{park_id}/queue_times.json"

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            for land in data.get("lands", []):
                land_name = land.get("name", "Unknown Land")

                for ride in land.get("rides", []):
                    ride_id = ride.get("id")
                    ride_name = ride.get("name")
                    wait_time = ride.get("wait_time", 0)
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

            print(f"Saved wait times for {park_name}")

        except requests.RequestException as error:
            print(f"Error fetching {park_name}: {error}")

    conn.commit()
    conn.close()
