# -*- coding: utf-8 -*-
import csv, codecs, cStringIO
import copy
from collections import Counter
import random
import subprocess
import pprint
import numbers
import sys

from openpyxl import load_workbook

def read_xls_to_table(path):
    wb = load_workbook(path)
    sheet = wb.active

    header = [c.value for c in sheet.rows[0]]

    table = []
    for row in sheet.rows[1:]:
        row = [cell.value if cell.value is not None else '' for cell in row]
        row = dict(zip(header, row))
        table.append(row)

    return table


def file_to_table():
    #with codecs.open('./dataset.txt', 'r', encoding='utf-16') as f:
    with codecs.open('./menu.cache.csv', 'r', encoding='utf-8') as f:
    # with codecs.open('./toy.txt', 'r') as f:
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

    return table

def count_meat_and_vege(table):
    # count meat and vege
    meat = 0
    vege = 0
    for row in table:
        if row['MEAT'] == 1:
            meat += 1
        elif row['MEAT'] == 0:
            vege += 1
    return meat,vege

def split_meat_vege_ids(table):
    # get the id of all the meat and vege items
    meat_id_list = []
    vege_id_list = []
    for i,row in enumerate(table):
        if row['MEAT'] == 1:
            meat_id_list.append(i)
        elif row['MEAT'] == 0:
            vege_id_list.append(i)
        else:
            raise RuntimeError("{} is not valid value".format(row['MEAT']))

    return meat_id_list, vege_id_list

def is_chosen(value):
    return not value in ('', 0)

def get_marked_entries(table, meatlist, vegelist):
    # get the items already marked
    meat_chosen = []
    vege_chosen = []

    for i in meatlist:
        if is_chosen(table[i]['COOK?']):
            meat_chosen.append(i)

    for i in vegelist:
        if is_chosen(table[i]['COOK?']):
            vege_chosen.append(i)

    return meat_chosen, vege_chosen

def send_email(tolist, subject):
    import smtplib
    import getpass

    gmail_user = "ojunhe@gmail.com"
    with open('./email.config', 'r') as f:
        gmail_pwd = f.readline().strip()
    # gmail_pwd = getpass.getpass('enter your password:')
    FROM = 'ojunhe@gmail.com'
    TO = tolist
    SUBJECT = subject
    TEXT = "Left empty intentionally."

    # Prepare actual message
    message = """\From: %s\nTo: %s\nSubject: %s\n\n%s
    """ % (FROM, ", ".join(TO), SUBJECT, TEXT)

    #server = smtplib.SMTP(SERVER)
    server = smtplib.SMTP("smtp.gmail.com", 587) #or port 465 doesn't seem to work!
    server.ehlo()
    server.starttls()
    server.login(gmail_user, gmail_pwd)
    server.sendmail(FROM, TO, message)
    server.close()
    print 'successfully sent the mail'

def send_items_by_email(itemtoentry):
    for item, elist in itemtoentry.items():
        ents = u','.join(elist)
        subject = u"{itemname} ({entries})".format(
                    itemname = item,
                    entries = ents)
        print subject.encode("utf-8")
        send_email(['project.141578026.3993020@todoist.net'], subject.encode('utf-8'))


def print_table(table):
    for row in table:
        values = [str(v) if isinstance(v, numbers.Number) else v.encode("utf-8") for v in row.values()]
        print ', '.join(values)

def sample_rows(table, n_meat, n_vege):
    """
    n_meat, n_vege: the number we want
    """
    print 'Will sample', n_meat, "meat", n_vege, "vege"
    meat_id_list, vege_id_list = split_meat_vege_ids(table)

    meat_chosen, vege_chosen = get_marked_entries(
            table, meat_id_list, vege_id_list)

    # remove chosen items from list
    meat_id_list = [x for x in meat_id_list if not x in meat_chosen]
    vege_id_list = [x for x in vege_id_list if not x in vege_chosen]

    # pick the rest
    nmeat_left = n_meat - len(meat_chosen)
    if nmeat_left < 0:
        nmeat_left = 0
    nvege_left = n_vege - len(vege_chosen)
    if nvege_left < 0:
        nvege_left = 0

    meat_chosen = meat_chosen + random.sample(meat_id_list, nmeat_left)
    vege_chosen = vege_chosen + random.sample(vege_id_list, nvege_left)

    chosen_ids = meat_chosen + vege_chosen

    return [row for i, row in enumerate(table) if i in chosen_ids]

def mark_chosen_ones(table, meat_chosen, vege_chosen):
    for i,row in enumerate(table):
        if i in meat_chosen or i in vege_chosen:
            row['COOK?'] = 1

def count_integrands(table):
    items = []
    for row in table:
        items.extend(row['Recipe'].split("|"))
    count = dict(Counter(items))

    return count

def build_table_for_display(table):
    table = copy.deepcopy(table)
    count = count_integrands(table)

    # build a table for display
    header = ['Entry', 'COOK?', 'MEAT'] + count.keys()
    for row in table:
        rowitems = row['Recipe'].split("|")
        del row['Recipe']
        for item in count.keys():
            cnt = rowitems.count(item)
            if cnt == 0:
                cnt = ''
            row[item] = cnt

    add_summary_row(table, count)

    table.sort(key=lambda k: k['MEAT'], reverse=False)

    return table

def add_summary_row(table, count):
    counterrow = copy.copy(count)
    counterrow['Entry'] = 'Summary'
    counterrow['COOK?'] = len([1 for row in table if is_chosen(row['COOK?'])])
    counterrow['MEAT']  = len([1 for row in table if row['MEAT'] == 1])

    table.append(counterrow)

def save_to_csv(table, path):
    with codecs.open(path, 'wb', encoding='utf-8') as f:
        # write header
        prefix = ['Entry', 'MEAT', 'COOK?']
        header = table[0].keys()
        header = [x for x in header if not x in prefix]
        header = prefix + header

        line = ','.join(header) + '\n'
        f.write(line)

        for row in table:
            row['Entry'] = row['Entry'].encode('utf-8')
            items = [row[k] for k in header]
            items = [str(x) for x in items]
            line = ','.join(items) + '\n'
            f.write(line.decode('utf-8'))

def save_and_open(table):
    path = 'tmp.csv'
    save_to_csv(table, path)
    subprocess.call("open -a /Applications/Numbers.app/ {}".format(path), shell=True)

def send_to_todoist(table):
    table = copy.deepcopy(table)
    count = count_integrands( table )

    isok = raw_input("Is the menu OK? (y/n)")
    if isok.lower() == 'y':
        # find which entry each item is for
        itemtoentry = {}
        for k,v in count.items():
            if count[k] > 0:
                entries = []
                for row in table:
                    if k in row['Recipe']:
                        entries.append(row['Entry'])
                itemtoentry[k] = entries
        send_items_by_email(itemtoentry)
    else:
        print 'did NOT send to TODOist'

def rows_for_cook(table):
    return [row for row in table if is_chosen(row['COOK?'])]

def main():
    if len(sys.argv) != 3:
        print "Usage:", sys.argv[0], "#meat #vege"
        exit(1)
    n_meat = int(sys.argv[1])
    n_vege = int(sys.argv[2])

    table = read_xls_to_table("./menu.xlsx")
    orig_table = copy.deepcopy(table)

    chosen_rows = sample_rows(table, n_meat, n_vege)

    table_display = build_table_for_display(chosen_rows)
    save_and_open(table_display)

    send_to_todoist(chosen_rows)

if __name__ == '__main__':
    main()


