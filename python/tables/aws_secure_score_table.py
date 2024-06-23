import calendar
from tables.html_tables import simple_table
from utils.logic_operations.trend import calculate_trend

def generate_aws_secure_score_table(data):
    headings = ['Subscription']
    for i in range(data[0]['month']-1, data[0]['month']+len(data)-1):
        headings.append(calendar.month_abbr[(i%12)+1])
    headings.append('Trend')

    rows = []

    data_len = len(data)
    aws_secure_score_data = data[-1]['aws_secure_score_data']

    for account in aws_secure_score_data:
        cells = []
        penultimate_result = None
        subscription = account['subscription']
        cells.append(subscription)

        for month_position in range(data_len):
            month_data = data[month_position]['aws_secure_score_data']
            results = [x for x in month_data if x['subscription'] == subscription]
            
            score = results[0]['score'] if len(results) else 'N/A'
            score = score if score else 'N/A'

            if month_position == data_len - 2: #Second to last result
                penultimate_result = score if score != 'N/A' else None

            cells.append(f'{score}')

            if month_position == data_len - 1:
                score = score if score != 'N/A' else None
                trend = calculate_trend(penultimate_result, score)
                cells.append(trend)

        rows.append(cells)
    
    #column alignments
    align = ['left']

    for i in range(data_len):
        align.append('right')
        
    align.append('center')
    align.append('left')

    return simple_table(rows, headings, align, None)