import csv, codecs, cStringIO
import copy
from collections import Counter
import random
import subprocess
import pprint

def main():
    #with codecs.open('./dataset.txt', 'r', encoding='utf-16') as f:
    with codecs.open('./fullrecipecsv.csv', 'r', encoding='utf-8') as f:
    #with codecs.open('./toy.txt', 'r') as f:
        header = False
        table = []
        for line in f:
            line = line.strip()
            items = line.split(',')
            if header == False:
                header = items
            else:
                row = dict(zip(header, items))
                if row.has_key(''):
                    del row['']
                if row.has_key('Recipe'):
                    row['Recipe'] = row['Recipe'].split('|')
                table.append(row)

    # print table

    # count meat and vege
    meat = 0
    vege = 0
    for row in table:
        if row['MEAT'] == '1':
            meat += 1
        elif row['MEAT'] == '0':
            vege += 1

    # get the id of all the meat and vege items
    meatlist = []
    vegelist = []
    for i,row in enumerate(table):
        if row['MEAT'] == '1':
            meatlist.append(i)
        else:
            vegelist.append(i)

    print meatlist
    print vegelist

    n_meat = 7
    n_vege = 7

    # get the items already marked
    meat_chosen = []
    vege_chosen = []

    for i in meatlist:
        if table[i]['COOK?'] == '1':
            meat_chosen.append(i)

    for i in vegelist:
        if table[i]['COOK?'] == '1':
            vege_chosen.append(i)

    print meat_chosen
    print vege_chosen

    # remove chosen items from list
    meatlist = [x for x in meatlist if not x in meat_chosen]
    vegelist = [x for x in vegelist if not x in vege_chosen]

    # pick the rest
    nmeat_left = n_meat - len(meat_chosen)
    if nmeat_left < 0:
        nmeat_left = 0
    nvege_left = n_vege - len(vege_chosen)
    if nvege_left < 0:
        nvege_left = 0

    meat_chosen = meat_chosen + random.sample(meatlist, nmeat_left)
    vege_chosen = vege_chosen + random.sample(vegelist, nvege_left)
    print meat_chosen
    print vege_chosen

    for i,row in enumerate(table):
        if i in meat_chosen or i in vege_chosen:
            row['COOK?'] = '1'

    # filter the un-chosen
    choices = []
    for row in table:
        # print 'cook?', row['COOK?']
        if not (row['COOK?'] == '0' or row['COOK?'] == ''):
            # print 'chosen'
            choices.append(row)

    # count the number of each integrades
    items = []
    for row in choices:
        items.extend(row['Recipe'])

    counter = dict(Counter(items))

    # build a table for display
    header = ['Entry', 'COOK?', 'MEAT'] + counter.keys()
    for row in choices:
        rowitems = row['Recipe']
        del row['Recipe']
        for item in counter.keys():
            cnt = rowitems.count(item)
            if cnt == 0:
                cnt = ''
            row[item] = cnt

    counterrow = copy.copy(counter)
    counterrow['Entry'] = 'Summary'
    counterrow['COOK?'] = len([1 for row in choices if row['COOK?'] == '1'])
    counterrow['MEAT']  = len([1 for row in choices if row['MEAT'] == '1'])

    choices.append(counterrow)

    choices.sort(key=lambda k: k['MEAT'], reverse=False)

    with codecs.open('tmp.csv', 'wb', encoding='utf-8') as f:
        # write header
        line = ','.join(header) + '\n'
        f.write(line)

        for row in choices:
            row['Entry'] = row['Entry'].encode('utf-8')
            items = [row[k] for k in header]
            items = [str(x) for x in items]
            line = ','.join(items) + '\n'
            f.write(line.decode('utf-8'))
    subprocess.call("open -a /Applications/Numbers.app/ tmp.csv", shell=True)

if __name__ == '__main__':
    main()


