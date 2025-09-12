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

