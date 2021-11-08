import secrets
import string
import json

from global_init import mysql, mail
from flask import Blueprint, request, redirect, url_for, render_template
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
        location_id = int(request.form.get("location_id"))
        start_time = request.form.get("start_time")
        end_time = request.form.get("end_time")
        study_table_manager = StudyTableManager(mysql)
        return render_template("booking_screen.html", available_tables=study_table_manager.get_available_tables(
            location_id,
            start_time,
            end_time
        ))

    return json.dumps({
        "statusCode": StatusCode.INTERNAL_ERR_CODE,
        "message": "API method handler does not exist for this route"
    })
