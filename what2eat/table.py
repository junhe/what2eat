from copy import deepcopy
import random

from utils import *

"""
- Read Excel file
- Generate a table with contents of the excel file
- Pick n meat items
- Pick m vege items
- Send the ingredients to TODOist
- Save generated menu as Numbers file
"""

class Table(object):
    def __init__(self, rows):
        self._rows = deepcopy(rows)

    def filter_equal(self, colname, value):
        "Return a table so you can chain"
        result = [row for row in self._rows if row[colname] == value]
        return Table(result)

    def filter_not_equal(self, colname, value):
        "Return a table so you can chain"
        result = [row for row in self._rows if not row[colname] == value]
        return Table(result)

    def rows(self):
        return self._rows

    def duplicate(self):
        return Table(deepcopy(self._rows))

    def col(self, colname):
        return [row[colname] for row in self._rows]

    def sample(self, n):
        if self.n_rows() < n:
            return self.duplicate()
        else:
            rows = random.sample(self._rows, n)
            return Table(rows)

    def n_rows(self):
        return len(self._rows)

    def extend(self, table):
        self._rows.extend( table.duplicate().rows() )

    def __str__(self):
        ret = table_to_str(self._rows)
        return ret

