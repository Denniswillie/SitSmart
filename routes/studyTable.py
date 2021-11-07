from flask import Blueprint, request
from global_init import mysql
from .enums import StatusCode
import json
from db_managers import StudyTableManager
from entities import StudyTable

studyTable_api = Blueprint('studyTable_api', __name__)


@studyTable_api.route("/studyTable", methods=["POST"])
def create_table():
    location_id = request.form.get("location_id")
    study_table_name = request.form.get("study_table_name")
    mac_address = request.form.get("mac_address")
    study_table = StudyTable(study_table_name, location_id, mac_address)
    study_table_manager = StudyTableManager(mysql)
    try:
        study_table_manager.create_study_table(study_table)
        return json.dumps({
            "statusCode": StatusCode.SUCCESSFUL_CREATION_STATUS_CODE,
            "message": "Successfully created a new table"
        })
    except Exception as e:
        err_msg = str(e) if len(str(e)) > 0 else "an unexpected error has occurred"
        return json.dumps({
            "statusCode": StatusCode.INTERNAL_ERR_CODE,
            "message": err_msg
        })


@studyTable_api.route("/getTableInfo", methods=["POST"])
def table_info():
    mac_address = request.form.get("mac_address")
    study_table_manager = StudyTableManager(mysql)
    try:
        res = study_table_manager.get_table_info(mac_address)
        return json.dumps({
            "statusCode": StatusCode.OK_STATUS_CODE,
            "result": res
        })
    except Exception as e:
        err_msg = str(e) if len(str(e)) > 0 else "an unexpected error has occurred"
        return json.dumps({
            "statusCode": StatusCode.OK_STATUS_CODE,
            "message": err_msg
        })


@studyTable_api.route("/removeTable", methods=["DELETE"])
def remove_table():
    study_table_id = request.form.get("study_table_id")
    study_table_manager = StudyTableManager(mysql)
    try:
        study_table_manager.remove_study_table(study_table_id)
        return json.dumps({
            "statusCode": StatusCode.OK_STATUS_CODE,
            "message": "Successfully removed a table"
        })
    except Exception as e:
        err_msg = str(e) if len(str(e)) > 0 else "an unexpected error has occurred"
        return json.dumps({
            "statusCode": StatusCode.INTERNAL_ERR_CODE,
            "message": err_msg
        })
