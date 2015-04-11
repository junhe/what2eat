# -*- coding: utf-8 -*-
import csv, codecs, cStringIO
import copy
from collections import Counter
import random
import subprocess
import pprint

def file_to_table():
    #with codecs.open('./dataset.txt', 'r', encoding='utf-16') as f:
    with codecs.open('./recipe.cache.csv', 'r', encoding='utf-8') as f:
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

    # pprint.pprint( table )
    return table

def count_meat_and_vege(table):
    # count meat and vege
    meat = 0
    vege = 0
    for row in table:
        if row['MEAT'] == '1':
            meat += 1
        elif row['MEAT'] == '0':
            vege += 1
    # print meat, vege
    return meat,vege

def get_meat_vege_id(table):
    # get the id of all the meat and vege items
    meatlist = []
    vegelist = []
    for i,row in enumerate(table):
        if row['MEAT'] == '1':
            meatlist.append(i)
        else:
            vegelist.append(i)

    # print meatlist
    # print vegelist
    return meatlist, vegelist

def get_marked_entries(table, meatlist, vegelist):
    # get the items already marked
    meat_chosen = []
    vege_chosen = []

    for i in meatlist:
        if table[i]['COOK?'] == '1':
            meat_chosen.append(i)

    for i in vegelist:
        if table[i]['COOK?'] == '1':
            vege_chosen.append(i)

    # print meat_chosen
    # print vege_chosen
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
        print subject
        # send_email(['junjohnhe@gmail.com'], subject.encode('utf-8'))
        send_email(['project.141578026.3993020@todoist.net'], subject.encode('utf-8'))
        # TO = ['junjohnhe@gmail.com', '] #must be a list

def main():
    table = file_to_table()
    meat,vege = count_meat_and_vege(table)

    # in total, how many do you want for each
    n_meat = 2
    n_vege = 2

    meatlist, vegelist = get_meat_vege_id(table)

    meat_chosen, vege_chosen = get_marked_entries(table, meatlist, vegelist)

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
    # print meat_chosen
    # print vege_chosen

    # mark the chosen ones
    for i,row in enumerate(table):
        if i in meat_chosen or i in vege_chosen:
            row['COOK?'] = '1'

    # filter out the un-chosen
    choices = []
    for row in table:
        if not (row['COOK?'] == '0' or row['COOK?'] == ''):
            choices.append(row)

    # count the number of each integrades
    items = []
    for row in choices:
        items.extend(row['Recipe'])
    counter = dict(Counter(items))

    counter2 = copy.deepcopy(counter)
    choices2 = copy.deepcopy(choices)

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

    isok = raw_input("Is the menu OK? (y/n)")
    if isok.lower() == 'y':
        # find which entry each item is for
        itemtoentry = {}
        for k,v in counter2.items():
            if counter2[k] > 0:
                entries = []
                for row in choices2:
                    if k in row['Recipe']:
                        entries.append(row['Entry'])
                itemtoentry[k] = entries
        # print itemtoentry
        send_items_by_email(itemtoentry)
    else:
        print 'did NOT send to TODOist'

if __name__ == '__main__':
    main()


