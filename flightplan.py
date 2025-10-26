from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel                  #incoming data request
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import os                                       #file path
import requests                                 #aviation api

#RUN "uvicorn flightplan:app --reload" to start backend

app = FastAPI(title="Jet Lag Flight Planner API")

TZ_IATA_MAP = {
    # Asia
    "Asia/Taipei": "TPE",          # Taiwan Taoyuan International
    "Asia/Tokyo": "HND",           # Tokyo Haneda
    "Asia/Shanghai": "PVG",        # Shanghai Pudong
    "Asia/Hong_Kong": "HKG",       # Hong Kong International
    "Asia/Seoul": "ICN",           # Incheon International
    "Asia/Singapore": "SIN",       # Changi Airport
    "Asia/Kolkata": "DEL",         # Indira Gandhi International (New Delhi)
    "Asia/Dubai": "DXB",           # Dubai International
    "Asia/Kuala_Lumpur": "KUL",    # Kuala Lumpur International
    "Asia/Manila": "MNL",          # Ninoy Aquino International
    "Asia/Bangkok": "BKK",         # Suvarnabhumi Airport

    # Europe
    "Europe/London": "LHR",        # Heathrow
    "Europe/Paris": "CDG",         # Charles de Gaulle
    "Europe/Berlin": "BER",        # Berlin Brandenburg
    "Europe/Madrid": "MAD",        # Madrid-Barajas
    "Europe/Rome": "FCO",          # Fiumicino
    "Europe/Moscow": "SVO",        # Sheremetyevo
    "Europe/Amsterdam": "AMS",     # Schiphol
    "Europe/Zurich": "ZRH",        # Zurich Airport
    "Europe/Oslo": "OSL",          # Oslo Gardermoen
    "Europe/Stockholm": "ARN",     # Arlanda

    # North America
    "America/New_York": "JFK",     # JFK International
    "America/Chicago": "ORD",      # O’Hare
    "America/Denver": "DEN",       # Denver International
    "America/Los_Angeles": "LAX",  # Los Angeles International
    "America/Toronto": "YYZ",      # Pearson International
    "America/Vancouver": "YVR",    # Vancouver International
    "America/Mexico_City": "MEX",  # Mexico City International
    "America/Anchorage": "ANC",    # Ted Stevens Anchorage
    "America/Phoenix": "PHX",      # Sky Harbor
    "America/Detroit": "DTW",      # Detroit Metro

    # South America
    "America/Sao_Paulo": "GRU",    # Guarulhos
    "America/Buenos_Aires": "EZE", # Ezeiza
    "America/Lima": "LIM",         # Jorge Chávez
    "America/Bogota": "BOG",       # El Dorado
    "America/Santiago": "SCL",     # Arturo Merino Benítez

    # Oceania
    "Australia/Sydney": "SYD",     # Sydney Kingsford Smith
    "Australia/Melbourne": "MEL",  # Melbourne Airport
    "Australia/Brisbane": "BNE",   # Brisbane Airport
    "Australia/Perth": "PER",      # Perth Airport
    "Pacific/Auckland": "AKL",     # Auckland Airport
    "Pacific/Fiji": "NAN",         # Nadi International

    # Africa / Middle East
    "Africa/Johannesburg": "JNB",  # OR Tambo International
    "Africa/Cairo": "CAI",         # Cairo International
    "Africa/Nairobi": "NBO",       # Jomo Kenyatta
    "Africa/Lagos": "LOS",         # Murtala Muhammed
    "Africa/Casablanca": "CMN"     # Mohammed V
}


