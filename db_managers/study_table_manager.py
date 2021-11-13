from flask_mysqldb import MySQL
from entities import StudyTable, StudyTableInfo, AvailableStudyTableData, TableStats
from typing import List


class StudyTableManager:
    def __init__(self, mysql: MySQL):
        self._mysql = mysql

    def create_study_table(self, study_table: StudyTable) -> int:
        try:
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
        except:
            return -1

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
        result = cur.fetchone()
        if result is not None:
            study_table_id, study_table_name, location_name = result
        else:
            study_table_id = study_table_name = location_name = None
        cur.close()
        return StudyTableInfo(study_table_id, study_table_name, location_name)

    def get_available_tables(self, location_id: int, start_time: str, end_time: str) -> List[AvailableStudyTableData]:
        cur = self._mysql.connection.cursor()
        cur.execute("select availableStudyTablesInfo.studyTableId, availableStudyTablesInfo.studyTableName, "
                    "availableStudyTablesInfo.maxRecordedTime, tableStats.temperatureLevel, tableStats.soundLevel, "
                    "tableStats.co2Level from (select availableStudyTables.studyTableId, "
                    "availableStudyTables.studyTableName, availableStudyTables.locationId, max(recordedTime) as "
                    "maxRecordedTime from tableStats right join (select studyTable.studyTableId, "
                    "studyTable.studyTableName, studyTable.locationId from studyTable LEFT JOIN booking on "
                    "studyTable.studyTableId = booking.studyTableId WHERE studyTable.locationId = %s group by "
                    "studyTable.studyTableId having count(case when not (%s <= booking.startTime or booking.endTime "
                    "<= %s) then 1 end) = 0) as availableStudyTables on tableStats.studyTableId = "
                    "availableStudyTables.studyTableId group by availableStudyTables.studyTableId) as "
                    "availableStudyTablesInfo join tableStats on availableStudyTablesInfo.studyTableId = "
                    "tableStats.studyTableId and availableStudyTablesInfo.maxRecordedTime = tableStats.recordedTime;",
                    [location_id, end_time, start_time]
                    )
        self._mysql.connection.commit()
        available_study_tables = []
        for study_table_id, study_table_name, recorded_time, temperature_lvl, sound_lvl, co2_level in cur.fetchall():
            available_study_tables.append(AvailableStudyTableData(
                StudyTable(
                    study_table_name,
                    location_id,
                    None,
                    study_table_id
                ),
                TableStats(
                    study_table_id,
                    recorded_time,
                    temperature_lvl,
                    sound_lvl,
                    co2_level
                )
            ))
        cur.close()
        return available_study_tables
