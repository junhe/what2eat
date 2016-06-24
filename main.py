# -*- coding: utf-8 -*-
import argparse
from what2eat.menu import *

def create_menu(n_meat, n_vege, mode):
    menu = menu_from_file('menu.xlsx')
    picked = menu.pick(order={
        TYPE_MEAT: n_meat,
        TYPE_VEGETABLE: n_vege,
        TYPE_PERMANENT: 1,
        },
        mode=mode
        )

    print '================================================ MENU =================================================='
    print str(picked)
    send(picked)

def send(picked):
    ans = raw_input("Send to TODOist? (y/n): ")
    if ans.lower().strip() == 'y':
        picked.send_ingredients_map('project.141578026.3993020@todoist.net')
        print 'All ingredients sent to TODOist'
        print str(picked)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--meat', default=0, action='store')
    parser.add_argument('-v', '--vegetable', default=0, action='store')
    parser.add_argument('-d', '--mode', default='semi', action='store',
            help='hand/auto/semi')
    args = parser.parse_args()

    create_menu(int(args.meat), int(args.vegetable), args.mode)

if __name__ == '__main__':
    main()



