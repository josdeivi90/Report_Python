import calendar
from utils.logic_operations.trend import calculate_trend
from tables.html_tables import simple_table

def generate_app_cost_table(data, teams_metrics):
    headings = ['Application']

    if teams_metrics and 'cost' in teams_metrics:
        cost_data = teams_metrics['cost']

    for i in range(data[0]['month']-1, data[0]['month']+len(data)-1):
        headings.append(calendar.month_abbr[(i%12)+1])

    headings.append(' Trend ')
    rows = []
    totals = []

    data_len = len(data)
    cost_data_results = data[-1]['app_cost_data']

    for x in range(data_len): totals.append(0)

    for application in cost_data_results:
        cells = []
        application_name = application['application']
        cells.append(application_name)

        for month_position in range(data_len):
            month_data = data[month_position]['app_cost_data']
            results = [x for x in month_data if x['application'] == application_name]
            
            totalcost = results[0]['total'] if len(results) else 'N/A'
            totalcost = totalcost if totalcost else 'N/A'
            
            if totalcost == 'N/A':
                cells.append(totalcost)
            else:
                totals[month_position] += totalcost
                totaldollars =  '${:.2f}'.format(totalcost)

                if month_position == data_len - 1 and cost_data:
                    color = cost_data[application_name]['color']
                    if color != 'green':
                        color = color if color == 'yellow' else 'red'
                        totaldollars = f'<td bgcolor=\'{color}\' style=\'text-align:right\'><b>{totaldollars}</b></td>'
                
                cells.append(totaldollars)

            if month_position == data_len - 1:
                trend = results[0]['trend']
        
        if trend<0:
            cells.append('&#8595 {:.2f}%'.format(trend * -1))
        elif trend == 0:
            cells.append('&#8596 0.00% ')
        else:
            cells.append('&#8593 {:.2f}%'.format(trend))

        rows.append(cells)

    align = ['left']

    for i in range(data_len):
        align.append('right')

    align.append('center')
    align.append('left')
    

    return simple_table(rows, headings, align, None)