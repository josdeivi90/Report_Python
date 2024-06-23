import calendar
from utils.logic_operations.trend import calculate_trend
from utils.svgstuff import draw_compliance_bar, draw_security_bar
from tables.html_tables import performance_table

def generate_secure_score_table(data, png):
    metrics = ['Secure Score', 'ISO 27001:2013', 'Azure CIS 1.4.0', 'SOC 2 Type 2']
    metrics_len = len(metrics)
    headings = ['Subscription', 'Metric']

    for i in range(data[0]['month'] - 1, data[0]['month'] + len(data) - 1):
        headings.append(calendar.month_abbr[(i % 12) + 1])

    headings.append('Trend')
    rows = []

    data_len = len(data)
    security_data = data[-1]['security_data']

    for sub in security_data:
        subscription_name = sub['subscription']
        penultimate_secure_score = None
        penultimate_iso_27001_2013 = None
        penultimate_azure_cis_1_4_0 = None
        penultimate_soc_2_type_2 = None

        for i in range(metrics_len):
            cells = []
            cells.append(subscription_name)
            cells.append(metrics[i])

            for month_position in range(data_len):
                month_data = data[month_position]['security_data']
                results = [x for x in month_data if x['subscription'] == subscription_name]
                
                if len(results): 
                    results = results[0]
                
                else:
                    cells.append('<small>N/A</small>')
                    continue

                if i == 0: #Secure score
                    score = results['score']

                    if score is None:
                        value = '<small>N/A</small>'
                    else:
                        value = draw_security_bar(score, png)
                    
                    cells.append(value)

                    if month_position == data_len - 2: penultimate_secure_score = score

                    if month_position == data_len - 1:
                        trend = calculate_trend(penultimate_secure_score, score)
                        cells.append(trend)

                elif i == 1: #iso_27001_2013
                    score = results['iso_27001_2013']['pass']
                    fail_value = results['iso_27001_2013']['fail']

                    if score is None:
                        value = '<small>N/A</small>'
                    else:
                        value = draw_compliance_bar(score, fail_value, 0, png)
                        #note: ignoring skipped for iso:27001:2013.  If it returns to normal, change that zero to 'data[k]['security_data'][i]['iso_27001_2013']['skip']'
                    
                    cells.append(value)

                    if month_position == data_len - 2: penultimate_iso_27001_2013 = score

                    if month_position == data_len - 1:
                        trend = calculate_trend(penultimate_iso_27001_2013, score)
                        cells.append(trend)

                elif i == 2: #azure cis 1.4.0
                    score = results['azure_cis_1_4_0']['pass']
                    fail_value = results['azure_cis_1_4_0']['fail']
                    skip_value = results['azure_cis_1_4_0']['skip']

                    if score is None:
                        value = '<small>N/A</small>'
                    else:
                        value = draw_compliance_bar(score, fail_value, skip_value, png)
                    
                    cells.append(value)

                    if month_position == data_len - 2: penultimate_azure_cis_1_4_0 = score

                    if month_position == data_len - 1:
                        trend = calculate_trend(penultimate_azure_cis_1_4_0, score)
                        cells.append(trend)

                elif i == 3: #soc_2_type_2
                    score = results['soc_2_type_2']['pass']
                    fail_value = results['soc_2_type_2']['fail']
                    skip_value = results['soc_2_type_2']['skip']

                    if score is None:
                        value = '<small>N/A</small>'
                    else:
                        value = draw_compliance_bar(score, fail_value, skip_value, png)
                    
                    cells.append(value)

                    if month_position == data_len - 2: penultimate_soc_2_type_2 = score

                    if month_position == data_len - 1:
                        trend = calculate_trend(penultimate_soc_2_type_2, score)
                        cells.append(trend)
            
            rows.append(cells)
            
    #column alignments
    align = ['left','left']

    for i in range(data_len):
        align.append('right')

    align.append('center')
    align.append('left')
    return performance_table(rows, headings, align, metrics_len)