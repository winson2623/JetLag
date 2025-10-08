import mysql.connector
from tkinter import *
from tkinter import ttk
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


#------------------------------------------CLASS & LOCAL VARIABLES-----------------------------------------
class FLIGHTPLAN:

    def flightSchedule(self, name, origin, destination, depart_datetime, flight_hours,
                     direction, pre_days, post_days, avg_sleep_start, avg_sleep_end):

        self.name = name
        self.origin = origin
        self.destination = destination
        self.depart_datetime = depart_datetime
        self.flight_hours = flight_hours
        self.direction = direction
        self.pre_days = pre_days
        self.post_days = post_days
        self.avg_sleep_start = avg_sleep_start
        self.avg_sleep_end = avg_sleep_end

        #shifting hour for pre/post flight schedule
        self.shift_hours = 1

        #converting datetime to object so that we can do arithmetic
        self.depart_dt = datetime.strptime(depart_datetime, "%Y-%m-%d %H:%M")
        self.arrival_dt = self.calculate_arrival()



    def calculate_arrival(self):
        #attaches departure timezone
        dt = self.depart_dt.replace(tzinfo=ZoneInfo(self.origin))

        #adds the flight duration to origin timezone
        arrival = dt + timedelta(hours=self.flight_hours)

        #converts to destination timezone
        arrival = arrival.astimezone(ZoneInfo(self.destination))
        return arrival



    #helper functions
    def format_time(self, decimal_hour):
        hours = int(decimal_hour)
        minutes = int((decimal_hour - hours) * 60)
        return f"{hours:01d}:{minutes:02d}"

    def military_time(self, time_value, shift):
        return (time_value + shift) % 24

    def preFlightSchedule(self):
        self.pre_schedule = []

        if self.direction == "east": #east means sleep earlier
            shift_direction = -1
        elif self.direction == "west": #west means sleep later
            shift_direction = +1
        else:
            print("Direction must be east or west, try again.")
            shift_direction = 0
            return

        pre_sleep_start = self.avg_sleep_start
        pre_sleep_end = self.avg_sleep_end

        print("---Pre-Flight Schedule Printed---")

        for i in range(self.pre_days):
            # date loop
            next_day = self.depart_dt.date() - timedelta(days=self.pre_days - i)
            print(next_day.month, "/", next_day.day)

            #shift sleep times
            pre_sleep_start = self.military_time(pre_sleep_start, shift_direction * self.shift_hours)
            pre_sleep_end = self.military_time(pre_sleep_end, shift_direction * self.shift_hours)

            #caffine & nap cut off time
            stop_caffeine = self.military_time(pre_sleep_start, -6)
            stop_nap = self.military_time(pre_sleep_start, -8)

            self.pre_schedule.append({
                "date": next_day,
                "pre_sleep_start": self.format_time(pre_sleep_start),
                "pre_sleep_end": self.format_time(pre_sleep_end),
                "no_caffeine": self.format_time(stop_caffeine),
                "no_nap": self.format_time(stop_nap)
            })



    def postFlightSchedule(self):
        self.post_schedule = []

        print("---Post-Flight Schedule Printed---")


        if self.direction == "east": #east means sleep earlier
            nap_cutoff = self.avg_sleep_start - 8
            get_light = nap_cutoff - 6
            for i in range(self.post_days):
                next_day = self.arrival_dt.date() + timedelta(days = i)
                print(next_day.month, "/", next_day.day)

                nap_cutoff = self.military_time(nap_cutoff, -1)
                get_light = self.military_time(nap_cutoff, -6)

                self.post_schedule.append({
                    "date": next_day,
                    "post_sleep_start": self.format_time(self.avg_sleep_start),
                    "post_sleep_end": self.format_time(self.avg_sleep_end),
                    "nap_cutoff": self.format_time(nap_cutoff),
                    "get_light": f"{self.format_time(get_light)} - {self.format_time(nap_cutoff - 3)}"
                })

        elif self.direction == "west":
            nap_cutoff = self.avg_sleep_start - 8
            get_light = nap_cutoff - 6

            for i in range(self.post_days):
                next_day = self.arrival_dt.date() + timedelta(days=i)
                print(next_day.month, "/", next_day.day)

                self.post_schedule.append({
                    "date": next_day,
                    "post_sleep_start": self.format_time(self.avg_sleep_start),
                    "post_sleep_end": self.format_time(self.avg_sleep_end),
                    "nap_cutoff": self.format_time(nap_cutoff),
                    "get_light": f"{self.format_time(get_light)} - {self.format_time(nap_cutoff - 3)}"
                })
                #decrement for next day
                nap_cutoff = self.military_time(nap_cutoff, -1)
                get_light = self.military_time(nap_cutoff, -6)
        else:
            print("Direction must be east or west, try again.")


