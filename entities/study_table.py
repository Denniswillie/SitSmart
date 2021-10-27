class StudyTable:
    def __init__(self, study_table_id, location_id, pi_mac_address, avg_temperature_lvl, avg_sound_lvl, avg_co2_lvl):
        self._study_table_id = study_table_id
        self._location_id = location_id
        self._pi_mac_address = pi_mac_address
        self._avg_temperature_lvl = avg_temperature_lvl
        self._avg_sound_lvl = avg_sound_lvl
        self._avg_co2_lvl = avg_co2_lvl

    @property
    def study_table_id(self):
        return self._study_table_id

    @property
    def location_id(self):
        return self._location_id

    @property
    def pi_mac_address(self):
        return self._pi_mac_address

    @property
    def avg_temperature_lvl(self):
        return self._avg_temperature_lvl

    @property
    def avg_sound_lvl(self):
        return self._avg_sound_lvl

    @property
    def avg_co2_lvl(self):
        return self._avg_co2_lvl
