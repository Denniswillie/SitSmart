import os
import uuid
import threading

from flask import Flask, render_template, request, redirect, session
from flask_session import Session
from routes import location_api, booking_api, studyTable_api
from db_managers import LocationManager
from global_init import mysql, mail
from pubnub.pnconfiguration import PNConfiguration
from pubnub_handler import PubnubHandler

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'sit_smart'
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
pubnub_config.publish_key = "pub-c-94051755-9540-4114-bbc2-58edb0260e91"
pubnub_config.subscribe_key = "sub-c-fe5caef8-3a61-11ec-b2c1-a25c7fcd9558"
pubnub_config.uuid = str(uuid.uuid4())
pubnub_handler = PubnubHandler(mysql, pubnub_config, app)


@app.route("/")
def index():
    # session.clear()
    if not session.get('email'):
        return redirect("/register")
    return render_template("booking_screen.html")


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
    if "is_redirect" in request.args and request.args["is_redirect"] is True:
        bookings = {}
        for key, value in request.args.items():
            if key.startswith("study_table_name"):
                bookings[request.args.get(key)] = []

        for key, value in request.args.items():
            if key.startswith("times"):
                study_table_name = key.split("-")[-1]
                start_time = request.args.get(key).split("until")[0]
                end_time = request.args.get(key).split("until")[1]
                bookings[study_table_name].append([start_time, end_time])

        return render_template(
            "receipt_screen.html",
            study_table_name=request.args["study_table_name"],
            location_name=request.args["location_name"],
            booking_date=request.args["booking_date"],
            bookings=bookings,
            booking_password=request.args["booking_password"],
            email_address=session.get("email")
        )
    else:
        return redirect("/register")


app.register_blueprint(location_api, url_prefix='/location')
app.register_blueprint(booking_api, url_prefix='/booking')
app.register_blueprint(studyTable_api, url_prefix='/studyTable')

if __name__ == "__main__":
    # Subscribe pubnub handler to channel
    pubnub_handler_subscribe_thread = threading.Thread(target=pubnub_handler.subscribe(CHANNEL))
    pubnub_handler_subscribe_thread.start()
    app.run(debug=True, use_reloader=False)
