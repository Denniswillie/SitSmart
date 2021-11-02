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
