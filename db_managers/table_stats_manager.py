from flask_mysqldb import MySQL
from entities import TableStats


class TableStatsManager:
    def __init__(self, mysql: MySQL):
        self._mysql = mysql

    def save_table_stats(self, table_stats: TableStats):
        cur = self._mysql.connection.cursor()
        cur.execute("insert into tableStats (studyTableId, recordedTime, temperatureLevel, soundLevel, co2Level) "
                    "values (%s, %s, %s, %s, %s);", [
                        table_stats.table_id,
                        table_stats.time,
                        table_stats.temperature_lvl,
                        table_stats.sound_lvl,
                        table_stats.co2_lvl
                    ])
        self._mysql.connection.commit()
        cur.close()
