from .study_table import StudyTable
from .table_stats import TableStats


class AvailableStudyTableData:
    def __init__(self, study_table: StudyTable, latest_table_stats: TableStats):
        self._study_table = study_table
        self._latest_table_stats = latest_table_stats

    @property
    def study_table(self) -> StudyTable:
        return self._study_table

    @property
    def latest_table_stats(self) -> TableStats:
        return self._latest_table_stats
