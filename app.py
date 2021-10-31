import json
import os

from flask import Flask, render_template, request, redirect,session
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
internal_err_code = 500
ok_status_code = 200
successful_creation_status_code = 201


@app.route("/")
def index():
    if not session.get('email'):
        return redirect("/startScreen")
    return render_template("bookingScreen.html")


@app.route("/startScreen")
def startScreen():
    return render_template("startScreen.html")


@app.route("/register", methods=["POST"])
def register():
    email = request.form.get("email")
    session["email"] = email
    return redirect("/bookingScreen")


@app.route("/bookingScreen")
def bookingScreen():
    return render_template("booking_screen.html")


@app.route("/receiptScreen")
def receiptScreen():
    return render_template("receipt_screen.html")


# ---------------------Location APIs----------------------#
@app.route("/location", methods=["POST"])
def location():
    name = request.form.get("location")
    location = Location(name)
    location_manager = LocationManager(mysql)
    try:
        return_id = location_manager.create_location(location)
        return json.dumps({
            "statusCode": successful_creation_status_code,
            "message": "Your new table ID is " + str(return_id)
        })
    except Exception as e:
        err_msg = str(e) if len(str(e)) > 0 else "an unexpected error has occurred"
        return json.dumps({
            "statusCode": internal_err_code,
            "message": err_msg
        })


@app.route("/editLocation", methods=["POST"])
def editLocation():
    name = request.form.get("location")
    id = request.form.get("location_id")
    location = Location(name, id)
    location_manager = LocationManager(mysql)
    try:
        location_manager.edit_location(location)
        return json.dumps({
            "statusCode": ok_status_code,
            "message": "Successfully edited"
        })
    except Exception as e:
        err_msg = str(e) if len(str(e)) > 0 else "an unexpected error has occurred"
        return json.dumps({
            "statusCode": internal_err_code,
            "message": err_msg
        })


@app.route("/removeLocation", methods=["DELETE"])
def removeLocation():
    id = request.form.get("location_id")
    try:
        location_manager = LocationManager(mysql)
        location_manager.remove_location(id)
        return json.dumps({
            "statusCode": ok_status_code,
            "message": "Successfully removed"
        })
    except Exception as e:
        err_msg = str(e) if len(str(e)) > 0 else "an unexpected error has occurred"
        return json.dumps({
            "statusCode": internal_err_code,
            "message": err_msg
        })


# ---------------------StudyTable APIs----------------------#
@app.route("/studyTable", methods=["POST"])
def createTable():
    locationId = request.form.get("locationId")
    tableId = request.form.get("tableId")
    macAddress = request.form.get("macAddress")
    studyTable = StudyTable(tableId, locationId, macAddress)
    studyTable_manager = StudyTableManager(mysql)
    try:
        studyTable_manager.create_study_table(studyTable)
        return json.dumps({
            "statusCode": successful_creation_status_code,
            "message": "Successfully created a new table"
        })
    except Exception as e:
        err_msg = str(e) if len(str(e)) > 0 else "an unexpected error has occurred"
        return json.dumps({
            "statusCode": internal_err_code,
            "message": err_msg
        })


@app.route("/getTableInfo", methods=["POST"])
def tableInfo():
    macAddress = request.form.get("macAddress")
    studyTable_manager = StudyTableManager(mysql)
    try:
        res = studyTable_manager.get_table_info(macAddress)
        return json.dumps({
            "statusCode": ok_status_code,
            "result": res
        })
    except Exception as e:
        err_msg = str(e) if len(str(e)) > 0 else "an unexpected error has occurred"
        return json.dumps({
            "statusCode": internal_err_code,
            "message": err_msg
        })


@app.route("/removeTable", methods=["DELETE"])
def removeTable():
    id = request.form.get("table_id")
    studyTable_manager = StudyTableManager(mysql)
    try:
        studyTable_manager.remove_study_table(id)
        return json.dumps({
            "statusCode": ok_status_code,
            "message": "Successfully removed a table"
        })
    except Exception as e:
        err_msg = str(e) if len(str(e)) > 0 else "an unexpected error has occurred"
        return json.dumps({
            "statusCode": internal_err_code,
            "message": err_msg
        })


app.run(debug=True)
