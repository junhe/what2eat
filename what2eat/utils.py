from openpyxl import load_workbook

def read_xls(path):
    wb = load_workbook(path)
    sheet = wb.active

    header = [c.value for c in sheet.rows[0]]

    table = []
    for row in sheet.rows[1:]:
        row = [cell.value for cell in row]
        row = dict(zip(header, row))
        table.append(row)

    return table


def adjust_width(s, width = 32):
    return s.rjust(width)


def table_to_str(table, adddic=None, sep=';', width=32):
    """
    table is of format: [
                    {'col1':data, 'col2':data, ..},
                    {'col1':data, 'col2':data, ..},
                    {'col1':data, 'col2':data, ..},
                    ]
    output is:
        col1   col2   col3 ..
        data   data   data ..
    """
    if len(table) == 0:
        return None

    tablestr = ''
    colnames = table[0].keys()
    if adddic != None:
        colnames += adddic.keys()
    colnamestr = sep.join([adjust_width(s, width=width) for s in colnames]) + '\n'
    tablestr += colnamestr
    for row in table:
        if adddic != None:
            rowcopy = dict(row.items() + adddic.items())
        else:
            rowcopy = row
        rowstr = [rowcopy[k] for k in colnames]
        rowstr = [x if isinstance(x, basestring) else str(x) for x in rowstr]
        rowstr = [adjust_width(x, width=width) for x in rowstr]
        rowstr = sep.join(rowstr) + '\n'
        tablestr += rowstr

    return tablestr.encode('utf-8')





