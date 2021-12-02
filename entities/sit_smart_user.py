class SitSmartUser:
    def __init__(self, sit_smart_user_id=None, email=None):
        self._sit_smart_user_id = sit_smart_user_id
        self._email = email

    @property
    def sit_smart_user_id(self):
        return self._sit_smart_user_id

    @property
    def email(self):
        return self._email
