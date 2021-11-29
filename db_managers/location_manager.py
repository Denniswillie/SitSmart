from entities import Location
from flask_mysqldb import MySQL
from typing import List


class LocationManager:
    def __init__(self, mysql: MySQL):
        self._mysql = mysql

    def create_location(self, location: Location) -> int:
        cur = self._mysql.connection.cursor()
        cur.execute("INSERT INTO Location(name) VALUES (%s);", [location.name])
        cur.execute("SELECT LAST_INSERT_ID();")
        self._mysql.connection.commit()
        last_inserted_id = cur.fetchone()[0]
        cur.close()
        return last_inserted_id

    def verify_location_id(self, location_id) -> bool:
        cur = self._mysql.connection.cursor()
        cur.execute("SELECT locationId from Location WHERE locationId = %s;", [location_id])
        self._mysql.connection.commit()
        location_id = cur.fetchone()
        if not location_id:
            return False
        else:
            return True

    def edit_location(self, location: Location):
        cur = self._mysql.connection.cursor()
        cur.execute("UPDATE Location SET name = %s WHERE locationId = %s;", [location.name, location.location_id])
        self._mysql.connection.commit()
        cur.close()

    def remove_location(self, location_id: int):
        cur = self._mysql.connection.cursor()
        cur.execute("DELETE from Location WHERE locationId = %s", [location_id])
        self._mysql.connection.commit()
        cur.close()

    def get_available_locations(self) -> List[Location]:
        cur = self._mysql.connection.cursor()
        cur.execute("SELECT locationId, name from Location;")
        self._mysql.connection.commit()
        locations = [Location(location_id=location_id, name=name) for location_id, name in cur.fetchall()]
        cur.close()
        return locations

    def get_location_name(self, location_id):
        cur = self._mysql.connection.cursor()
        cur.execute("SELECT name from Location where locationId = %s;", [location_id])
        self._mysql.connection.commit()
        result = cur.fetchone()
        cur.close()
        return result[0] if result is not None else None
