import os
import uuid
import threading

from flask import Flask, render_template, request, redirect, session
from flask_session import Session
from flask_cors import CORS
from routes import location_api, booking_api, studyTable_api
from db_managers import LocationManager
from global_init import mysql, mail
from pubnub.pnconfiguration import PNConfiguration
from pubnub_handler import PubnubHandler

app = Flask(__name__)
cors = CORS(app)

app.config['MYSQL_HOST'] = 'us-cdbr-east-04.cleardb.com'
app.config['MYSQL_USER'] = 'b64b251ec004bb'
app.config['MYSQL_PASSWORD'] = '151814c3'
app.config['MYSQL_DB'] = 'heroku_61619fb58469271'
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_POST'] = 587
app.config['MAIL_SERVER'] = "smtp.gmail.com"
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = "filesystem"

mail.init_app(app)
mysql.init_app(app)
Session(app)

CHANNEL = "sitsmart_sensors_data_channel"
pubnub_config = PNConfiguration()
pubnub_config.publish_key = "pub-c-9216e21f-73cf-4bfd-a909-b08f59eb9a22"
pubnub_config.subscribe_key = "sub-c-12216cc6-5074-11ec-b60b-aa41d66f579f"
pubnub_config.uuid = str(uuid.uuid4())
pubnub_handler = PubnubHandler(mysql, pubnub_config, app)


@app.route("/")
def index():
    # session.clear()
    if not session.get('email'):
        return redirect("/register")
    return render_template("booking.html")


@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        email_address = request.form.get("email")
        location_id = request.form.get("locations")
        session["email"] = email_address
        session["location_id"] = location_id
        return redirect("/booking")
    # handle GET request
    else:
        if session.get('email'):
            return redirect("/booking")
        location_manager = LocationManager(mysql)
        return render_template("index.html", locations=location_manager.get_available_locations())


@app.route("/receipt")
def receipt_screen():
    if "bookings_confirmation" in session:
        bookings = {}
        for study_table_id, booking_data in session["bookings_confirmation"]["bookings"].items():
            study_table_name = booking_data["studyTableName"]
            bookings[study_table_name] = []
            for start_time, end_time in booking_data["times"]:
                if start_time > 12:
                    start_time_string = "{}pm".format(start_time - 12)
                elif start_time == 12:
                    start_time_string = "12pm"
                else:
                    start_time_string = "{}am".format(start_time)
                if end_time > 12:
                    end_time_string = "{}pm".format(end_time - 12)
                elif end_time == 12:
                    end_time_string = "12pm"
                else:
                    end_time_string = "{}am".format(end_time)
                bookings[study_table_name].append([start_time_string, end_time_string])

        booking_confirmation = session["bookings_confirmation"]
        location_name = booking_confirmation["location_name"]
        booking_date = booking_confirmation["booking_date"]
        booking_password = booking_confirmation["booking_password"]
        del session["bookings_confirmation"]
        session.modified = True

        return render_template(
            "receipt_screen.html",
            location_name=location_name,
            booking_date=booking_date,
            bookings=bookings,
            booking_password=booking_password,
            email_address=session.get("email")
        )
    else:
        return redirect("/register")


app.register_blueprint(location_api, url_prefix='/location')
app.register_blueprint(booking_api, url_prefix='/booking')
app.register_blueprint(studyTable_api, url_prefix='/studyTable')

if __name__ == "__main__":
    # Subscribe pubnub handler to channel
    pubnub_handler.subscribe(CHANNEL)
    app.run(use_reloader=False)
