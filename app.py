import json
import os

from flask import Flask, render_template, request, redirect, session
from flask_mysqldb import MySQL
from flask_mail import Mail, Message
from flask_session import Session
from entities import Location, StudyTable
from db_managers import LocationManager, StudyTableManager

app = Flask(__name__)
mysql = MySQL(app)
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
Session(app)

mail = Mail(app)
INTERNAL_ERR_CODE = 500
OK_STATUS_CODE = 200
SUCCESSFUL_CREATION_STATUS_CODE = 201


@app.route("/")
def index():
    if not session.get('email'):
        return redirect("/register")
    return render_template("booking.html")


@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        email = request.form.get("email")
        session["email"] = email
        return redirect("/booking")
    # handle GET request
    else:
        if session.get('email'):
            return redirect("/booking")
        return render_template("register.html")


@app.route("/receipt")
def receipt_screen():
    return render_template("receipt.html")


# ---------------------Location APIs----------------------#
@app.route("/location", methods=["POST"])
def create_location():
    name = request.form.get("location_name")
    location = Location(name)
    location_manager = LocationManager(mysql)
    try:
        location_id = location_manager.create_location(location)
        return json.dumps({
            "statusCode": SUCCESSFUL_CREATION_STATUS_CODE,
            "message": "Your new table ID is " + str(location_id)
        })
    except Exception as e:
        err_msg = str(e) if len(str(e)) > 0 else "an unexpected error has occurred"
        return json.dumps({
            "statusCode": INTERNAL_ERR_CODE,
            "message": err_msg
        })


@app.route("/editLocation", methods=["POST"])
def edit_location():
    try:
        location_name = request.form.get("location_name")
        location_id = int(request.form.get("location_id"))
        location = Location(location_name, location_id)
        location_manager = LocationManager(mysql)
        location_manager.edit_location(location)
        return json.dumps({
            "statusCode": OK_STATUS_CODE,
            "message": "Successfully edited"
        })
    except Exception as e:
        err_msg = str(e) if len(str(e)) > 0 else "an unexpected error has occurred"
        return json.dumps({
            "statusCode": INTERNAL_ERR_CODE,
            "message": err_msg
        })


@app.route("/removeLocation", methods=["DELETE"])
def remove_location():
    try:
        location_id = int(request.form.get("location_id"))
        location_manager = LocationManager(mysql)
        location_manager.remove_location(location_id)
        return json.dumps({
            "statusCode": OK_STATUS_CODE,
            "message": "Successfully removed"
        })
    except Exception as e:
        err_msg = str(e) if len(str(e)) > 0 else "an unexpected error has occurred"
        return json.dumps({
            "statusCode": INTERNAL_ERR_CODE,
            "message": err_msg
        })


# ---------------------StudyTable APIs----------------------#
@app.route("/studyTable", methods=["POST"])
def create_table():
    location_id = request.form.get("location_id")
    study_table_name = request.form.get("study_table_name")
    mac_address = request.form.get("mac_address")
    study_table = StudyTable(study_table_name, location_id, mac_address)
    study_table_manager = StudyTableManager(mysql)
    try:
        study_table_manager.create_study_table(study_table)
        return json.dumps({
            "statusCode": SUCCESSFUL_CREATION_STATUS_CODE,
            "message": "Successfully created a new table"
        })
    except Exception as e:
        err_msg = str(e) if len(str(e)) > 0 else "an unexpected error has occurred"
        return json.dumps({
            "statusCode": INTERNAL_ERR_CODE,
            "message": err_msg
        })


@app.route("/getTableInfo", methods=["POST"])
def table_info():
    mac_address = request.form.get("mac_address")
    study_table_manager = StudyTableManager(mysql)
    try:
        res = study_table_manager.get_table_info(mac_address)
        return json.dumps({
            "statusCode": OK_STATUS_CODE,
            "result": res
        })
    except Exception as e:
        err_msg = str(e) if len(str(e)) > 0 else "an unexpected error has occurred"
        return json.dumps({
            "statusCode": INTERNAL_ERR_CODE,
            "message": err_msg
        })


@app.route("/removeTable", methods=["DELETE"])
def remove_table():
    study_table_id = request.form.get("study_table_id")
    study_table_manager = StudyTableManager(mysql)
    try:
        study_table_manager.remove_study_table(study_table_id)
        return json.dumps({
            "statusCode": OK_STATUS_CODE,
            "message": "Successfully removed a table"
        })
    except Exception as e:
        err_msg = str(e) if len(str(e)) > 0 else "an unexpected error has occurred"
        return json.dumps({
            "statusCode": INTERNAL_ERR_CODE,
            "message": err_msg
        })


app.run(debug=True)
