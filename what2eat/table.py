from copy import deepcopy

"""
- Read Excel file
- Generate a table with contents of the excel file
- Pick n meat items
- Pick m vege items
- Send the ingredients to TODOist
- Save generated menu as Numbers file
"""

class Table(object):
    def __init__(self, table):
        self._rows = deepcopy(table)

    def filter_equal(self, colname, value):
        result = [row for row in self._rows if row[colname] == value]
        return result

    def get_row(self, rowid):
        return self._rows[rowid]

    def rows(self):
        return self._rows


