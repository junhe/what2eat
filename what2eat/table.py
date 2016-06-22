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


TYPE_MEAT = 1
TYPE_VEGETABLE = 0

TYPE_NOT_ADDED = None
TYPE_EXCLUDED = 0
TYPE_ADDED = 1
TYPE_ALWAYS = 2

col_entrytype = 'EntryType'
col_entryname = 'EntryName'
col_addentry = 'AddEntry'
col_ingredients = 'Ingredients'

class Menu(object):
    def __init__(self, path):
        self._table = Table(read_xls(path))

    def sample(self, entrytype, n):
        ret_table = self._table.filter_equal(col_entrytype, entrytype)\
                .sample(n)
        return ret_table

    def add_and_sample(self, entrytype, n):
        """
        Add all the rows that marked "Add" first,
        if not enough, sample the else
        """
        ret_table = self._table.filter_equal(col_entrytype, entrytype)\
                               .filter_equal(col_addentry, TYPE_ADDED)

        remaining = n - ret_table.n_rows()
        if remaining > 0:
            sample_table = self._table\
                    .filter_equal(col_entrytype, entrytype)\
                    .filter_equal(col_addentry, TYPE_NOT_ADDED)\
                    .sample(remaining)
            ret_table.extend(sample_table)
        return ret_table

    def pick(self, order):
        """
        order is a dictionary:
            {TYPE_MEAT: 8,
             TYPE_VEGETABLE: 2}
        """
        ret_table = Table([])
        for entrytype, count in order.items():
            t = self.add_and_sample(entrytype, count)
            ret_table.extend(t)

        return ret_table

    def __str__(self):
        return str(self._table)



