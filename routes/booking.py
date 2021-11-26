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
        location_name = data.get("location_name")
        booking_date = data.get("booking_date")

        # code snippet inspiration from https://stackoverflow.com/questions/2257441/random-string-generation-with
        # -upper-case-letters-and-digits
        # The idea is to generate 4 random base10 digits resulting in (10 ^ 4) password possibilities.
        booking_password = "".join(secrets.choice(string.digits) for _ in range(4))

        bookings = data.get("bookings")
        for study_table_id, booking_data in bookings.items():
            for start_time, end_time in booking_data["times"]:
                start_time_string = "{}:00:00".format(start_time) if start_time > 10 else "0{}:00:00".format(start_time)
                end_time_string = "{}:00:00".format(end_time) if end_time > 10 else "0{}:00:00".format(end_time)
                booking_start_time = booking_date + " " + start_time_string
                booking_end_time = booking_date + " " + end_time_string
                booking = Booking(
                    booking_password=booking_password,
                    start_time=booking_start_time,
                    end_time=booking_end_time,
                    table_id=study_table_id
                )
                booking_manager.create_booking(booking)

        # send confirmation email
        message_string = "You have booked the following study tables in the {} on {}:\n".format(location_name,
                                                                                                booking_date)
        for study_table_id, booking_data in bookings.items():
            message_string += (booking_data["studyTableName"] + "\n")
            for index, (start_time, end_time) in enumerate(booking_data["times"]):
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

                message_string += "{}. {} until {}\n".format(index + 1, start_time_string, end_time_string)
        message_string += "Your booking password is {}".format(booking_password)
        message = Message(
            message_string,
            recipients=[email_address])
        # mail.send(message)

        session["bookings_confirmation"] = {
            "bookings": bookings,
            "location_name": location_name,
            "booking_password": booking_password,
            "booking_date": booking_date
        }
        session.modified = True

        print(session["bookings_confirmation"])

        # redirect to receipt screen
        return json.dumps({
            "success": True,
        })

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
        return render_template("booking.html")

    return json.dumps({
        "statusCode": StatusCode.INTERNAL_ERR_CODE,
        "message": "API method handler does not exist for this route"
    })


@booking_api.route("/available_tables", methods=["POST"])
def get_available_tables():
    # booking_date must be in the format "YYYY-MM-DD"
    data = request.get_json(silent=True)
    booking_date = str(data.get("booking_date"))
    print(booking_date)
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


@booking_api.route("/tapBooking", methods=["POST"])
def tapBooking():
    start_time = request.form.get("start_time")
    end_time = request.form.get("end_time")
    study_table_id = request.form.get("study_table_id")
    password = 1234  # not important as we are tapping to claim it
    booking_manager = BookingManager(mysql)
    booking = Booking(
        password,
        study_table_id,
        start_time,
        end_time,
    )
    booking_manager.create_booking(booking)
    return json.dumps({
        "statusCode": StatusCode.SUCCESSFUL_CREATION_STATUS_CODE,
        "message": "Successfully created a booking"
    })
