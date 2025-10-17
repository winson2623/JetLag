from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import os

#RUN "uvicorn flightplan:app --reload" to start backend

app = FastAPI(title="Jet Lag Flight Planner API")

# --- Serve static files ---
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def serve_home():
    return FileResponse(os.path.join("static", "index.html"))



# --------------------------------------CLASS--------------------------------------
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

        self.depart_dt = datetime.strptime(depart_datetime, "%Y-%m-%d %H:%M")
        self.arrival_dt = self.calculate_arrival()

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
