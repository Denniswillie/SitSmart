from flask_mysqldb import MySQL
from entities import SitSmartUser


class SitSmartUserManager:
    def __init__(self, mysql: MySQL):
        self._mysql = mysql

    def create_user_if_not_exists(self, sit_smart_user: SitSmartUser):
        cur = self._mysql.connection.cursor()
        cur.execute("select sitSmartUserId from SitSmartUser where email = %s;",
                    [sit_smart_user.email]
                    )
        self._mysql.connection.commit()
        result = cur.fetchone()
        if result is not None:
            cur.close()
            return result[0]
        cur.execute("insert into SitSmartUser (email) values (%s);", [sit_smart_user.email])
        cur.execute("SELECT LAST_INSERT_ID();")
        self._mysql.connection.commit()
        last_inserted_id = cur.fetchone()[0]
        cur.close()
        return last_inserted_id
