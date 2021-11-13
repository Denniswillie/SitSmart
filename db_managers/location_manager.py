from entities import Location
from flask_mysqldb import MySQL


class LocationManager:
    def __init__(self, mysql: MySQL):
        self._mysql = mysql

    def create_location(self, location: Location) -> int:
        cur = self._mysql.connection.cursor()
        cur.execute("INSERT INTO location(name) VALUES (%s);", [location.name])
        cur.execute("SELECT LAST_INSERT_ID();")
        self._mysql.connection.commit()
        last_inserted_id = cur.fetchone()[0]
        cur.close()
        return last_inserted_id

    def verify_location_id(self, location_id) -> bool:
        cur = self._mysql.connection.cursor()
        cur.execute("SELECT locationId from location WHERE locationId = %s;", [location_id])
        self._mysql.connection.commit()
        location_id = cur.fetchone()
        if not location_id:
            return False
        else:
            return True

    def edit_location(self, location: Location):
        cur = self._mysql.connection.cursor()
        cur.execute("UPDATE location SET name = %s WHERE locationId = %s;", [location.name, location.location_id])
        self._mysql.connection.commit()
        cur.close()

    def remove_location(self, location_id: int):
        cur = self._mysql.connection.cursor()
        cur.execute("DELETE from location WHERE locationId = %s", [location_id])
        self._mysql.connection.commit()
        cur.close()
