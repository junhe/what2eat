from what2eat.utils import read_xls,tobytes

def get_input():
    dic = {"c": "Costco",
            "w": "Wenhua",
            "s": "Sentry"}

    while True:
        ret = raw_input("Which store (Costco/Wenhua/Sentry)?")
        if not ret in ("c", "w", "s"):
            continue
        else:
            return dic[ret]

def get_my_items():
    table = read_xls("./menu.xlsx")

    myitems = set()
    for row in table:
        items = tobytes(row[u'Ingredients']).split('|')
        for myitem in items:
            myitems.add(myitem)

    return myitems

    # f_map = open("item-map.txt", "w")

def main():
    myitems = get_my_items()

    f = open("item-map.txt", "w")

    for myitem in myitems:
        print myitem
        store = get_input()
        line =  ",".join([myitem, store]) + '\n'
        print line,
        f.write(line)
        f.flush()


if __name__ == '__main__':
    main()

