from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import os
import requests

"""
def get_flights():
    dep_iata = input("Enter departure airport IATA code (e.g., TPE): ").strip().upper()
    arr_iata = input("Enter arrival airport IATA code (e.g., BKK): ").strip().upper()
    flight_date = input("Enter flight date (YYYY-MM-DD): ").strip()

    base_url = "https://api.aviationstack.com/v1/flightsFuture"
    params = {
        "access_key": "7b00304b4dbeef5e33178863939959ac",
        "iataCode": dep_iata,
        "type": "departure",
        "date": flight_date
    }

    response = requests.get(base_url, params=params)

    if response.status_code != 200:
        print(f"Failed: {response.status_code}")
        print(response.text)
        return

    data = response.json()
    flights = data.get("data", [])

    if not flights:
        print("No flights found for these parameters.")
        return

    print(f"\nFlights from {dep_iata} → {arr_iata} on {flight_date}:\n")

    found = False
    for f in flights:
        dep = f.get("departure", {})
        arr = f.get("arrival", {})
        ac = f.get("aircraft", {})
        al = f.get("airline", {})
        fl = f.get("flight", {})

        # Filter only flights going to user input arrival
        if arr.get("iataCode", "").upper() != arr_iata:
            continue

        dep_time = dep.get("scheduledTime", "N/A")
        arr_time = arr.get("scheduledTime", "N/A")

        print(
            f"{al.get('name', '').title()} flight {fl.get('iataNumber', '').upper()} "
            f"({ac.get('modelText', 'Unknown Aircraft')})\n"
            f"From {dep.get('iataCode', '').upper()} → {arr.get('iataCode', '').upper()} "
            f"| Departs {dep_time} → Arrives {arr_time}\n"
        )
        found = True

    if not found:
        print(f"No flights found from {dep_iata} → {arr_iata} on {flight_date}.")

#get_flights()
"""

#RUN "uvicorn flightplan:app --reload" to start backend

app = FastAPI(title="Jet Lag Flight Planner API")

# --- Serve static files ---
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def serve_home():
    return FileResponse(os.path.join("static", "index.html"))



# --------------------------------------CODE--------------------------------------
class FLIGHTPLAN:

    def flightSchedule(self, name, origin, destination, depart_datetime, flight_hours,
                       direction, pre_days, post_days, avg_sleep_start, avg_sleep_end):

        self.name = name
        self.origin = origin
        self.destination = destination
        self.depart_datetime = depart_datetime
        self.flight_hours = flight_hours
        self.direction = direction.lower()
        self.pre_days = pre_days
        self.post_days = post_days
        self.avg_sleep_start = avg_sleep_start
        self.avg_sleep_end = avg_sleep_end
        self.shift_hours = 1


        # Add timezone to departure
        self.depart_dt = datetime.strptime(depart_datetime, "%Y-%m-%d %H:%M").replace(tzinfo=ZoneInfo(origin))
        self.arrival_dt = self.calculate_arrival()

        return self  # so you can chain calls


    def calculate_arrival(self):
        dt = self.depart_dt.replace(tzinfo=ZoneInfo(self.origin))
        arrival = dt + timedelta(hours=self.flight_hours)
        arrival = arrival.astimezone(ZoneInfo(self.destination))
        return arrival

    def format_time(self, decimal_hour):
        hours = int(decimal_hour)
        minutes = int((decimal_hour - hours) * 60)
        return f"{hours:01d}:{minutes:02d}"

    def military_time(self, time_value, shift):
        return (time_value + shift) % 24

    def preFlightSchedule(self):
        pre_schedule = []
        shift_direction = -1 if self.direction == "east" else +1

        pre_sleep_start = self.avg_sleep_start
        pre_sleep_end = self.avg_sleep_end

        for i in range(self.pre_days):
            next_day = self.depart_dt.date() - timedelta(days=self.pre_days - i)
            pre_sleep_start = self.military_time(pre_sleep_start, shift_direction * self.shift_hours)
            pre_sleep_end = self.military_time(pre_sleep_end, shift_direction * self.shift_hours)

            stop_caffeine = self.military_time(pre_sleep_start, -6)
            stop_nap = self.military_time(pre_sleep_start, -8)

            pre_schedule.append({
                "date": str(next_day),
                "sleep_start": self.format_time(pre_sleep_start),
                "sleep_end": self.format_time(pre_sleep_end),
                "no_caffeine_after": self.format_time(stop_caffeine),
                "no_nap_after": self.format_time(stop_nap)
            })
        return pre_schedule

    def postFlightSchedule(self):
        post_schedule = []
        if self.direction == "east":
            nap_cutoff = self.avg_sleep_start - 6
            get_light = nap_cutoff - 6
            for i in range(self.post_days):
                next_day = self.arrival_dt.date() + timedelta(days=i)
                nap_cutoff = self.military_time(nap_cutoff, -1)
                get_light = self.military_time(nap_cutoff, -6)

                post_schedule.append({
                    "date": str(next_day),
                    "sleep_start": self.format_time(self.avg_sleep_start),
                    "sleep_end": self.format_time(self.avg_sleep_end),
                    "nap_cutoff": self.format_time(nap_cutoff),
                    "get_sunlight": self.format_time(get_light)
                })
        elif self.direction == "west":
            for i in range(self.post_days):
                next_day = self.arrival_dt.date() + timedelta(days=i)
                post_schedule.append({
                    "date": str(next_day),
                    "note": "Try to avoid naps and get sunlight in the afternoon."
                })
        return post_schedule

    def jetLagScore(self):
        origin_tz = self.depart_dt.tzinfo.utcoffset(self.depart_dt).total_seconds() / 3600
        dest_tz = self.arrival_dt.tzinfo.utcoffset(self.arrival_dt).total_seconds() / 3600
        tz_diff = abs(origin_tz - dest_tz)
        if tz_diff > 12:
            tz_diff = 24 - tz_diff  # handle wraparound (e.g. TPE→LAX)

        # 1. Timezone difference penalty (max 30 pts)
        diff_score = max(0, 30 - tz_diff * 2.5)

        # 2. Direction adjustment
        if self.direction == "east":
            direction_factor = +1
            direction_score = -5
        else:
            direction_factor = -1
            direction_score = +5

        # 3. Arrival alignment (body clock) max 20
        arrival_local_hour = self.arrival_dt.hour + self.arrival_dt.minute / 60
        body_clock_hour = (arrival_local_hour - tz_diff * direction_factor) % 24
        if 8 <= body_clock_hour <= 18:
            arrival_score = 20
        elif 6 <= body_clock_hour < 8 or 18 < body_clock_hour <= 22:
            arrival_score = 10
        else:
            arrival_score = 0

        # 4. In-flight sleep opportunity (max 30 pts)
        # Assume flight covers continuous period backward from arrival
        sleep_overlap = 0
        for h in range(int(self.flight_hours)):
            t = (body_clock_hour - self.flight_hours + h) % 24
            if t >= self.avg_sleep_start or t < self.avg_sleep_end:
                sleep_overlap += 1
        sleep_ratio = sleep_overlap / max(self.flight_hours, 1)
        plane_sleep_score = sleep_ratio * 30

        # Adjust for service interruptions
        if self.flight_hours > 8:
            plane_sleep_score -= 3
        elif self.flight_hours > 4:
            plane_sleep_score -= 2
        else:
            plane_sleep_score -= 1
        plane_sleep_score = max(0, plane_sleep_score)

        # 5. Sleep pressure (stay awake too long after arrival)(max 15)
        awake_time = abs(arrival_local_hour - self.avg_sleep_start)
        if awake_time >= 10:
            pressure_score = 10
        elif awake_time >= 6 and awake_time < 10:   #best sleep pressure duration
            pressure_score = 15
        elif awake_time >= 2 and awake_time < 6:
            pressure_score = 5
        else:
            pressure_score = 0

        # 6. Total score
        total_score = diff_score + direction_score + arrival_score + plane_sleep_score + pressure_score
        total_score = max(0, min(100, total_score))

        return {
            "total_score": round(total_score, 1),
            "arrival_score": round(arrival_score, 1),
            "plane_sleep_score": round(plane_sleep_score, 1),
            "pressure_score": round(pressure_score, 1),
            "diff_score": round(diff_score, 1),
            "direction_score": round(direction_score, 1),
        }

    def rankFlights(flights):
        ranked = []
        for f in flights:
            scores = f.jetLagScore()
            name = f.name
            print(
                f"{name}: Total={scores['total_score']} | "
                f"Arrival={scores['arrival_score']} | "
                f"Sleep={scores['plane_sleep_score']} | "
                f"Pressure={scores['pressure_score']} | "
                f"TZ Diff={scores['diff_score']} | "
                f"Direction={scores['direction_score']}"
            )
            ranked.append((name, scores['total_score']))
        ranked.sort(key=lambda x: x[1], reverse=True)
        return ranked


