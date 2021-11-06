from db_managers import TableStatsManager, StudyTableManager
from entities import TableStats, StudyTableInfo, StudyTable
from flask_mysqldb import MySQL


def get_table_info(message: dict, mysql: MySQL) -> StudyTableInfo:
    pi_mac_address = str(message["pi_mac_address"])
    study_table_manager = StudyTableManager(mysql)
    return study_table_manager.get_table_info(pi_mac_address)


def create_table(message: dict, mysql: MySQL):
    study_table_manager = StudyTableManager(mysql)
    study_table_name = message["study_table_name"]
    location_id = message["location_id"]
    pi_mac_address = message["pi_mac_address"]
    study_table = StudyTable(study_table_name, location_id, pi_mac_address)
    return study_table_manager.create_study_table(study_table)


def remove_table(message: dict, mysql: MySQL):
    study_table_manager = StudyTableManager(mysql)
    table_id = str(message["table_id"])
    study_table_manager.remove_study_table(table_id)


def save_table_stats(message: dict, mysql: MySQL):
    table_id = message["table_id"]
    recorded_time = message["recorded_time"]
    temperature_level = message["temperature_level"]
    co2_level = message["co2_level"]
    sound_level = message["sound_level"]
    table_states = TableStats(table_id, recorded_time, temperature_level, sound_level, co2_level)
    table_states_manager = TableStatsManager(mysql)
    table_states_manager.save_table_stats(table_states)