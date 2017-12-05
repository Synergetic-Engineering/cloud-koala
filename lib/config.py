import os
import uuid

from openpyxl import load_workbook


def _find_input_output(workbook):
    input_datalists = {}
    output_datalists = {}
    for sheet in workbook:
        input_datalists[sheet.title.encode('utf-8')] = []
        output_datalists[sheet.title.encode('utf-8')] = []

        for col in sheet.iter_cols():
            for cell in col:
                if cell.value is None:
                    continue
                elif isinstance(cell.value, unicode):
                    continue
                elif isinstance(cell.value, (float, long)):
                    input_datalists[sheet.title.encode('utf-8')].append(str(cell.column) + str(cell.row))
                elif isinstance(cell.value, str) and cell.value.startswith('='):
                    output_datalists[sheet.title.encode('utf-8')].append(str(cell.column) + str(cell.row))

        # If sheet is empty, delete it from dictionary
        if input_datalists[sheet.title.encode('utf-8')] == []:
            del input_datalists[sheet.title.encode('utf-8')]
        if output_datalists[sheet.title.encode('utf-8')] == []:
            del output_datalists[sheet.title.encode('utf-8')]
    return input_datalists, output_datalists


def _generate_config_rows(cell_type, datalists):
    for elements in datalists:
        for coords in datalists[elements]:
            yield cell_type, elements, coords


def create_config_sheet(file_string):
    # XXX HACK this was required for koala but haven't worked out if it's required for openpyxl yte
    if not os.path.exists('/tmp'): # mainly required for dev / test environment
        os.mkdir('/tmp')
    temp_id = uuid.uuid4().hex
    dummy_excel_file_name = '/tmp/temp_excel_file_{}.xlsx'.format(temp_id)
    with open(dummy_excel_file_name, 'wb') as fp:
        fp.write(file_string)

    workbook = load_workbook((dummy_excel_file_name), data_only=False)
    input_datalists, output_datalists = _find_input_output(workbook)
    rows = [('type', 'sheet', 'cell')]
    rows.extend(_generate_config_rows('input', input_datalists))
    rows.extend(_generate_config_rows('output', output_datalists))
    config_sheet = workbook.create_sheet("cloud-koala-config")
    for row in rows:
        config_sheet.append(row)
    workbook.save(dummy_excel_file_name)
    with open(dummy_excel_file_name, 'rb') as fp:
        new_file_string = fp.read()

    # XXX cleans up previous workaround
    os.remove(dummy_excel_file_name)
    if not os.listdir('/tmp'):
        os.rmdir('/tmp')

    return new_file_string
