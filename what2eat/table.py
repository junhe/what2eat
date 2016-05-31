from copy import deepcopy

class Table(object):
    def __init__(self, table):
        self._table = deepcopy(table)

    def filter_equal(self, colname, value):
        result = [row for row in self._table if row[colname] == value]
        return deepcopy(result)

    def get_row(self, rowid):
        return self._table[rowid]

