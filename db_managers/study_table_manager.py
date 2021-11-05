from flask_mysqldb import MySQL
from entities import StudyTable
from entities import StudyTableInfo


class StudyTableManager:
    def __init__(self, mysql: MySQL):
        self._mysql = mysql

    def create_study_table(self, study_table: StudyTable) -> int:
        cur = self._mysql.connection.cursor()
        cur.execute("INSERT INTO studyTable(studyTableName, locationId, piMacAddress) values (%s, %s, %s)", [
                study_table.study_table_name,
                study_table.location_id,
                study_table.pi_mac_address
            ]
        )
        cur.execute("SELECT LAST_INSERT_ID();")
        self._mysql.connection.commit()
        last_inserted_id = cur.fetchone()[0]
        cur.close()
        return last_inserted_id

    def remove_study_table(self, study_table_id: str):
        cur = self._mysql.connection.cursor()
        cur.execute("DELETE from studyTable WHERE studyTableId = %s", [study_table_id])
        self._mysql.connection.commit()
        cur.close()

    def get_table_info(self, pi_mac_address: str) -> StudyTableInfo:
        cur = self._mysql.connection.cursor()
        cur.execute("SELECT studyTable.studyTableId, studyTable.studyTableName, location.name from studyTable JOIN "
                    "location ON studyTable.locationId = location.locationId WHERE piMacAddress = %s;", [pi_mac_address]
        )
        self._mysql.connection.commit()
        study_table_id, study_table_name, location_name = cur.fetchone()
        cur.close()
        return StudyTableInfo(study_table_id, study_table_name, location_name)

    def get_available_tables(self, location_id: int, start_time: str, end_time: str) -> List[StudyTable]:
        cur = self._mysql.connection.cursor()
        cur.execute("select studyTable.studyTableId, studyTable.studyTableName, studyTable.averageTemperatureLevel, "
                    "studyTable.averageSoundLevel, studyTable.averageCo2Level from studyTable LEFT JOIN booking on "
                    "studyTable.studyTableId = booking.studyTableId WHERE studyTable.locationId = %s group by "
                    "studyTableId having count(case when not (%s <= booking.startTime or "
                    "booking.endTime <= %s) then 1 end) = 0;", [location_id, end_time, start_time])
        self._mysql.connection.commit()
        available_study_tables = []
        for study_table_id, study_table_name, avg_temperature_lvl, avg_sound_lvl, avg_co2_lvl in cur.fetchall():
            available_study_tables.append(StudyTable(
                study_table_name,
                location_id,
                None,
                avg_temperature_lvl,
                avg_sound_lvl,
                avg_co2_lvl,
                study_table_id
            ))
        cur.close()
        return available_study_tables
