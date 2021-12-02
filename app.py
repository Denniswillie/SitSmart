import json
import os
import uuid
import threading
from dotenv import load_dotenv

from flask import Flask, render_template, request, redirect, session, url_for
from flask_session import Session
from flask_cors import CORS
from routes import location_api, booking_api, studyTable_api, tableKit
from db_managers import LocationManager, SitSmartUserManager
from global_init import mysql, mail
from pubnub.pnconfiguration import PNConfiguration
from pubnub_handler import PubnubHandler
from authlib.integrations.flask_client import OAuth
from entities import SitSmartUser

load_dotenv()
app = Flask(__name__)
cors = CORS(app)
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_params=None,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    userinfo_endpoint='https://openidconnect.googleapis.com/v1/userinfo',
    # This is only needed if using openId to fetch user info
    client_kwargs={'scope': 'openid email profile'},
)

app.config['MYSQL_HOST'] = os.getenv("MYSQL_HOST")
app.config['MYSQL_USER'] = os.getenv("MYSQL_USER")
app.config['MYSQL_PASSWORD'] = os.getenv("MYSQL_PASSWORD")
app.config['MYSQL_DB'] = os.getenv("MYSQL_DB")
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
pubnub_config.publish_key = os.getenv("PUBNUB_PUBLISH_KEY")
pubnub_config.subscribe_key = os.getenv("PUBNUB_SUBSCRIBE_KEY")
pubnub_config.uuid = str(uuid.uuid4())
pubnub_handler = PubnubHandler(mysql, pubnub_config, app)




@app.route("/")
def index():
    if not session.get('email'):
        return redirect("/register")
    return render_template("booking.html")


@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        location_id = request.form.get("location_id")
        session["location_id"] = location_id
        print("this is the location_id: ",  location_id)
        return json.dumps({
            "stored": True
        })
    # handle GET request
    else:
        if session.get('email'):
            return redirect("/booking")
        location_manager = LocationManager(mysql)
        return render_template("index.html", locations=location_manager.get_available_locations())


@app.route('/login')
def login():
    google = oauth.create_client('google')  # create the google oauth client
    redirect_uri = url_for('authorize', _external=True)
    return google.authorize_redirect(redirect_uri)


@app.route('/authorize')
def authorize():
    google = oauth.create_client('google')  # create the google oauth client
    token = google.authorize_access_token()  # Access token from google (needed to get user info)
    resp = google.get('userinfo')  # userinfo contains stuff u specificed in the scrope
    user_info = resp.json()
    user = oauth.google.userinfo()  # uses openid endpoint to fetch user info
    # Here you use the profile/user data that you got and query your database find/register the user
    # and set ur own data in the session not the profile from google
    print(user_info)
    session['email'] = user_info['email']

    sit_smart_user_manager = SitSmartUserManager(mysql)
    sit_smart_user = SitSmartUser(email=user_info["email"])
    sit_smart_user_id = sit_smart_user_manager.create_user_if_not_exists(sit_smart_user)
    session['sit_smart_user_id'] = sit_smart_user_id
    session.permanent = True

    return redirect('/')


@app.route("/receipt")
def receipt_screen():
    if "bookings_confirmation" in session:
        bookings = {}
        for study_table_id, booking_data in session["bookings_confirmation"]["bookings"].items():
            study_table_name = booking_data["studyTableName"]
            bookings[study_table_name] = []

            # pre-process booking times (group adjacent booking times into one booking)
            pre_processed_times = []
            curr_start_time = 0
            for i, (start_time, end_time) in enumerate(booking_data["times"]):
                if i == 0:
                    curr_start_time = start_time
                elif start_time != booking_data["times"][i - 1][1]:
                    pre_processed_times.append([curr_start_time, booking_data["times"][i - 1][1]])
                    curr_start_time = start_time
            pre_processed_times.append([curr_start_time, booking_data["times"][-1][1]])

            for start_time, end_time in pre_processed_times:
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
app.register_blueprint(tableKit, url_prefix='/tableKit')


# For gunicorn post work hook (to be called after app.run() is called
def subscribe_pubnub():
    pubnub_handler_subscribe_thread = threading.Thread(target=pubnub_handler.subscribe(CHANNEL))
    pubnub_handler_subscribe_thread.start()


if __name__ == "__main__":
    # Subscribe pubnub handler to channel
    pubnub_handler_subscribe_thread = threading.Thread(target=pubnub_handler.subscribe(CHANNEL))
    pubnub_handler_subscribe_thread.start()
    app.run(debug=True, use_reloader=False)
