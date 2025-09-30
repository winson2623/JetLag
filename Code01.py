import mysql.connector
from tkinter import *
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

        print("---Pre-Flight Schedule---")

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


            print(f"pre_sleep_start time: ", self.format_time(pre_sleep_start))
            print(f"pre_sleep_end time: ", self.format_time(pre_sleep_end))
            print(f"no caffeine after: ", self.format_time(stop_caffeine))
            print(f"no power naps after: ", self.format_time(stop_nap))
        print()


    def postFlightSchedule(self):
        self.post_schedule = []

        print("---Post-Flight Schedule---")
        print("YOUR FLIGHT IS ON: ", self.depart_dt.strftime("%Y-%m-%d %H:%M %Z"),
              " AND WILL ARRIVE ON: ", self.arrival_dt.strftime("%Y-%m-%d %H:%M %Z"))
        print()


        if self.direction == "east": #east means sleep earlier
            nap_cutoff = self.avg_sleep_start - 6
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
                    "sunlight": self.format_time(get_light)
                })

                print(f"post_sleep_start time: ", self.format_time(self.avg_sleep_start))
                print(f"post_sleep_end time: ", self.format_time(self.avg_sleep_end))
                print(f"nap_cutoff time: ", self.format_time(nap_cutoff))
                print(f"get sunlight between: ", self.format_time(get_light), "and", self.format_time(nap_cutoff - 3))


        elif self.direction == "west":
            print("Try not to take naps")
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
    mydb.commit()

    # LOOPING DATA INTO POST_TABLE
    for entry in my_flight.post_schedule:
        my_cursor.execute(
            "INSERT INTO post_table(flight_id, date, post_sleep_start, post_sleep_end, no_nap, sunlight) VALUES (%s,%s,%s,%s,%s,%s)",
            (flight_id, entry["date"], entry["post_sleep_start"], entry["post_sleep_end"], entry["nap_cutoff"],
             entry["sunlight"])
        )
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
window.geometry("520x450")
window.title("Jet Lag Scheduler")
window.configure(background="white")

fields = [("Name","name",0),
          ("Origin","origin",40),
          ("Destination","destination",80),
          ("Departure Date Time", "depart_datetime", 120),
          ("Flight Hours","flight_hours",160),
          ("Flight Direction","direction",200),
          ("Pre-Flight Adjustment Days","pre_days",240),
          ("Post-Flight Adjustment Days","post_days",280),
          ("Average Bedtime","avg_sleep_start",320),
          ("Average Wake Up Time","avg_sleep_end",360)]
entries = {}

for label_text, key, y in fields:
    label = Label(window, text=label_text, font=("Arial", 12) ,background="white")
    label.place(x=0, y=y)

    entry = Entry(window, font=("Arial", 12), justify = "center",background="white")
    entry.place(x=320, y=y)

    if key == "depart_datetime":
        entry.placeholder = "YYYY-MM-DD HH:MM"
        entry.insert(0,entry.placeholder)
        entry.config(foreground="gray")
        entry.bind("<FocusIn>", entry_focus_in)
        entry.bind("<FocusOut>", entry_focus_out)

    if key in ("avg_sleep_start" , "avg_sleep_end"):
        entry.placeholder = "0-23"
        entry.insert(0,entry.placeholder)
        entry.config(foreground="gray")
        entry.bind("<FocusIn>", entry_focus_in)
        entry.bind("<FocusOut>", entry_focus_out)

    entries[key] = entry


submit_btn = Button(window, text="Submit", command=submit)
submit_btn.place(x=455, y=400)

window.mainloop()


