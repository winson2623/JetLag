import mysql.connector
from datetime import datetime, timedelta

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="root1234",
    database="jetlagdb"
)

#create cursor instance
my_cursor = mydb.cursor()

#user input for flight_table
#name = input("Enter Name: ")
#origin = input("Enter Origin City: ")
#destination = input("Enter Destination City: ")
depart_datetime = input ("Departure Date and Time: (YYYY-MM-DD HH:MM:SS): ")
#arrival_datetime = input ("Arrival Date and Time: (YYYY-MM-DD HH:MM:SS): ")
#flight_hours = float(input("Flight Hours: "))
direction = input ("Flight Direction: ")
pre_days = int(input("pre-adjust days: "))
post_days = int(input("post-adjust days: "))

avg_sleep_start = int(input ("Average Bed time (0-24): "))
avg_sleep_end = int(input ("Average Wake up time (0-24): "))

"""
#FLIGHT TABLE
flightTableSql = """
#INSERT INTO flight_table
#(origin_city, destination_city, departure_datetime, arrival_datetime,
#flight_hours, direction, pre_adjust_days, post_adjust_days)
#VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
"""

flightTableVal = (origin, destination, depart_datetime, arrival_datetime,
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

#PRE FLIGHT PLAN TABLE
#TO DO - CLEAN UP CODE

shift_hours = 1
pre_sleep_start = 0
pre_sleep_end = 0


datetime_convert = datetime.strptime(depart_datetime, "%Y-%m-%d %H:%M:%S")
shifted_date = datetime_convert.date()

#east means sleep early
if direction == "east":
    for i in range(pre_days):
        next_day = shifted_date - timedelta(days= pre_days - i)

        print(next_day.month,"/",next_day.day)

        avg_sleep_start = (avg_sleep_start - shift_hours) % 24
        avg_sleep_end = (avg_sleep_end - shift_hours) % 24

        hours_start = int(avg_sleep_start)
        minutes_start = int((avg_sleep_start - hours_start) * 60)
        hours_end = int(avg_sleep_end)
        minutes_end = int((avg_sleep_end - hours_end) * 60)

        print(f"pre_sleep_start time: {hours_start:02d}:{minutes_start:02d}")
        print(f"pre_sleep_end time: {hours_end:02d}:{minutes_end:02d}")

        stop_caffeine = (avg_sleep_start - 6) % 24
        stop_nap = (avg_sleep_start - 8) % 24

        sc_hours = int(stop_caffeine)
        sc_minutes = int((stop_caffeine - sc_hours) * 60)
        sn_hours = int(stop_nap)
        sn_minutes = int((stop_nap - sn_hours) * 60)

        print(f"no caffeine after: {sc_hours:02d}:{sc_minutes:02d}")
        print(f"no power naps after: {sn_hours:02d}:{sn_minutes:02d}")

#west means sleep later
elif direction == "west":
    for i in range(pre_days):
        next_day = shifted_date - timedelta(days= pre_days - i)
        print(next_day.month,"/",next_day.day)

        avg_sleep_start = (avg_sleep_start + shift_hours) % 24
        avg_sleep_end = (avg_sleep_end + shift_hours) % 24

        hours_start = int(avg_sleep_start)
        minutes_start = int((avg_sleep_start - hours_start) * 60)
        hours_end = int(avg_sleep_end)
        minutes_end = int((avg_sleep_end - hours_end) * 60)

        print(f"pre_sleep_start time: {hours_start:02d}:{minutes_start:02d}")
        print(f"pre_sleep_end time: {hours_end:02d}:{minutes_end:02d}")

        stop_caffeine = (avg_sleep_start - 6) % 24
        stop_nap = (avg_sleep_start - 8) % 24

        sc_hours = int(stop_caffeine)
        sc_minutes = int((stop_caffeine - sc_hours) * 60)
        sn_hours = int(stop_nap)
        sn_minutes = int((stop_nap - sn_hours) * 60)

        print(f"no caffeine after: {sc_hours:02d}:{sc_minutes:02d}")
        print(f"no power naps after: {sn_hours:02d}:{sn_minutes:02d}")
else:
    print("Flight direction must be east or west, try again.")





"""
Post-Flight Plan PseudoCode
1. Let post flight plan be fixed according to the [avg_sleep_schedule] of the local time
2. Adjust the range of nap time/caffeine intake according to the [post_adjust_days], does not matter if east or westward
3. Could include the recommended time period to get sunlight
"""