# -------------------------------------------- Test Input ------------------------------------------
flights = [
    FLIGHTPLAN().flightSchedule("Morning Flight", "Asia/Taipei", "America/Los_Angeles",
                                "2025-10-30 10:10", 12, "east", 0, 3, 22, 6),
    FLIGHTPLAN().flightSchedule("Evening Flight", "Asia/Taipei", "America/Los_Angeles",
                                "2025-10-30 19:40", 11, "east", 0, 3, 22, 6),
    FLIGHTPLAN().flightSchedule("Late Night Flight", "Asia/Taipei", "America/Los_Angeles",
                                "2025-10-30 00:00", 11, "east", 0, 3, 22, 6),
    FLIGHTPLAN().flightSchedule("Short flight", "Asia/Taipei", "Asia/Bangkok",
                                "2025-10-30 9:10", 3, "west", 0, 0, 22, 6)
]

# ------------------------------------- Print jet-lag scores -----
for f in flights:
    print(f"{f.name} | Depart: {f.depart_dt.strftime('%Y-%m-%d %H:%M')} | Arrival: {f.arrival_dt.strftime('%Y-%m-%d %H:%M')} | Jet-lag score: {f.jetLagScore()}")

# ------------------------------------- Print ranked flights -----
print("\nRanked Flights:")
for name, score in FLIGHTPLAN.rankFlights(flights):
    print(f"{name}: {score}")


# --------------------------------------FASTAPI MODEL--------------------------------------
class FlightRequest(BaseModel):
    name: str
    origin: str
    destination: str
    depart_datetime: str  # "YYYY-MM-DD HH:MM"
    flight_hours: float
    direction: str
    pre_days: int
    post_days: int
    avg_sleep_start: float
    avg_sleep_end: float


# --------------------------------------API ROUTE--------------------------------------
@app.post("/generate_schedule")
def generate_schedule(data: FlightRequest):
    planner = FLIGHTPLAN()
    planner.flightSchedule(**data.dict())

    pre_schedule = planner.preFlightSchedule()
    post_schedule = planner.postFlightSchedule()

    return {
        "traveler": data.name,
        "origin": data.origin,
        "destination": data.destination,
        "departure_time": data.depart_datetime,
        "arrival_time": planner.arrival_dt.strftime("%Y-%m-%d %H:%M %Z"),
        "pre_flight_schedule": pre_schedule,
        "post_flight_schedule": post_schedule
    }
