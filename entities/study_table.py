class StudyTable:
    def __init__(self,
                 study_table_name,
                 location_id,
                 pi_mac_address,
                 study_table_id=None):
        self._study_table_name = study_table_name
        self._study_table_id = study_table_id
        self._location_id = location_id
        self._pi_mac_address = pi_mac_address

    @property
    def study_table_name(self):
        return self._study_table_name

    @property
    def study_table_id(self):
        return self._study_table_id

    @property
    def location_id(self):
        return self._location_id

    @property
    def pi_mac_address(self):
        return self._pi_mac_address
