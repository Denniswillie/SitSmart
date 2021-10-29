import json

from flask import Flask, render_template, request, redirect
from flask_mysqldb import MySQL
from flask_mail import Mail, Message
from entities import Location, StudyTable
from db_managers import LocationManager, StudyTableManager

app = Flask(__name__)
mysql = MySQL(app)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'sit_smart'

mail = Mail(app)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/bookingScreen")
def bookingScreen():
    email = request.form.get("email")
    return render_template("booking_screen.html")


@app.route("/receipt")
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
            "statusCode": 201,
            "description": "Your new table ID is " + str(return_id)
        })
    except Exception as e:
        err_msg = str(e) if len(str(e)) > 0 else "an unexpected error has occurred"
        return json.dumps({
            "statusCode": 500,
            "description": err_msg
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
            "statusCode": 200,
            "description": "Successfully edited"
        })
    except Exception as e:
        err_msg = str(e) if len(str(e)) > 0 else "an unexpected error has occurred"
        return json.dumps({
            "statusCode": 500,
            "description": err_msg
        })


@app.route("/removeLocation", methods=["DELETE"])
def removeLocation():
    id = request.form.get("location_id")
    try:
        location_manager = LocationManager(mysql)
        location_manager.remove_location(id)
        return json.dumps({
            "statusCode": 200,
            "description": "Successfully removed"
        })
    except Exception as e:
        err_msg = str(e) if len(str(e)) > 0 else "an unexpected error has occurred"
        return json.dumps({
            "statusCode": 500,
            "description": err_msg
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
            "statusCode": 201,
            "description": "Successfully created a new table"
        })
    except Exception as e:
        err_msg = str(e) if len(str(e)) > 0 else "an unexpected error has occurred"
        return json.dumps({
            "statusCode": 500,
            "description": err_msg
        })


@app.route("/getTableInfo", methods=["POST"])
def tableInfo():
    macAddress = request.form.get("macAddress")
    studyTable_manager = StudyTableManager(mysql)
    try:
        res = studyTable_manager.get_table_info(macAddress)
        return json.dumps({
            "statusCode": 200,
            "info": res
        })
    except Exception as e:
        err_msg = str(e) if len(str(e)) > 0 else "an unexpected error has occurred"
        return json.dumps({
            "statusCode": 500,
            "description": err_msg
        })


@app.route("/removeTable", methods=["DELETE"])
def removeTable():
    id = request.form.get("table_id")
    studyTable_manager = StudyTableManager(mysql)
    try:
        studyTable_manager.remove_study_table(id)
        return json.dumps({
            "statusCode": 200,
            "description": "Successfully removed a table"
        })
    except Exception as e:
        err_msg = str(e) if len(str(e)) > 0 else "an unexpected error has occurred"
        return json.dumps({
            "statusCode": 500,
            "description": err_msg
        })


app.run(debug=True)
