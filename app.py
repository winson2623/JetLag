from flask import Flask, request, jsonify
from flask_cors import CORS
from flightplan import FLIGHTPLAN
import mysql.connector

app = Flask(__name__)
CORS(app)  # allows frontend from different origin (like GitHub Pages) to access backend

# ---------------------------------------
# MySQL Connection (adjust credentials)
# ---------------------------------------
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="root1234",
    database="jetlagdb"
)
my_cursor = mydb.cursor()

# ---------------------------------------
# API Route
# ---------------------------------------
@app.route("/submit", methods=["POST"])
def submit():
    data = request.get_json()

    # initialize and run your logic
    my_flight = FLIGHTPLAN()
    my_flight.flightSchedule(
        data["name"], data["origin"], data["destination"],
        data["depart_datetime"], int(data["flight_hours"]),
        data["direction"], int(data["pre_days"]), int(data["post_days"]),
        int(data["avg_sleep_start"]), int(data["avg_sleep_end"])
    )

    my_flight.preFlightSchedule()
    my_flight.postFlightSchedule()

    # save into MySQL (like your Tkinter version)
    inputTableSql = """
        INSERT INTO input_table
        (name, origin, destination, depart_datetime, flight_hours,
        direction, pre_days, post_days, avg_sleep_start, avg_sleep_end)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    inputTableVal = (
        data["name"], data["origin"], data["destination"], data["depart_datetime"],
        data["flight_hours"], data["direction"], data["pre_days"], data["post_days"],
        data["avg_sleep_start"], data["avg_sleep_end"]
    )

    my_cursor.execute(inputTableSql, inputTableVal)
    mydb.commit()
    flight_id = my_cursor.lastrowid

    # Insert pre-flight schedule
    for entry in my_flight.pre_schedule:
        my_cursor.execute(
            "INSERT INTO pre_table(flight_id, date, pre_sleep_start, pre_sleep_end, no_caffeine, no_nap) VALUES (%s,%s,%s,%s,%s,%s)",
            (flight_id, entry["date"], entry["pre_sleep_start"], entry["pre_sleep_end"], entry["no_caffeine"], entry["no_nap"])
        )
    mydb.commit()

    # Insert post-flight schedule
    for entry in my_flight.post_schedule:
        my_cursor.execute(
            "INSERT INTO post_table(flight_id, date, post_sleep_start, post_sleep_end, no_nap, sunlight) VALUES (%s,%s,%s,%s,%s,%s)",
            (flight_id, entry["date"], entry["post_sleep_start"], entry["post_sleep_end"], entry["nap_cutoff"], entry["sunlight"])
        )
    mydb.commit()

    # Return results as JSON
    return jsonify({
        "message": "Flight schedule saved!",
        "flight_id": flight_id,
        "pre_schedule": my_flight.pre_schedule,
        "post_schedule": my_flight.post_schedule
    })

# ---------------------------------------
# Run server
# ---------------------------------------python app.py
if __name__ == "__main__":
    app.run(debug=True)
