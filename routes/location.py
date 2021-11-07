from flask import Blueprint, request
from .enums import StatusCode
import json
from global_init import mysql
from db_managers import LocationManager
from entities import Location

location_api = Blueprint('location', __name__)


@location_api.route("/location", methods=["POST"])
def create_location():
    name = request.form.get("location_name")
    location = Location(name)
    location_manager = LocationManager(mysql)
    try:
        location_id = location_manager.create_location(location)
        return json.dumps({
            "statusCode": StatusCode.SUCCESSFUL_CREATION_STATUS_CODE,
            "message": "Your new table ID is " + str(location_id)
        })
    except Exception as e:
        err_msg = str(e) if len(str(e)) > 0 else "an unexpected error has occurred"
        return json.dumps({
            "statusCode": StatusCode.INTERNAL_ERR_CODE,
            "message": err_msg
        })


@location_api.route("/editLocation", methods=["POST"])
def edit_location():
    try:
        location_name = request.form.get("location_name")
        location_id = int(request.form.get("location_id"))
        location = Location(location_name, location_id)
        location_manager = LocationManager(mysql)
        location_manager.edit_location(location)
        return json.dumps({
            "statusCode": StatusCode.OK_STATUS_CODE,
            "message": "Successfully edited"
        })
    except Exception as e:
        err_msg = str(e) if len(str(e)) > 0 else "an unexpected error has occurred"
        return json.dumps({
            "statusCode": StatusCode.INTERNAL_ERR_CODE,
            "message": err_msg
        })


@location_api.route("/removeLocation", methods=["DELETE"])
def remove_location():
    try:
        location_id = int(request.form.get("location_id"))
        location_manager = LocationManager(mysql)
        location_manager.remove_location(location_id)
        return json.dumps({
            "statusCode": StatusCode.OK_STATUS_CODE,
            "message": "Successfully removed"
        })
    except Exception as e:
        err_msg = str(e) if len(str(e)) > 0 else "an unexpected error has occurred"
        return json.dumps({
            "statusCode": StatusCode.INTERNAL_ERR_CODE,
            "message": err_msg
        })
