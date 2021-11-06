class TableStats:
    def __init__(self, table_id, time, temperature_lvl, sound_lvl, co2_lvl, table_stats_id=None):
        self._table_stats_id = table_stats_id
        self._table_id = table_id
        self._time = time
        self._temperature_lvl = temperature_lvl
        self._sound_lvl = sound_lvl
        self._co2_lvl = co2_lvl

    @property
    def table_stats_id(self):
        return self._table_stats_id

    @property
    def table_id(self):
        return self._table_id

    @property
    def time(self):
        return self._time

    @property
    def temperature_lvl(self):
        return self._temperature_lvl

    @property
    def sound_lvl(self):
        return self._sound_lvl

    @property
    def co2_lvl(self):
        return self._co2_lvl
