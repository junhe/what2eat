import csv, codecs, cStringIO
import copy
from collections import Counter
import random
import subprocess
import pprint

class UTF16Recoder:
    """
    Iterator that reads an encoded stream and reencodes the input to UTF-16
    """
    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode("utf-16")

class UnicodeReader:
    """
    A CSV reader which will iterate over lines in the CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-16", **kwds):
        f = UTF16Recoder(f, encoding)
        self.reader = csv.reader(f, dialect=dialect, **kwds)

    def next(self):
        row = self.reader.next()
        return [unicode(s, "utf-16") for s in row]

    def __iter__(self):
        return self

class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-16", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([s.encode("utf-16") for s in row])
        # Fetch UTF-16 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-16")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)

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

    meat_choices = random.sample(range(meat), 7)
    vege_choices = random.sample(range(vege), 7)

    meat_i = 0
    vege_i = 0
    for row in table:
        row['COOK?'] = '0' #overwrite
        if row['MEAT'] == '1':
            if meat_i in meat_choices:
                row['COOK?'] = '1'
            meat_i += 1
        else:
            if vege_i in vege_choices:
                row['COOK?'] = '1'
            vege_i += 1

    # filter the un-chosen
    choices = []
    for row in table:
        # print 'cook?', row['COOK?']
        if not (row['COOK?'] == '0' or row['COOK?'] == ''):
            # print 'chosen'
            choices.append(row)
    print '---------------'
    print choices

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
            row[item] = rowitems.count(item)
    print choices

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
            print row['Entry']
            items = [row[k] for k in header]
            items = [str(x) for x in items]
            print items
            line = ','.join(items) + '\n'
            f.write(line.decode('utf-8'))
    subprocess.call("open -a /Applications/Numbers.app/ tmp.csv", shell=True)

if __name__ == '__main__':
    main()


