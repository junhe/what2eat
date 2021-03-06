# -*- coding: utf-8 -*-
import unittest

from what2eat.utils import *
from what2eat.table import *
from what2eat.menu import *

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
        menu = menu_from_file("./tests/menusample.xlsx")

        rows = menu.sample(TYPE_VEGETABLE, 1).raw_table().rows()
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
        menu = menu_from_file("./tests/menusample.xlsx")

        sampled_table = menu.sample(TYPE_MEAT, 2).raw_table()
        rows = sampled_table.rows()
        self.assertEqual(len(rows), 2)
        self.assertIn(rows[0]['EntryName'], self.meat_entries())
        self.assertIn(rows[1]['EntryName'], self.meat_entries())
        self.assertNotEqual(rows[0]['EntryName'], rows[1]['EntryName'])

    def test_add_and_sample(self):
        menu = menu_from_file("./tests/menusample.xlsx")

        sampled_table = menu.add_and_sample(TYPE_MEAT, 2).raw_table()
        self.assertIn(u'肉末酸豆角', sampled_table.col('EntryName'))
        self.assertEqual(sampled_table.n_rows(), 2)

    def test_pick(self):
        menu = menu_from_file("./tests/menusample.xlsx")

        picked_table = menu.pick({TYPE_MEAT: 2, TYPE_VEGETABLE: 2},
                mode='auto').raw_table()

        self.assertEqual(picked_table.n_rows(), 3) # only one vege available
        meat_entries = picked_table.filter_equal(COL_ENTRYTYPE, TYPE_MEAT)\
                .col(COL_ENTRYNAME)
        for entryname in meat_entries:
            self.assertIn(entryname, self.meat_entries())

    def test_ingredients_to_entry(self):
        menu = menu_from_file("./tests/menusample.xlsx")

        table = menu.sample(TYPE_VEGETABLE, 1).raw_table()
        menu2 = Menu(table)
        i_map = menu2.ingredients_map()
        d = i_map.raw_dict()

        self.assertDictEqual(d, {u'丝瓜': [u'丝瓜蛋汤'],
            u'蛋': [u'丝瓜蛋汤']})

    def test_multiple_entries(self):
        menu = menu_from_file("./tests/menusample.xlsx")
        table = menu.raw_table()

        t = table.filter_equal(COL_ENTRYNAME, u'肉末酸豆角')
        t2 = table.filter_equal(COL_ENTRYNAME, u'辣椒酿')
        t.extend(t2)

        new_menu = Menu(t)

        i_map = new_menu.ingredients_map()
        text_lines = i_map.text_lines()

        self.assertIn(u'肉末 (肉末酸豆角,辣椒酿)', text_lines)

    def test_flatten(self):
        i_map = IngredientMap({u'丝瓜': [u'丝瓜蛋汤'],
                               u'蛋': [u'丝瓜蛋汤']})
        lines = i_map.text_lines()

        self.assertIn(u'丝瓜 (丝瓜蛋汤)', lines)
        self.assertIn(u'蛋 (丝瓜蛋汤)', lines)
        self.assertEqual(len(lines), 2)

    def test_building_structure(self):
        storemap = StoreMap("./item-map.txt")
        i_map = IngredientMap({u'丝瓜': [u'丝瓜蛋汤'],
                               u'蛋': [u'丝瓜蛋汤']},
                storemap)

        structure = i_map.get_structure()

        self.assertDictEqual(structure,
                {u"Wenhua": [u'丝瓜 (丝瓜蛋汤)'],
                 u"Costco": [u'蛋 (丝瓜蛋汤)']})

    def test_split_ingredients(self):
        menu = Menu()
        self.assertListEqual(menu._ingredients({COL_INGREDIENTS: "a|b|c"}),
                ['a', 'b', 'c'])

    def test_remove(self):
        menu = menu_from_file("./tests/menusample.xlsx")

        entryname = u'丝瓜蛋汤'
        self.assertIn(entryname, menu.raw_table().col(COL_ENTRYNAME))
        menu.remove(u'丝瓜蛋汤')
        self.assertNotIn(entryname, menu.raw_table().col(COL_ENTRYNAME))

    def test_prompt_and_pick(self):
        menu = menu_from_file("./tests/menusample.xlsx")

        sampled_table = menu.hand_pick(TYPE_MEAT, 2, test=True).raw_table()
        rows = sampled_table.rows()
        self.assertEqual(len(rows), 2)
        self.assertIn(rows[0]['EntryName'], self.meat_entries())
        self.assertIn(rows[1]['EntryName'], self.meat_entries())
        self.assertNotEqual(rows[0]['EntryName'], rows[1]['EntryName'])

    def test_semi_prompt_and_pick(self):
        menu = menu_from_file("./tests/menusample.xlsx")

        sampled_table = menu.semi_hand_pick(TYPE_MEAT, 2, test=True).raw_table()
        rows = sampled_table.rows()
        self.assertEqual(len(rows), 2)
        self.assertIn(rows[0]['EntryName'], self.meat_entries())
        self.assertIn(rows[1]['EntryName'], self.meat_entries())
        self.assertNotEqual(rows[0]['EntryName'], rows[1]['EntryName'])


class TestItemMap(unittest.TestCase):
    def test_map(self):
        d = load_map("./item-map.txt")
        self.assertEqual(d['香茹'], 'Wenhua')

    def test_map_class(self):
        mymap = StoreMap("./item-map.txt")
        self.assertEqual(mymap.storename('香茹'), 'Wenhua')
        self.assertEqual(mymap.storename('香茹xx'), 'UNKONWN')



def main():
    unittest.main()

if __name__ == '__main__':
    main()

