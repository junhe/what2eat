import csv, codecs, cStringIO
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
    with codecs.open('./recipe.csv', 'r', encoding='utf-8') as f:
    #with codecs.open('./toy.txt', 'r') as f:
        header = False
        table = []
        for line in f:
            line = line.strip()
            items = line.split(',')
            print items
            if header == False:
                header = items
            else:
                row = dict(zip(header, items))
                table.append(row)
                
    #pprint.pprint( table )
    print table 

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
        print 'cook?', row['COOK?']
        if not (row['COOK?'] == '0' or row['COOK?'] == ''):
            print 'chosen'
            choices.append(row)
    print '---------------'
    print choices

    counter = {}
    for col in header:
        for row in choices:
            if col == 'Entry':
                continue
            print 'row[col]',row[col]
            val = row[col].strip().encode('ascii')
            if val == '':
                val = 0
            val = int(val)
            
            if not counter.has_key(col):
                counter[col] = 0
            counter[col] += val
    print "counter"
    print counter

    for k, v in counter.items():
        print k,v
        if v == 0:
            # del column k
            header.remove(k)
            for row in table:
                del row[k]

    print counter
    print choices

    counter2 = {}
    counter2[u'Entry'] = 'Count'
    for k,v in counter.items():
        if v != 0:
            counter2[k] = str(v)
    choices.insert(0, counter2)
    
    choices.sort(key=lambda k: k['MEAT'], reverse=True)

    with codecs.open('tmp.csv', 'wb', encoding='utf-8') as f:
        # write header
        line = ','.join(header) + '\n'
        f.write(line)

        for row in choices:
            items = [row[k] for k in header]
            line = ','.join(items) + '\n'
            f.write(line)
    subprocess.call("open -a /Applications/Numbers.app/ tmp.csv", shell=True)

if __name__ == '__main__':
    main()


