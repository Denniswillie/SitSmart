from flask_mysqldb import MySQL
from entities import StudyTable


class StudyTableManager:
    def __init__(self, mysql: MySQL):
        self._mysql = mysql

    def create_study_table(self, study_table: StudyTable):
        cur = self._mysql.connection.cursor()
        cur.execute("INSERT INTO studyTable(studyTableId, locationId, piMacAddress) values (%s, %s, %s)", [
            study_table.study_table_id,
            study_table.location_id,
            study_table.pi_mac_address
        ]
                    )
        self._mysql.connection.commit()
        cur.close()

    def remove_study_table(self, study_table_id: str) -> bool:
        try:
            cur = self._mysql.connection.cursor()
            cur.execute("DELETE from studyTable WHERE studyTableId = %s", [study_table_id])
            self._mysql.connection.commit()
            cur.close()
            return True
        except Exception as e:
            print(e)
            return False