#-------------------------------------------GUI INPUTS----------------------------------------------------------------
def submit():
    name = entries["name"].get()
    origin = entries["origin"].get()
    destination = entries["destination"].get()
    depart_datetime = entries["depart_datetime"].get()
    flight_hours = int(entries["flight_hours"].get())
    direction = entries["direction"].get()
    pre_days = int(entries["pre_days"].get())
    post_days = int(entries["post_days"].get())
    avg_sleep_start = int(entries["avg_sleep_start"].get())
    avg_sleep_end = int(entries["avg_sleep_end"].get())


    # -----------INITIALIZE CLASS------------
    my_flight = FLIGHTPLAN()
    my_flight.flightSchedule(name, origin, destination, depart_datetime, flight_hours,
                             direction, pre_days, post_days, avg_sleep_start, avg_sleep_end)

    my_flight.preFlightSchedule()
    my_flight.postFlightSchedule()

    # Show arrival time in GUI
    arrival_time_str = my_flight.arrival_dt.strftime("%Y-%m-%d %H:%M %Z")
    arrival_label.config(text=f"Arrival Date & Time: {arrival_time_str}")

    # -------------MYSQL DATA--------------
    inputTableSql = """
                    INSERT INTO input_table
                    (name, origin, destination, depart_datetime, flight_hours,
                     direction, pre_days, post_days, avg_sleep_start, avg_sleep_end)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) \
                    """

    inputTableVal = (name, origin, destination, depart_datetime, flight_hours,
                     direction, pre_days, post_days, avg_sleep_start, avg_sleep_end)

    my_cursor.execute(inputTableSql, inputTableVal)
    mydb.commit()
    flight_id = my_cursor.lastrowid  # ID of the newly inserted flight
    print("Inserted flight_id:", flight_id)

    # LOOPING DATA INTO PRE_TABLE
    for entry in my_flight.pre_schedule:
        my_cursor.execute(
            "INSERT INTO pre_table(flight_id, date, pre_sleep_start, pre_sleep_end, no_caffeine, no_nap) VALUES (%s,%s,%s,%s,%s,%s)",
            (flight_id, entry["date"], entry["pre_sleep_start"], entry["pre_sleep_end"], entry["no_caffeine"],
             entry["no_nap"])
        )
        # Insert into GUI table
        pre_tree.insert(parent='', index='end', iid=f"{flight_id}_pre_{entry['date']}", text='',
                        values=(entry["date"], entry["pre_sleep_start"], entry["pre_sleep_end"],
                                entry["no_caffeine"], entry["no_nap"]))
    mydb.commit()

    # LOOPING DATA INTO POST_TABLE
    for entry in my_flight.post_schedule:
        my_cursor.execute(
            "INSERT INTO post_table(flight_id, date, post_sleep_start, post_sleep_end, no_nap, get_light) VALUES (%s,%s,%s,%s,%s,%s)",
            (flight_id, entry["date"], entry["post_sleep_start"], entry["post_sleep_end"], entry["nap_cutoff"],
             entry["get_light"])
        )
        # Insert into GUI table
        post_tree.insert(parent='', index='end', iid=f"{flight_id}_post_{entry['date']}", text='',
                         values=(entry["date"], entry["post_sleep_start"], entry["post_sleep_end"],
                                 entry["nap_cutoff"], entry["get_light"]))
    mydb.commit()

    print(my_cursor.rowcount, " flight record inserted.")

def entry_focus_in(event):
    if event.widget.get() == event.widget.placeholder:
        event.widget.delete(0, 'end')
        event.widget.config(foreground='black')

def entry_focus_out(event):
    if event.widget.get() == "":
        event.widget.insert(0,event.widget.placeholder)
        event.widget.config(foreground='gray')


# ------------------------------------------MYSQL CONNECTOR---------------------------------------------
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="root1234",
    database="jetlagdb"
)
my_cursor = mydb.cursor()


# -------------------------------------------GUI LAYOUT--------------------------------------------------
window = Tk()
window.geometry("620x780")
window.title("Jet Lag Scheduler")
window.configure(background="white")

