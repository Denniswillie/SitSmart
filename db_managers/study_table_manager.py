from flask_mysqldb import MySQL
from entities import StudyTable, StudyTableInfo, AvailableStudyTableData, TableStats
from typing import List


class StudyTableManager:
    def __init__(self, mysql: MySQL):
        self._mysql = mysql

    def create_study_table(self, study_table: StudyTable) -> int:
        try:
            cur = self._mysql.connection.cursor()
            cur.execute("INSERT INTO StudyTable(studyTableName, locationId, piMacAddress) values (%s, %s, %s)", [
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
        except:
            return -1

    def remove_study_table(self, study_table_id: int, pi_mac_address: str) -> bool:
        cur = self._mysql.connection.cursor()
        cur.execute("DELETE from Booking where studyTableId = %s;", [study_table_id])
        self._mysql.connection.commit()
        cur.execute("DELETE from TableStats where studyTableId = %s;", [study_table_id])
        self._mysql.connection.commit()
        rows_affected = cur.execute(
            "DELETE from StudyTable WHERE studyTableId = %s and piMacAddress = %s;",
            [study_table_id, pi_mac_address]
        )
        self._mysql.connection.commit()
        cur.close()
        return rows_affected > 0

    def get_table_info(self, pi_mac_address: str) -> StudyTableInfo:
        cur = self._mysql.connection.cursor()
        cur.execute("SELECT StudyTable.studyTableId, StudyTable.studyTableName, Location.name from StudyTable JOIN "
                    "Location ON StudyTable.locationId = Location.locationId WHERE piMacAddress = %s;", [pi_mac_address]
                    )
        self._mysql.connection.commit()
        result = cur.fetchone()
        if result is not None:
            study_table_id, study_table_name, location_name = result
        else:
            study_table_id = study_table_name = location_name = None
        cur.close()
        return StudyTableInfo(study_table_id, study_table_name, location_name)

    def get_available_tables(self, location_id: int, start_time: str, end_time: str) -> List[StudyTable]:
        cur = self._mysql.connection.cursor()
        cur.execute("select StudyTable.studyTableId, StudyTable.studyTableName, StudyTable.locationId, "
                    "StudyTable.piMacAddress from StudyTable LEFT JOIN Booking on StudyTable.studyTableId = "
                    "Booking.studyTableId WHERE StudyTable.locationId = %s group by StudyTable.studyTableId having "
                    "count(case when not (binary %s <= binary Booking.startTime or binary Booking.endTime <= binary %s)"
                    " then 1 end) = 0;",
                    [location_id, end_time, start_time]
                    )
        self._mysql.connection.commit()
        available_study_tables = []
        for study_table_id, study_table_name, study_table_location_id, mac_address in cur.fetchall():
            available_study_tables.append(StudyTable(
                study_table_name=study_table_name,
                study_table_id=study_table_id,
                location_id=study_table_location_id,
                pi_mac_address=mac_address
            ))
        cur.close()
        return available_study_tables

    def get_study_tables_in_location(self, location_id) -> List[AvailableStudyTableData]:
        cur = self._mysql.connection.cursor()
        cur.execute("select * from StudyTable where locationId = %s;", [location_id])
        study_tables = []
        self._mysql.connection.commit()
        for study_table_id, study_table_name, study_table_location_id, mac_address, temp, sound, co2 in cur.fetchall():
            study_tables.append(AvailableStudyTableData(
                study_table=StudyTable(
                    study_table_name=study_table_name,
                    location_id=study_table_location_id,
                    pi_mac_address=mac_address,
                    study_table_id=study_table_id
                ),
                latest_table_stats=TableStats(
                    table_id=study_table_id,
                    sound_lvl=sound,
                    co2_lvl=co2,
                    temperature_lvl=temp,
                    time=None
                )
            ))
        return study_tables