# ---static files---
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
        # parse datetime first
        self.depart_dt = datetime.strptime(depart_datetime, "%Y-%m-%d %H:%M")

        # add timezone using ZoneInfo, but pass the **timezone string**, NOT the IATA code
        self.depart_dt = self.depart_dt.replace(tzinfo=ZoneInfo(self.origin))

        # calculate arrival
        self.arrival_dt = self.calculate_arrival()

        return self


    def calculate_arrival(self):
        dt = self.depart_dt.replace(tzinfo=ZoneInfo(self.origin))
        arrival = self.depart_dt + timedelta(hours=self.flight_hours)
        arrival = arrival.astimezone(ZoneInfo(self.destination))  # destination = timezone string
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

        #TIME ZONE DIFFERENCE SCORE
        tz_diff = abs(origin_tz - dest_tz)
        if tz_diff > 12:
            tz_diff = 24 - tz_diff

        #DIRECTION SCORE
        diff_score = max(0.0, 30.0 - tz_diff * 2.5)
        direction_factor = +1 if self.direction == "east" else -1
        direction_score = -5 if self.direction == "east" else +5

        #ARRIVAL TIME SCORE
        arrival_local_hour = self.arrival_dt.hour + self.arrival_dt.minute / 60
        body_clock_hour = (arrival_local_hour - tz_diff * direction_factor) % 24
        if 8 <= body_clock_hour <= 18:
            arrival_score = 20
        elif 6 <= body_clock_hour < 8 or 18 < body_clock_hour <= 22:
            arrival_score = 10
        else:
            arrival_score = 0

        #PLANE SLEEP SCORE
        sleep_overlap = 0
        for h in range(int(self.flight_hours)):
            t = (body_clock_hour - self.flight_hours + h) % 24
            if t >= self.avg_sleep_start or t < self.avg_sleep_end:
                sleep_overlap += 1
        sleep_ratio = sleep_overlap / max(self.flight_hours, 1)
        plane_sleep_score = sleep_ratio * 30

        #IN FLIGHT SERVICE DISRUPTION TO SLEEP
        if self.flight_hours > 8:
            plane_sleep_score -= 3
        elif self.flight_hours > 4:
            plane_sleep_score -= 2
        else:
            plane_sleep_score -= 1
        plane_sleep_score = max(0, plane_sleep_score)

        #PRESSURE SLEEP SCORE
        awake_time = abs(arrival_local_hour - self.avg_sleep_start)
        if awake_time >= 10:
            pressure_score = 10
        elif 6 <= awake_time < 10:
            pressure_score = 15
        elif 2 <= awake_time < 6:
            pressure_score = 5
        else:
            pressure_score = 0

        total_score = diff_score + direction_score + arrival_score + plane_sleep_score + pressure_score
        total_score = max(0.0, min(100.0, total_score))
        return {
            "total_score": round(total_score, 1),
            "arrival_score": round(arrival_score, 1),
            "plane_sleep_score": round(plane_sleep_score, 1),
            "pressure_score": round(pressure_score, 1),
            "diff_score": round(diff_score, 1),
            "direction_score": round(direction_score, 1),
        }

    @staticmethod
    def rankFlights(flights):
        ranked = []
        for f in flights:
            scores = f.jetLagScore()
            name = f.name
            print(f"{name}: Total={scores['total_score']} | Arrival={scores['arrival_score']} | "
                  f"Sleep={scores['plane_sleep_score']} | Pressure={scores['pressure_score']} | "
                  f"TZ Diff={scores['diff_score']} | Direction={scores['direction_score']}")
            ranked.append((name, scores['total_score']))
        ranked.sort(key=lambda x: x[1], reverse=True)
        return ranked


    # -------------------------------------- flights API FETCH -------------------------------------------
    def get_flights(self, origin, destination, depart_datetime,direction):
        dep_iata = TZ_IATA_MAP.get(origin, "Unknown").strip().upper()
        arr_iata = TZ_IATA_MAP.get(destination, "Unknown").strip().upper()
        flight_date = depart_datetime.date()

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
            return []

        data = response.json()
        flights_data = data.get("data", [])
        flights = []

        for f in flights_data:
            dep = f.get("departure", {})
            arr = f.get("arrival", {})
            ac = f.get("aircraft", {})
            al = f.get("airline", {})
            fl = f.get("flight", {})

            #filters arrival airport IATA
            if arr.get("iataCode", "").upper() != arr_iata:
                continue

            dep_time = dep.get("scheduledTime")
            arr_time = arr.get("scheduledTime")

            print(
                f"{al.get('name', '').title()} flight {fl.get('iataNumber', '').upper()} "
                f"({ac.get('modelText', 'Unknown Aircraft')})\n"
                f"Depart: {dep_iata} at {dep_time} | Arrive: {arr_iata} at {arr_time}\n"
            )

            if not dep_time or not arr_time:
                continue

            try:
                dep_dt = datetime.strptime(f"{flight_date} {dep_time}", "%Y-%m-%d %H:%M")
            except ValueError:
                continue

            #Approx flight duration
            dep_hour = int(dep_time.split(":")[0])
            arr_hour = int(arr_time.split(":")[0])
            flight_hours = (arr_hour - dep_hour) % 24
            flight_hours = flight_hours if flight_hours > 0 else 2


            #Create FLIGHTPLAN
            flight_obj = FLIGHTPLAN()
            flight_obj.orig_dep_time = dep_time
            flight_obj.orig_arr_time = arr_time
            flight_obj.flightSchedule(
                f"{al.get('name', '').title()} {fl.get('iataNumber', '').upper()}",
                origin, destination,
                f"{flight_date} {dep_time}",  # API departure
                flight_hours,  # compute from API times
                direction, 0, 0, 22, 6
            )
            flights.append(flight_obj)

        if not flights:
            print(f"No flights found from {dep_iata} → {arr_iata} on {flight_date}.")
        return flights


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
    user_dt = datetime.strptime(data.depart_datetime, "%Y-%m-%d %H:%M")

    # --- Fetch all flights for the date ---
    planner = FLIGHTPLAN()
    flights_data = planner.get_flights(
        origin=data.origin,
        destination=data.destination,
        depart_datetime=datetime.strptime(data.depart_datetime, "%Y-%m-%d %H:%M"),
        direction = data.direction
    )

    # --- Create FLIGHTPLAN for each flight for ranking ---
    for f in flights_data:
        f.flightSchedule(
            f.name, f.origin, f.destination, f.depart_datetime,
            f.flight_hours, f.direction, 0, 0, data.avg_sleep_start, data.avg_sleep_end
        )

    # --- Rank all flights ---
    # The updated flights_data is used for ranking.
    ranked_flights = FLIGHTPLAN.rankFlights(flights_data)


    user_flight = FLIGHTPLAN().flightSchedule(
        f"{data.name}'s flight",
        data.origin, data.destination,
        data.depart_datetime,
        data.flight_hours,
        data.direction,
        data.pre_days,
        data.post_days,
        data.avg_sleep_start,
        data.avg_sleep_end
    )
    pre_schedule = user_flight.preFlightSchedule()
    post_schedule = user_flight.postFlightSchedule()

    # --- Build response ---
    ranked_table = []
    for rank, (name, score) in enumerate(ranked_flights, start=1):
        f_obj = next(f for f in flights_data if f.name == name)
        ranked_table.append({
            "rank": rank,
            "flight_name": name,
            "total_score": score,
            "departure": f_obj.orig_dep_time,
            "arrival": f_obj.orig_arr_time,
        })

    return {
        "pre_flight_schedule": pre_schedule,
        "post_flight_schedule": post_schedule,
        "flights_found": ranked_table
    }
