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




