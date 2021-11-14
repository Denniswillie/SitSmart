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
        email_address = request.form.get("email_address")
        start_time = request.form.get("start_time")
        end_time = request.form.get("end_time")
        study_table_id = request.form.get("study_table_id")
        study_table_name = request.form.get("study_table_name")
        location_name = request.form.get("location_name")

        # code snippet inspiration from https://stackoverflow.com/questions/2257441/random-string-generation-with
        # -upper-case-letters-and-digits
        # The idea is to generate 4 random base36 digits resulting in (36 ^ 4) password possibilities.
        booking_password = "".join(secrets.choice(string.digits + string.ascii_uppercase) for _ in range(4))

        booking = Booking(
            booking_password,
            study_table_id,
            start_time,
            end_time,
        )
        booking_manager.create_booking(booking)

        # send confirmation email
        message = Message(
            'You have booked table {} in {}, from {} to {}. Your booking password is {}'.format(
                study_table_name,
                location_name,
                start_time,
                end_time,
                booking_password
            ),
            recipients=[email_address])
        mail.send(message)

        # redirect to receipt screen
        return redirect(url_for(
            ".receipt_screen",
            is_redirect=True,
            study_table_name=study_table_name,
            location_name=location_name,
            start_time=start_time,
            end_time=end_time,
            booking_password=booking_password
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
    return result
