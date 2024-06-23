import calendar
from utils.logic_operations.trend import calculate_trend
from tables.html_tables import performance_table

def generate_pd_table(data, teams_metrics):
    performance_data = None

    if teams_metrics and 'performance' in teams_metrics:
        performance_data = teams_metrics['performance']

    metrics = ['MTTA', 'MTTR', 'MTBF']
    units = ['min', 'min', 'hr']
    headings = ['Team', 'Metric']

    for i in range(data[0]['month'] - 1, data[0]['month'] + len(data) - 1):
        headings.append(calendar.month_abbr[(i % 12) + 1])

    headings.append(' Trend ') #The extra spaces here trigger tables.html_tables.py to swap trend colors.  Down is green here
    rows = []

    metrics_len = len(metrics)
    data_len = len(data)
    pd_data = data[-1]['pd_data']

    for team in pd_data:
        penultimate_result = None
        team_name = team['team']['name']

        for i in range(metrics_len):
            cells = []
            cells.append(team_name)
            cells.append(metrics[i])

            result = None

            for month_position in range(data_len):
                month_data = data[month_position]['pd_data']
                results = [x for x in month_data if x['team']['name'] == team_name]

                result = results[0]['data'][metrics[i]] if len(results) else 'N/A'

                if month_position == data_len - 2: #Second to last result
                    penultimate_result = result if result != 'N/A' else None

                if result is None:
                    cells.append('N/A')
                else:
                    metric = f'{result} {units[i]}'

                    if performance_data and month_position == data_len - 1 and i < 2:
                        color = performance_data[team_name][metrics[i]]['color']

                        if color != 'green':
                            color = color if color == 'yellow' else 'red'
                            metric = f'<td bgcolor=\'{color}\' style=\'text-align:right\'><b>{metric}</b></td>'

                    cells.append(metric)
            
            trend = calculate_trend(penultimate_result, result)
            cells.append(trend)
            rows.append(cells)
            
    #column alignments
    align = ['left','left']

    for i in range(data_len):
        align.append('right')
        
    align.append('center')
    align.append('left')

    return performance_table(rows, headings, align,3)