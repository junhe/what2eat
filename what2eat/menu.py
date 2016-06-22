from .table import *
from .utils import *


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

    def raw_table(self):
        return self._table

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
        return row[COL_INGREDIENTS].split(u'|')

    def __str__(self):
        return str(self._table)


class IngredientMap(object):
    def __init__(self, d):
        self._dict = d
        self._email_addr = 'project.141578026.3993020@todoist.net'

    def raw_dict(self):
        return self._dict

    def flatten(self, ingr, entrynames):
        entrystr = u','.join(entrynames)
        return u"{} ({})".format(ingr, entrystr)

    def text_lines(self):
        strlist = []
        for ingr, entrynames in self._dict.items():
            strlist.append( self.flatten(ingr, entrynames) )

        return strlist

    def __unicode__(self):
        return u'\n'.join(self.text_lines())

    def __str__(self):
        return tobytes(unicode(self))

    def send_to_todoist(self):
        text_lines = self.text_lines()
        for line in text_lines:
            send_email([self._email_addr], tobytes(line))


def menu_from_file(path):
    table = Table(read_xls(path))
    return Menu(table)

