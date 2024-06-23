import calendar
from tables.html_tables import performance_table
from utils.logic_operations.trend import calculate_trend

def generate_prisma_cloud_table(data):
    vulnerabilities = ['Critical', 'High', 'Medium']
    vulnerabilities_len = len(vulnerabilities)
    headings = ['Service', 'Impact']
    data_len = len(data)

    for i in range(data[0]['month']-1, data[0]['month']+len(data)-1):
        headings.append(calendar.month_abbr[(i%12)+1])

    headings.append(' Trend ')
    rows = []
    
    prisma_data = data[-1]['prisma_data']
    
    for application in prisma_data:
        application_name = application['application']

        for j in range(vulnerabilities_len):
            cells = []
            cells.append(application_name)
            cells.append(vulnerabilities[j])

            for month_position in range(len(data)):
                impact = vulnerabilities[j].lower()
                month_data = data[month_position]['prisma_data']

                results = [x for x in month_data if x['application'] == application_name]
                result = results[0]['total'][impact] if len(results) else 'N/A'
                result = result if result != None else 'N/A'

                if month_position == data_len - 2: #Second to last result
                    penultimate_result = result if result != 'N/A' else None

                score = f'<small>{result}</small>'
                cells.append(score)

                if month_position == data_len - 1:
                    result = result if result != 'N/A' else None
                    trend = calculate_trend(penultimate_result, result)
                    cells.append(trend)

            rows.append(cells)
    
    align = ['left','left']

    for i in range(data_len):
        align.append('right')
        
    align.append('center')
    align.append('left')

    table = performance_table(rows, headings, align, vulnerabilities_len)
    return table