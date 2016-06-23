# -*- coding: utf-8 -*-
from .table import *
from .utils import *


TYPE_PERMANENT = 2
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
        self._table = table.duplicate()
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
        return Menu(ret_table)

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
        return Menu(ret_table)

    def hand_pick(self, entrytype, n, test=False):
        work_menu = Menu(self._table.filter_equal(COL_ENTRYTYPE, entrytype))
        ret_menu = Menu()
        remaining = n

        while remaining > 0 and work_menu.raw_table().n_rows() > 0:
            single_menu = work_menu.sample(entrytype, 1)
            entryname = single_menu.raw_table().rows()[0][COL_ENTRYNAME]

            print str(single_menu)

            if test is False:
                ans = raw_input('Keep this entry? (y/n)[n]: ')
            else:
                ans = 'y'

            if ans.lower().strip() == 'y':
                ret_menu.extend(single_menu)
                remaining -= 1

            work_menu.remove(entryname)

        return ret_menu

    def duplicate(self):
        return Menu(self._table.duplicate())

    def remove(self, entryname):
        self._table = self._table.filter_not_equal(COL_ENTRYNAME, entryname)

    def extend(self, other_menu):
        assert isinstance(other_menu, Menu)
        self._table.extend(other_menu.raw_table())

    def pick(self, order, byhand=False):
        """
        order is a dictionary:
            {TYPE_MEAT: 8,
             TYPE_VEGETABLE: 2}
        """
        ret_table = Table([])
        for entrytype, count in order.items():
            if byhand is True:
                t = self.hand_pick(entrytype, count).raw_table()
            else:
                t = self.add_and_sample(entrytype, count).raw_table()
            ret_table.extend(t)

        return Menu(ret_table)

    def send_ingredients_map(self, email_addr):
        i_map = self.ingredients_map()
        i_map.send_to_todoist(email_addr)

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

    def send_to_todoist(self, email_addr):
        text_lines = self.text_lines()
        for line in text_lines:
            send_email_by_gmail(
                tolist=[email_addr],
                subject=tobytes(line),
                content='Left blank intentionally.',
                username='ojunhe',
                password_path='./email.config')
            print 'Sent', tobytes(line)


def menu_from_file(path):
    table = Table(read_xls(path))
    return Menu(table)

