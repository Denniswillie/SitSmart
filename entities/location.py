class Location:
    def __init__(self, name, location_id=None):
        self._location_id = location_id
        self._name = name

    @property
    def location_id(self):
        return self._location_id

    @property
    def name(self):
        return self._name
