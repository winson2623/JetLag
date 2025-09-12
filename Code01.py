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
origin = "Los Angeles"
destination = "Taipei"
depart_datetime = "2025-09-12 01:00:00"
arrival_datetime = "2025-09-13 05:00:00"
flight_hours = 13
direction = "west"
pre_days = 3
post_days = 3
avg_sleep_start = "22:00"
avg_sleep_end = "6:00"


sql = """
INSERT INTO flight_table
(origin_city, destination_city, departure_datetime, arrival_datetime,
 flight_hours, direction, pre_adjust_days, post_adjust_days)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
"""

val = (origin, destination, depart_datetime, arrival_datetime,
       flight_hours,direction, pre_days, post_days)

my_cursor.execute(sql, val)
mydb.commit()

print(my_cursor.rowcount, " flight record inserted.")

