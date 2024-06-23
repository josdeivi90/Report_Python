import calendar
from utils.logic_operations.trend import calculate_trend
from tables.html_tables import simple_table

def generate_availability_table(data, teams_metrics, all_data = False):
    availability_data = None
    
    if teams_metrics and 'availability' in teams_metrics:
        availability_data = teams_metrics['availability']
    headings = ['Service']

    for i in range(data[0]['month']-1, data[0]['month']+len(data)-1):
        headings.append(calendar.month_abbr[(i%12)+1])
    
    headings.append('SLA')
    headings.append('Trend')
    rows = []

    data_len = len(data)
    availability_data_results =  [x for x in data[-1]['availability_data'] if x['subscription'] == 'prod']
    env_list = ['prod', 'nonprod', 'sandbox', 'demo', 'preprod']
    rowclasses = []
    for env_position in range(len(env_list)):
        if all_data or env_list[env_position] == 'prod':
            for application in availability_data_results:
                cells = []
                we_got_data = False
                penultimate_result = None
                application_name = application['service']
                cells.append(application_name)
                for month_position in range(data_len):
                    month_data = data[month_position]['availability_data']
                    results = [x for x in month_data if x['service'] == application_name and x['subscription'] == env_list[env_position]]
   
                    result = results[0]['availability'] if len(results) else 'N/A'
                    result = result if result else 'N/A'
                    
                    if result == 'N/A':
                        cells.append(result)
                        continue
                    
                    we_got_data = True
                    avail =  '{:.5f}'.format(result)+'%'

                    if month_position == data_len - 2: #Second to last result
                        penultimate_result = result if result != 'N/A' else None

                    if month_position == data_len - 1 and availability_data:
                        color = availability_data[application_name]['color']

                        if color != 'green' and env_list[env_position] == 'prod':
                            color = color if color == 'yellow' else 'red'
                            avail = f'<td bgcolor=\'{color}\' style=\'text-align:right\'><b>{avail}</b></td>'
                    cells.append(avail)

                    if month_position == data_len - 1:
                        result = result if result != 'N/A' else None
                        trend = calculate_trend(penultimate_result, result)
                
                if we_got_data:
                    cells.append('99.00000%')
                    cells.append(trend)
                    rows.append(cells)
                    if all_data:
                        rowclasses.append(env_list[env_position])

    #column alignments
    align = ['left']

    for i in range(data_len):
        align.append('right')
        
    align.append('right')
    align.append('center')
    align.append('left')

    if all_data:
        return simple_table(rows, headings, align, rowclasses)
    else:
        return simple_table(rows, headings, align, None)