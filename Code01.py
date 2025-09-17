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

#MAKE THIS STRUCT?
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
shift_hours = 1
pre_sleep_start = avg_sleep_start
pre_sleep_end = avg_sleep_end

datetime_convert = datetime.strptime(depart_datetime, "%Y-%m-%d %H:%M:%S")
shifted_date = datetime_convert.date()

def format_time(decimal_hour):
    hours = int(decimal_hour)
    minutes = int((decimal_hour - hours) * 60)
    return f"{hours:01d}:{minutes:02d}"

if direction == "east": #east means sleep earlier
    shift_direction = -1
elif direction == "west": #west means sleep later
    shift_direction = +1
else:
    print("Direction must be east or west, try again.")
    shift_direction = 0


if shift_direction:
    for i in range(pre_days):
        next_day = shifted_date - timedelta(days= pre_days - i)
        print(next_day.month,"/",next_day.day)

        #shift sleep times
        pre_sleep_start = (pre_sleep_start + (shift_direction * shift_hours)) % 24
        pre_sleep_end = (pre_sleep_end + (shift_direction * shift_hours)) % 24

        print(f"pre_sleep_start time: ", format_time(pre_sleep_start))
        print(f"pre_sleep_end time: ", format_time(pre_sleep_end))

        #caffine & nap cut off time
        stop_caffeine = (avg_sleep_start - 6) % 24
        stop_nap = (avg_sleep_start - 8) % 24

        print(f"no caffeine after: ", format_time(stop_caffeine))
        print(f"no power naps after: ", format_time(stop_nap))



#POST FLIGHT TIME SCHEDULE
print()
print (f"post_sleep_start time: ", format_time(avg_sleep_start))
print(f"post_sleep_end time: ", format_time(avg_sleep_end))

if direction == "east": #east means sleep earlier
    get_light = 1
    nap_cutoff = avg_sleep_start - 6
    for i in range(pre_days):
        #LET NAP TiME BE A RANGE like 12:00-15:00 and let get light also be a range before NAP TIME like 9:00-12:00
        print(f"nap_cutoff time: ", format_time(nap_cutoff))
        print(f"get sunlight between: ", format_time(get_light), "and", format_time(nap_cutoff))
        nap_cutoff = nap_cutoff - shift_hours
        get_light = nap_cutoff - 3
elif direction == "west":
    print("Try not to take naps")
else:
    print("Direction must be east or west, try again.")



"""
Post-Flight Plan PseudoCode
1. Let post flight plan be fixed according to the [avg_sleep_schedule] of the local time
2. Adjust the range of nap time/caffeine intake according to the [post_adjust_days], does not matter if east or westward
3. Could include the recommended time period to get sunlight
"""