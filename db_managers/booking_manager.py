from flask_mysqldb import MySQL
from entities import Booking
import uuid
from datetime import datetime, timedelta


class BookingManager:
    def __init__(self, mysql: MySQL):
        self._mysql = mysql

    def create_booking(self, booking: Booking):
        cur = self._mysql.connection.cursor()

        # generate uuid for salt
        salt = str(uuid.uuid4())

        cur.execute("insert into Booking (bookingPasswordHash, salt, studyTableId, startTime, endTime, sitSmartUserId) values (SHA2("
                    "concat(%s, %s), 512), %s, %s, %s, %s, %s);", [booking.booking_password, salt, salt,
                                                               booking.table_id, booking.start_time, booking.end_time, booking.sit_smart_user_id])
        cur.execute("SELECT LAST_INSERT_ID();")
        self._mysql.connection.commit()
        last_id = cur.fetchone()[0]
        cur.close()
        return last_id

    # return a boolean value indicating whether the booking passcode is verified or not.
    def verify_booking_passcode(self, booking_id: int, booking_password: str) -> bool:
        cur = self._mysql.connection.cursor()
        cur.execute("select if(count(*) = 1, 1, 0) as isVerified from Booking where bookingId = %s and "
                    "bookingPasswordHash = SHA2(concat(%s, salt), 512);", [booking_id, booking_password])
        self._mysql.connection.commit()
        result = cur.fetchone()
        cur.close()
        return result[0] == 1

    def remove_booking(self, booking_id: int):
        cur = self._mysql.connection.cursor()
        cur.execute("DELETE from Booking where bookingId = %s", [booking_id])
        self._mysql.connection.commit()
        cur.close()

    def get_table_booking_next_hour_consecutive(self, study_table_id, start_time):
        cur = self._mysql.connection.cursor()
        cur.execute("select bookingId, studyTableId, startTime, endTime, sitSmartUserId from Booking where "
                    "studyTableId = %s and binary startTime = binary %s;", [study_table_id, start_time])
        self._mysql.connection.commit()
        result = cur.fetchone()
        if result is None:
            cur.close()
            return []
        bookings = []
        sit_smart_user_id = result[-1]
        bookings.append(Booking(
            booking_id=result[0],
            table_id=result[1],
            start_time=result[2].strftime("%Y-%m-%d %H:%M:%S"),
            end_time=result[3].strftime("%Y-%m-%d %H:%M:%S"),
            sit_smart_user_id=result[4]
        ))

        start_time = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
        while True:
            start_time += timedelta(hours=1)
            cur.execute("select bookingId, studyTableId, startTime, endTime, sitSmartUserId from Booking where "
                        "studyTableId = %s and startTime = %s;",
                        [study_table_id, start_time.strftime("%Y-%m-%d %H:%M:%S")]
                        )
            self._mysql.connection.commit()
            result = cur.fetchone()
            if result is None or int(result[-1]) != int(sit_smart_user_id):
                break
            bookings.append(Booking(
                booking_id=result[0],
                table_id=result[1],
                start_time=result[2].strftime("%Y-%m-%d %H:%M:%S"),
                end_time=result[3].strftime("%Y-%m-%d %H:%M:%S"),
                sit_smart_user_id=result[4]
            ))
        cur.close()

        return bookings
