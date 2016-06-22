# -*- coding: utf-8 -*-
import unittest

from what2eat.utils import *
from what2eat.table import *

class TestReadingXLS(unittest.TestCase):
    def test_simple(self):
        table = read_xls("./tests/sample.xlsx")

        self.assertEqual(len(table), 2)
        self.assertEqual(table[0]['col1'], 1)
        self.assertEqual(table[1]['col1'], 2)
        self.assertEqual(table[0]['col2'], 'a')
        self.assertEqual(table[1]['col2'], 'b')

    def test_chinese(self):
        table = read_xls("./tests/menusample.xlsx")
        row0 = table[0]
        self.assertEqual(row0['EntryName'], u"皮蛋瘦肉粥")


def create_test_table():
    origin = [{'col1': 1, 'col2': 2},
              {'col1': 3, 'col2': 4},
              {'col1': 1, 'col2': 8},
             ]
    table = Table(origin)
    return table


class TestTable(unittest.TestCase):
    def test_init(self):
        origin = [{'col1': 1, 'col2': 2},
                 {'col1': 3, 'col2': 4}]
        table = Table(origin)
        self.assertDictEqual({'col1': 1, 'col2': 2},
                table.rows()[0])
        self.assertDictEqual({'col1': 3, 'col2': 4},
                table.rows()[1])

    def test_filter(self):
        table = create_test_table()
        rows = table.filter_equal('col1', 3).rows()
        self.assertListEqual(rows, [{'col1': 3, 'col2': 4}])

    def test_load_excel(self):
        table_excel = read_xls("./tests/sample.xlsx")
        local_table = Table(table_excel)
        rows = local_table.rows()

        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]['col1'], 1)
        self.assertEqual(rows[1]['col1'], 2)
        self.assertEqual(rows[0]['col2'], 'a')
        self.assertEqual(rows[1]['col2'], 'b')

    def test_sample(self):
        table = create_test_table()
        sample_table = table.sample(1)

        self.assertEqual(sample_table.n_rows(), 1)

    def test_str(self):
        table = create_test_table()
        str_rows = str(table).split('\n')

        self.assertIn('3', str_rows[2])
        self.assertIn('4', str_rows[2])

    def test_duplicate(self):
        table = create_test_table()
        dup_table = table.duplicate()

        self.assertDictEqual(table.rows()[0], dup_table.rows()[0])
        self.assertDictEqual(table.rows()[1], dup_table.rows()[1])

        table.rows()[0]['col1'] = 88888
        self.assertNotEqual(table.rows()[0]['col1'],
                dup_table.rows()[0]['col1'])

    def test_extend(self):
        table = create_test_table()

        row = {'col1': 888, 'col2':999}
        table2 = Table([row])

        table.extend(table2)
        self.assertDictEqual(table.rows()[-1], row)


class TestChineseTable(unittest.TestCase):
    def test_filter(self):
        table_excel = read_xls("./tests/menusample.xlsx")
        table = Table(table_excel)

        rows = table.filter_equal('AddEntry', 1).rows()
        self.assertEqual(rows[0]['EntryName'], u"肉末酸豆角")

        rows = table.filter_equal('AddEntry', None).rows()
        self.assertEqual(rows[0]['EntryName'], u"皮蛋瘦肉粥")


class TestMenu(unittest.TestCase):
    def test_n_sample_vege(self):
        menu = Menu("./tests/menusample.xlsx")

        rows = menu.sample(TYPE_VEGETABLE, 1).rows()
        self.assertEqual(rows[0]['EntryName'], u'丝瓜蛋汤')

    def meat_entries(self):
        entries = [
                u'皮蛋瘦肉粥',
                u'笋炒腊肉',
                u'肉末酸豆角',
                u'辣椒酿',
                u'桂林米粉',
                u'春笋炒肉丝',
                u'肉末豆腐']
        return entries

    def test_n_sample_meat(self):
        menu = Menu("./tests/menusample.xlsx")

        sampled_table = menu.sample(TYPE_MEAT, 2)
        rows = sampled_table.rows()
        self.assertEqual(len(rows), 2)
        self.assertIn(rows[0]['EntryName'], self.meat_entries())
        self.assertIn(rows[1]['EntryName'], self.meat_entries())
        self.assertNotEqual(rows[0]['EntryName'], rows[1]['EntryName'])

    def test_add_and_sample(self):
        menu = Menu("./tests/menusample.xlsx")

        sampled_table = menu.add_and_sample(TYPE_MEAT, 2)
        self.assertIn(u'肉末酸豆角', sampled_table.col('EntryName'))
        self.assertEqual(sampled_table.n_rows(), 2)

    def test_pick(self):
        menu = Menu("./tests/menusample.xlsx")

        picked_table = menu.pick({TYPE_MEAT: 2, TYPE_VEGETABLE: 2})

        self.assertEqual(picked_table.n_rows(), 3) # only one vege available
        meat_entries = picked_table.filter_equal(col_entrytype, TYPE_MEAT)\
                .col(col_entryname)
        for entryname in meat_entries:
            self.assertIn(entryname, self.meat_entries())

def main():
    unittest.main()

if __name__ == '__main__':
    main()

