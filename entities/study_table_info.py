class StudyTableInfo:
    def __init__(self, study_table_id, location_name):
        self._study_table_id = study_table_id
        self._location_name = location_name

    @property
    def study_table_id(self):
        return self._study_table_id

    @property
    def location_name(self):
        return self._location_name
