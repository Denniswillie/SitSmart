class Booking:
    def __init__(self, booking_password=None, table_id=None, start_time=None, end_time=None, booking_id=None):
        self._booking_id = booking_id
        self._booking_password = booking_password
        self._table_id = table_id
        self._start_time = start_time
        self._end_time = end_time

    @property
    def booking_id(self):
        return self._booking_id

    @property
    def booking_password(self):
        return self._booking_password

    @property
    def table_id(self):
        return self._table_id

    @property
    def start_time(self):
        return self._start_time

    @property
    def end_time(self):
        return self._end_time

    def to_dict(self):
        return {
            "booking_id": self._booking_id,
            "table_id": self._table_id,
            "start_time": self._start_time,
            "end_time": self._end_time
        }
