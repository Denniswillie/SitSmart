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


pubnub_handler.subscribe(CHANNEL)