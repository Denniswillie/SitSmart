from typing import List

from flask_mysqldb import MySQL
from entities import Booking, StudyTable
import uuid


class BookingManager:
    def __init__(self, mysql: MySQL):
        self._mysql = mysql

    def create_booking(self, booking: Booking):
        cur = self._mysql.connection.cursor()

        # generate uuid for salt
        salt = str(uuid.uuid4())

        cur.execute("insert into booking (bookingPasswordHash, salt, studyTableId, startTime, endTime) values (SHA2("
                    "concat(%s, %s), 512), %s, %s, %s, %s);", [booking.booking_password, salt, salt,
                                                               booking.table_id, booking.start_time, booking.end_time])
        self._mysql.connection.commit()
        cur.close()

    # return a boolean value indicating whether the booking passcode is verified or not.
    def verify_booking_passcode(self, booking_id: int, booking_password: str) -> bool:
        cur = self._mysql.connection.cursor()
        cur.execute("select if(count(*) = 1, 1, 0) as isVerified from booking where bookingId = %s and "
                    "bookingPasswordHash = SHA2(concat(%s, salt), 512);", [booking_id, booking_password])
        self._mysql.connection.commit()
        result = cur.fetchone()
        cur.close()
        return result[0] == 1

    def remove_booking(self, booking_id: int):
        cur = self._mysql.connection.cursor()
        cur.execute("DELETE from booking where bookingId = %s", [booking_id])
        self._mysql.connection.commit()
        cur.close()

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
