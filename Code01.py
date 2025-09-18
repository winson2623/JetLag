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

#MAKE THIS CLASS? DONT MAKE IT GLOBAL VARIABLES
#user input for flight_table
#name = input("Enter Name: ")
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

#PRE FLIGHT PLAN TABLE
shift_hours = 1
pre_sleep_start = avg_sleep_start
pre_sleep_end = avg_sleep_end

def calculate_arrival():
    # Parse departure datetime (naive → no tzinfo yet)
    depart_dt = datetime.strptime(depart_datetime, "%Y-%m-%d %H:%M")

    # Attach departure timezone
    depart_dt = depart_dt.replace(tzinfo=ZoneInfo(origin))

    # Add flight duration to origin timezone
    arrival_dt = depart_dt + timedelta(hours=flight_hours)

    # Convert to destination timezone
    arrival_dt = arrival_dt.astimezone(ZoneInfo(destination))

    return depart_dt, arrival_dt

depart_dt, arrival_dt = calculate_arrival()


post_shifted_date = arrival_dt.date()
pre_shifted_date = depart_dt.date()


def format_time(decimal_hour):
    hours = int(decimal_hour)
    minutes = int((decimal_hour - hours) * 60)
    return f"{hours:01d}:{minutes:02d}"

def military_time(time_value, shift):
    return (time_value + shift) % 24

if direction == "east": #east means sleep earlier
    shift_direction = -1
elif direction == "west": #west means sleep later
    shift_direction = +1
else:
    print("Direction must be east or west, try again.")
    shift_direction = 0


if shift_direction:
    for i in range(pre_days):
        next_day = pre_shifted_date - timedelta(days= pre_days - i)
        print(next_day.month,"/",next_day.day)

        #shift sleep times
        pre_sleep_start = military_time(pre_sleep_start, shift_direction * shift_hours)
        pre_sleep_end = military_time(pre_sleep_end, shift_direction * shift_hours)

        print(f"pre_sleep_start time: ", format_time(pre_sleep_start))
        print(f"pre_sleep_end time: ", format_time(pre_sleep_end))

        #caffine & nap cut off time
        stop_caffeine = military_time(pre_sleep_start, -6)
        stop_nap = military_time(pre_sleep_start, -8)

        print(f"no caffeine after: ", format_time(stop_caffeine))
        print(f"no power naps after: ", format_time(stop_nap))


print()
print("YOUR FLIGHT IS ON: ", depart_dt.strftime("%Y-%m-%d %H:%M %Z"),
      " AND WILL ARRIVE ON: ", arrival_dt.strftime("%Y-%m-%d %H:%M %Z"))
print()
print (f"post_sleep_start time: ", format_time(avg_sleep_start))
print(f"post_sleep_end time: ", format_time(avg_sleep_end))

#POST FLIGHT TIME SCHEDULE
if direction == "east": #east means sleep earlier
    nap_cutoff = avg_sleep_start - 6
    get_light = nap_cutoff - 6
    for i in range(post_days):
        next_day = post_shifted_date + timedelta(days = i)
        print(next_day.month, "/", next_day.day)

        print(f"nap_cutoff time: ", format_time(nap_cutoff))
        print(f"get sunlight between: ", format_time(get_light), "and", format_time(nap_cutoff - 3))

        nap_cutoff = military_time(nap_cutoff, -1)
        get_light = military_time(nap_cutoff, -6)

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