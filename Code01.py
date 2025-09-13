import mysql.connector

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
depart_datetime = input ("Departure Date and Time: (YYYY-MM-DD HH:MM:SS): ")
arrival_datetime = input ("Arrival Date and Time: (YYYY-MM-DD HH:MM:SS): ")
flight_hours = float(input("Flight Hours: "))
direction = input ("Flight Direction: ")
pre_days = int(input("pre-adjust days: "))
post_days = int(input("post-adjust days: "))

avg_sleep_start = input ("Average Bed time (HH:MM): ")
avg_sleep_end = input ("Average Wake up time (HH:MM): ")

#FLIGHT TABLE
flightTableSql = """
INSERT INTO flight_table
(origin_city, destination_city, departure_datetime, arrival_datetime,
 flight_hours, direction, pre_adjust_days, post_adjust_days)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
"""

flightTableVal = (origin, destination, depart_datetime, arrival_datetime,
       flight_hours,direction, pre_days, post_days)

#USER TABLE
userTableSql = """
INSERT INTO user_table(user_name, average_sleep_start, average_sleep_end)VALUES (%s, %s, %s)
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
INSERT INTO sleep_plan_table(flight_id, user_id, user_name)VALUES (%s, %s, %s)
"""

sleepTableVal = (flight_id, user_id, name)


my_cursor.execute(sleepTableSql, sleepTableVal)
mydb.commit()
plan_id = my_cursor.lastrowid  # ID of the newly inserted flight
print("Inserted plan_id:", plan_id)

print(my_cursor.rowcount, " flight record inserted.")

"""
Pre-Flight Plan PseudoCode
1. using the input data from input to create [pre_flight_schedule]
2. decide the shift hours per day, lets say 1 hour per day according to [pre_days] input
3. if flight direction is east, go to bed early -X hours, if flight west go to bed later +X hours per day.
4. loop a table that creates suggested [pre_sleep_start] [pre_sleep_end] [notes]
    [pre_sleep_start] = [avg_sleep_start] east- or west+ ([shift_hours] * [pre_days])
                    example: 22 east- (1 * 3) = 19 is start of loop for column [pre_sleep_start]
    [pre_sleep_end] = [avg_sleep_end] east- or west+ ([shift_hours] * [pre_days])
                    example: 6 east- (1 * 3) = 3 is start of loop for column [pre_sleep_end]
    [notes]    = [pre_sleep_start] - 6 hours = stop_caffeine      example 19 - 6 = "no caffeine after 13
               = [pre_sleep_start] - 8 hours = stop_nap          example 19 - 8 = "no naps after 11
"""

"""
Post-Flight Plan PseudoCode
1. Let post flight plan be fixed according to the [avg_sleep_schedule] of the local time
2. Adjust the range of nap time/caffeine intake according to the [post_adjust_days], does not matter if east or westward
3. Could include the recommended time period to get sunlight
"""