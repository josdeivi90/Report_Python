import calendar
from tables.html_tables import simple_table
from utils.logic_operations.trend import calculate_trend

def generate_synthetic_tests_table(data):
    headings = ['Test']
    for i in range(data[0]['month']-1, data[0]['month']+len(data)-1):
        headings.append(calendar.month_abbr[(i%12)+1])
    headings.append('Trend')

    rows = []

    data_len = len(data)
    synthetic_tests_data = data[-1]['synthetic_tests_data']

    for test in synthetic_tests_data:
        cells = []
        penultimate_result = None
        test_name = test['test_name']
        cells.append(test_name)

        for month_position in range(data_len):
            month_data = data[month_position]['synthetic_tests_data']
            test_results = [x for x in month_data if x['test_name'] == test_name]

            result = test_results[0]['result'] if len(test_results) else 'N/A'
            result = result if result else 'N/A'
            
            if month_position == data_len - 2: #Second to last result
                penultimate_result = result if result != 'N/A' else None

            cells.append(f'{result}')
            if month_position == data_len - 1:
                result = result if result != 'N/A' else None
                trend = calculate_trend(penultimate_result, result)
                cells.append(trend)

        rows.append(cells)
    
    #column alignments
    align = ['left']

    for i in range(data_len):
        align.append('right')
        
    align.append('center')
    align.append('left')

    return simple_table(rows, headings, align, None)
