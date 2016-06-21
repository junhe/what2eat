from copy import deepcopy
import random

from table import *
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

    def get_row(self, rowid):
        return self._rows[rowid]

    def rows(self):
        return self._rows

    def sample(self, n):
        rows = random.sample(self._rows, n)
        return Table(rows)

    def n_rows(self):
        return len(self._rows)


TYPE_MEAT = 1
TYPE_VEGETABLE = 0

col_entrytype = 'EntryType'
col_entryname = 'EntryName'
col_addentry = 'AddEntry'
col_ingredients = 'Ingredients'

class Menu(object):
    def __init__(self, path):
        self._table = Table(read_xls(path))

    def sample(self, entrytype, n):
        ret_table = self._table.filter_equal(col_entrytype, entrytype)
        return ret_table








