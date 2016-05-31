import unittest

from what2eat.utils import *
from what2eat.table import *

class TestReadingXLS(unittest.TestCase):
    def test_main(self):
        table = read_xls("./tests/sample.xlsx")

        self.assertEqual(len(table), 2)
        self.assertEqual(table[0]['col1'], 1)
        self.assertEqual(table[1]['col1'], 2)
        self.assertEqual(table[0]['col2'], 'a')
        self.assertEqual(table[1]['col2'], 'b')


class TestTable(unittest.TestCase):
    def test_init(self):
        orgin = [{'col1': 1, 'col2': 2},
                 {'col1': 3, 'col2': 4}]
        table = Table(origin)
        self.assertDictEqual({'col1': 1, 'col2': 2}

class TestTable(unittest.TestCase):

def main():
    unittest.main()

if __name__ == '__main__':
    main()

