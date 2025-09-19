import mysql.connector
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="root1234",
    database="jetlagdb"
)

#create cursor instance
my_cursor = mydb.cursor()

#user input for flight_table
name = input("Enter Name: ")
origin = input("Enter Origin City: ")
destination = input("Enter Destination City: ")
depart_datetime = input ("Departure Date and Time: (YYYY-MM-DD HH:MM): ")
flight_hours = float(input("Flight Hours: "))
direction = input ("Flight Direction: ")
pre_days = int(input("pre-adjust days: "))
post_days = int(input("post-adjust days: "))
avg_sleep_start = int(input ("Average Bed time (0-24): "))
avg_sleep_end = int(input ("Average Wake up time (0-24): "))


"""
#FLIGHT TABLE
flightTableSql = """
#INSERT INTO flight_table
#(origin_city, destination_city, departure_datetime,
#flight_hours, direction, pre_adjust_days, post_adjust_days)
#VALUES (%s, %s, %s, %s, %s, %s, %s,)
"""

flightTableVal = (origin, destination, depart_datetime,
       flight_hours,direction, pre_days, post_days)

#USER TABLE
userTableSql = """
#INSERT INTO user_table(user_name, average_sleep_start, average_sleep_end)VALUES (%s, %s, %s)
"""

userTableVal = (name, avg_sleep_start, avg_sleep_end)

my_cursor.execute(userTableSql, userTableVal)
mydb.commit()
user_id = my_cursor.lastrowid  # ID of the newly inserted user
print("Inserted user_id:", user_id)

my_cursor.execute(flightTableSql, flightTableVal)
mydb.commit()
flight_id = my_cursor.lastrowid  # ID of the newly inserted flight
print("Inserted flight_id:", flight_id)


#SLEEP TABLE
sleepTableSql = """
#INSERT INTO sleep_plan_table(flight_id, user_id, user_name)VALUES (%s, %s, %s)
"""

sleepTableVal = (flight_id, user_id, name)


my_cursor.execute(sleepTableSql, sleepTableVal)
mydb.commit()
plan_id = my_cursor.lastrowid  # ID of the newly inserted flight
print("Inserted plan_id:", plan_id)

print(my_cursor.rowcount, " flight record inserted.")
"""

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

        self.shift_hours = 1

        self.depart_dt = datetime.strptime(depart_datetime, "%Y-%m-%d %H:%M")
        self.arrival_dt = self.calculate_arrival()

        self.pre_shifted_date = self.depart_dt.date()
        self.post_shifted_date = self.arrival_dt.date()


    def calculate_arrival(self):
        # Attach departure timezone
        dt = self.depart_dt.replace(tzinfo=ZoneInfo(self.origin))

        # Add flight duration to origin timezone
        arrival = dt + timedelta(hours=self.flight_hours)

        # Convert to destination timezone
        arrival = arrival.astimezone(ZoneInfo(self.destination))
        return arrival



    #helper Functions
    def format_time(self, decimal_hour):
        hours = int(decimal_hour)
        minutes = int((decimal_hour - hours) * 60)
        return f"{hours:01d}:{minutes:02d}"

    def military_time(self, time_value, shift):
        return (time_value + shift) % 24

    def preFlightSchedule(self):
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
            next_day = self.pre_shifted_date - timedelta(days= self.pre_days - i)
            print(next_day.month,"/",next_day.day)

            #shift sleep times
            pre_sleep_start = self.military_time(pre_sleep_start, shift_direction * self.shift_hours)
            pre_sleep_end = self.military_time(pre_sleep_end, shift_direction * self.shift_hours)

            print(f"pre_sleep_start time: ", self.format_time(pre_sleep_start))
            print(f"pre_sleep_end time: ", self.format_time(pre_sleep_end))

            #caffine & nap cut off time
            stop_caffeine = self.military_time(pre_sleep_start, -6)
            stop_nap = self.military_time(pre_sleep_start, -8)

            print(f"no caffeine after: ", self.format_time(stop_caffeine))
            print(f"no power naps after: ", self.format_time(stop_nap))
        print()


    def postFlightSchedule(self):
        print("---Post-Flight Schedule---")
        print("YOUR FLIGHT IS ON: ", self.depart_dt.strftime("%Y-%m-%d %H:%M %Z"),
              " AND WILL ARRIVE ON: ", self.arrival_dt.strftime("%Y-%m-%d %H:%M %Z"))
        print()
        print (f"post_sleep_start time: ", self.format_time(self.avg_sleep_start))
        print(f"post_sleep_end time: ", self.format_time(self.avg_sleep_end))
        print()

        if direction == "east": #east means sleep earlier
            nap_cutoff = self.avg_sleep_start - 6
            get_light = nap_cutoff - 6
            for i in range(self.post_days):
                next_day = self.post_shifted_date + timedelta(days = i)
                print(next_day.month, "/", next_day.day)

                print(f"nap_cutoff time: ", self.format_time(nap_cutoff))
                print(f"get sunlight between: ", self.format_time(get_light), "and", self.format_time(nap_cutoff - 3))

                nap_cutoff = self.military_time(nap_cutoff, -1)
                get_light = self.military_time(nap_cutoff, -6)

        elif self.direction == "west":
            print("Try not to take naps")
        else:
            print("Direction must be east or west, try again.")

my_flight = FLIGHTPLAN()
my_flight.flightSchedule(name, origin, destination, depart_datetime, flight_hours,
                         direction, pre_days, post_days, avg_sleep_start, avg_sleep_end)

my_flight.preFlightSchedule()
my_flight.postFlightSchedule()

