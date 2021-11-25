import secrets
import string
import json

from global_init import mysql, mail
from flask import Blueprint, request, redirect, url_for, render_template, session
from .enums import StatusCode
from db_managers import BookingManager, StudyTableManager
from entities import Booking
from flask_mail import Message

booking_api = Blueprint('booking_api', __name__)


@booking_api.route("/", methods=["POST", "GET", "DELETE"])
def handle_booking():
    booking_manager = BookingManager(mysql)
    # handle create booking
    if request.method == "POST":
        data = request.get_json(silent=True)
        email_address = session.get("email")
        study_table_id = data.get("study_table_id")
        study_table_name = data.get("study_table_name")
        location_name = data.get("location_name")

        # code snippet inspiration from https://stackoverflow.com/questions/2257441/random-string-generation-with
        # -upper-case-letters-and-digits
        # The idea is to generate 4 random base36 digits resulting in (36 ^ 4) password possibilities.
        booking_password = "".join(secrets.choice(string.digits + string.ascii_uppercase) for _ in range(4))

        times = data.get("times")
        for start_time, end_time in times:
            booking = Booking(
                booking_password,
                study_table_id,
                start_time,
                end_time,
            )
            booking_manager.create_booking(booking)

        # send confirmation email
        message_string = "You have booked table {} in {} on the following times:\n".format(
            study_table_name,
            location_name
        )
        for index, (start_time, end_time) in enumerate(times):
            message_string += "{}. {} until {}\n".format(index + 1, start_time, end_time)
        message_string += "Your booking password is {}".format(booking_password)
        message = Message(
            message_string,
            recipients=[email_address])
        mail.send(message)

        response_data = {
            "is_redirect": True,
            "study_table_name":study_table_name,
            "location_name": location_name,
            "booking_password": booking_password
        }

        for times_index, (start_time, end_time) in times:
            response_data["times" + times_index] = start_time+"until"+end_time

        # redirect to receipt screen
        return redirect(url_for(
            "receipt_screen",
            **response_data
        ))

    # handle remove booking
    elif request.method == "DELETE":
        booking_id = int(request.form.get("booking_id"))
        booking_manager.remove_booking(booking_id)
        return json.dumps({
            "statusCode": StatusCode.OK_STATUS_CODE,
            "message": "booking has successfully been deleted"
        })

    # handle get booking screen
    elif request.method == "GET":
        return render_template("booking_screen.html")

    return json.dumps({
        "statusCode": StatusCode.INTERNAL_ERR_CODE,
        "message": "API method handler does not exist for this route"
    })


@booking_api.route("/available_tables")
def get_available_tables():
    # booking_date must be in the format "YYYY-MM-DD"
    booking_date = str(request.form.get("booking_date"))
    location_id = session["location_id"]
    study_table_manager = StudyTableManager(mysql)
    study_tables_at_location = study_table_manager.get_study_tables_in_location(location_id)
    result = dict()
    for study_table_data in study_tables_at_location:
        result[study_table_data.study_table.study_table_name] = {
            "study_table_id": study_table_data.study_table.study_table_id,
            "table_stats": {
                "temperature_level": study_table_data.latest_table_stats.temperature_lvl,
                "sound_level": study_table_data.latest_table_stats.sound_lvl,
                "co2_level": study_table_data.latest_table_stats.co2_lvl,
            },
            "availability": []
        }

    for start_hour in range(24):
        end_hour = start_hour + 1
        time_template = "{} {}:00:00"
        start_time = time_template.format(booking_date, "0" + str(start_hour) if start_hour < 10 else str(start_hour))
        end_time = time_template.format(booking_date, "0" + str(end_hour) if end_hour < 10 else str(end_hour))
        available_tables = study_table_manager.get_available_tables(location_id, start_time, end_time)
        available_study_table_names = set()
        for available_table in available_tables:
            available_study_table_names.add(available_table.study_table_name)
        for study_table_name in result.keys():
            if study_table_name in available_study_table_names:
                result[study_table_name]["availability"].append(True)
            else:
                result[study_table_name]["availability"].append(False)
    return json.dumps(result)


@booking_api.route("/tableBooking", methods=["GET"])
def tableBooking():
    tableId = request.form.get("tableId")
    startTime = request.form.get("startTime")
    endTime = request.form.get("endTime")
    try:
        booking_manager = BookingManager(mysql)
        result = booking_manager.get_table_booking_next_hour(tableId, startTime, endTime)
        return json.dumps(result.to_dict() if result is not None else None)
    except Exception as e:
        err_msg = str(e) if len(str(e)) > 0 else "an unexpected error has occurred"
        return json.dumps({
            "statusCode": StatusCode.INTERNAL_ERR_CODE,
            "message": err_msg
        })
