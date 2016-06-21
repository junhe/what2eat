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
                table.get_row(0))
        self.assertDictEqual({'col1': 3, 'col2': 4},
                table.get_row(1))

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


class TestChineseTable(unittest.TestCase):
    def test_filter(self):
        table_excel = read_xls("./tests/menusample.xlsx")
        table = Table(table_excel)

        rows = table.filter_equal('AddEntry', 1).rows()
        self.assertEqual(rows[0]['EntryName'], u"肉末酸豆角")

        rows = table.filter_equal('AddEntry', None).rows()
        self.assertEqual(rows[0]['EntryName'], u"皮蛋瘦肉粥")


class TestMenu(unittest.TestCase):
    def test_n_sample_meat(self):
        menu = Menu("./tests/menusample.xlsx")

        rows = menu.sample(TYPE_VEGETABLE, 1).rows()
        self.assertEqual(rows[0]['EntryName'], u'丝瓜蛋汤')


def main():
    unittest.main()

if __name__ == '__main__':
    main()

