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

COL_ENTRYTYPE = 'EntryType'
COL_ENTRYNAME = 'EntryName'
COL_ADDENTRY = 'AddEntry'
COL_INGREDIENTS = 'Ingredients'

class Menu(object):
    def __init__(self, table=None):
        if table is None:
            table = Table([])
        assert isinstance(table, Table) is True
        self._table = table
        self._clean()

    def _clean(self):
        "Remove all spaces"
        for row in self._table.rows():
            for k, v in row.items():
                if isinstance(v, basestring):
                    row[k].replace(' ', '')

    def sample(self, entrytype, n):
        ret_table = self._table.filter_equal(COL_ENTRYTYPE, entrytype)\
                .sample(n)
        return ret_table

    def add_and_sample(self, entrytype, n):
        """
        Add all the rows that marked "Add" first,
        if not enough, sample the else
        """
        ret_table = self._table.filter_equal(COL_ENTRYTYPE, entrytype)\
                               .filter_equal(COL_ADDENTRY, TYPE_ADDED)

        remaining = n - ret_table.n_rows()
        if remaining > 0:
            sample_table = self._table\
                    .filter_equal(COL_ENTRYTYPE, entrytype)\
                    .filter_equal(COL_ADDENTRY, TYPE_NOT_ADDED)\
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

    def ingredients_map(self):
        i_map = {}
        for row in self._table.rows():
            entryname = row[COL_ENTRYNAME]
            ingredients = self._ingredients(row)
            for item in ingredients:
                entries_using_item = i_map.setdefault(item, [])
                entries_using_item.append(entryname)
        return IngredientMap(i_map)

    def _ingredients(self, row):
        return row[COL_INGREDIENTS].split('|')

    def __str__(self):
        return str(self._table)

class IngredientMap(object):
    def __init__(self, d):
        self._dict = d

    def raw_dict(self):
        return self._dict

    def __str__(self):
        for ingr, entrynames in self._dict.items():



def menu_from_file(path):
    table = Table(read_xls(path))
    return Menu(table)