# List of valid timezones for dropdowns
timezones = [
    # Asia
    "Asia/Taipei", "Asia/Tokyo", "Asia/Shanghai", "Asia/Hong_Kong",
    "Asia/Seoul", "Asia/Singapore", "Asia/Kolkata", "Asia/Dubai",
    "Asia/Kuala_Lumpur", "Asia/Manila", "Asia/Bangkok",
    # Europe
    "Europe/London", "Europe/Paris", "Europe/Berlin", "Europe/Madrid",
    "Europe/Rome", "Europe/Moscow", "Europe/Amsterdam", "Europe/Zurich",
    "Europe/Oslo", "Europe/Stockholm",
    # North America
    "America/New_York", "America/Chicago", "America/Denver",
    "America/Los_Angeles", "America/Toronto", "America/Vancouver",
    "America/Mexico_City", "America/Anchorage", "America/Phoenix",
    "America/Detroit",
    # South America
    "America/Sao_Paulo", "America/Buenos_Aires", "America/Lima",
    "America/Bogota", "America/Santiago",
    # Oceania
    "Australia/Sydney", "Australia/Melbourne", "Australia/Brisbane",
    "Australia/Perth", "Pacific/Auckland", "Pacific/Fiji",
    # Africa / Middle East
    "Africa/Johannesburg", "Africa/Cairo", "Africa/Nairobi",
    "Africa/Lagos", "Africa/Casablanca"
]

fields = [("Name","name",0),
          ("Origin","origin",40),
          ("Destination","destination",80),
          ("Departure Date Time", "depart_datetime",120),
          ("Flight Hours","flight_hours",160),
          ("Flight Direction","direction",200),
          ("Pre-Flight Adjustment Days","pre_days",240),
          ("Post-Flight Adjustment Days","post_days",280),
          ("Average Bedtime","avg_sleep_start",320),
          ("Average Wake Up Time","avg_sleep_end",360)]
entries = {}

for label_text, key, y in fields:
    label = Label(window, text=label_text, font=("Arial", 12), background="white")
    label.place(x=0, y=y)

    # Use dropdown for Origin and Destination
    if key in ("origin", "destination"):
        combo = ttk.Combobox(window, values=timezones, font=("Arial", 12), justify="center")
        combo.place(x=320, y=y, width=280)
        combo.current(0)  # default to first timezone
        entries[key] = combo
        continue

    entry = Entry(window, font=("Arial", 12), justify="center", background="white")
    entry.place(x=320, y=y, width=280)

    if key == "depart_datetime":
        entry.placeholder = "YYYY-MM-DD HH:MM"
        entry.insert(0, entry.placeholder)
        entry.config(foreground="gray")
        entry.bind("<FocusIn>", entry_focus_in)
        entry.bind("<FocusOut>", entry_focus_out)

    if key in ("avg_sleep_start", "avg_sleep_end"):
        entry.placeholder = "0-23"
        entry.insert(0, entry.placeholder)
        entry.config(foreground="gray")
        entry.bind("<FocusIn>", entry_focus_in)
        entry.bind("<FocusOut>", entry_focus_out)

    if key == "direction":
        entry.placeholder = "east or west"
        entry.insert(0, entry.placeholder)
        entry.config(foreground="gray")
        entry.bind("<FocusIn>", entry_focus_in)
        entry.bind("<FocusOut>", entry_focus_out)

    entries[key] = entry

submit_btn = Button(window, text="Submit", command=submit)
submit_btn.place(x=555, y=400)


# ----------------- PRE-FLIGHT SCHEDULE TABLE -----------------
pre_label = Label(window, text="Pre-Flight Schedule", font=("Arial", 12, "bold"), background="white")
pre_label.place(x=10, y=430)

pre_tree = ttk.Treeview(window)
pre_tree['columns'] = ("Date", "Pre Sleep Start", "Pre Sleep End", "No Caffeine After", "No Nap After")
pre_tree.column("#0", width=0, stretch=NO)
for col in pre_tree['columns']:
    pre_tree.column(col, anchor=CENTER, width=115)
    pre_tree.heading(col, text=col, anchor=CENTER)
pre_tree.place(x=10, y=460, width=600, height=120)

# ----------------- ARRIVAL INFO LABEL -----------------
arrival_label = Label(window, text="Arrival Date Time: (calculated after submit)",
                      font=("Arial", 12, "italic"), background="white", foreground="gray")
arrival_label.place(x=10, y=585)

# ----------------- POST-FLIGHT SCHEDULE TABLE -----------------
post_label = Label(window, text="Post-Flight Schedule", font=("Arial", 12, "bold"), background="white")
post_label.place(x=10, y=620)

post_tree = ttk.Treeview(window)
post_tree['columns'] = ("Date", "Post Sleep Start", "Post Sleep End", "No Nap After", "Get Light")
post_tree.column("#0", width=0, stretch=NO)
for col in post_tree['columns']:
    post_tree.column(col, anchor=CENTER, width=115)
    post_tree.heading(col, text=col, anchor=CENTER)
post_tree.place(x=10, y=650, width=600, height=120)

window.mainloop()


