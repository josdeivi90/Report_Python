import calendar
from utils.logic_operations.costs_per_subscription import calc_cost_per
from tables.html_tables import generate_html_cloud_cost_table
from utils.logic_operations.trend import calculate_trend

def generate_cloud_cost_table(data):
    headings = ['Subscription', 'Provider', 'Metric']

    for i in range(data[0]['month']-1, data[0]['month']+len(data)-1):
        headings.append(calendar.month_abbr[(i%12)+1])
    headings.append('Reduction (Gain)')
    headings.append(' Trend ')

    rows = []
    totals = []
    ests = []

    data_len = len(data)

    azure_cost_data = data[-1]['cost_data']

    for j in range(data_len):
        totals.append(0)
        ests.append(False)
    
    #Azure data

    for subscription in azure_cost_data:
        cells = []
        subcells = []
        subsubcells = []
        subscription_name = subscription['name']
        cells.append(subscription_name)
        cells.append('Azure')
        cells.append('Total Cost')
        subcells.append(subscription_name)
        subsubcells.append(subscription_name)
        maxcost = 0
        subcells.append('<small>Cost/Active User</small>')
        subsubcells.append('<small>Cost/User Session</small>')

        for month_position in range(data_len):
            month_data = data[month_position]['cost_data']
            results = [x for x in month_data if x['name'] == subscription_name]
            subscription_data = results[0] if len(results) else None

            est = ''
            if subscription_data and subscription_data['estimated']:
                est = '<small> (est)</small>'
                ests[month_position] = True
            
            totalcost = subscription_data['total'] if subscription_data else 0

            if totalcost == 0:
                cells.append('N/A'+est)
                subcells.append('N/A'+est)
                subsubcells.append('N/A'+est)
                continue

            if totalcost > maxcost:
                maxcost = totalcost #keep track of the maximum seen for this sub
            
            totals[month_position] += totalcost
            totaldollars =  '${:.2f}'.format(totalcost)
            cells.append(totaldollars + est)

            totalper = calc_cost_per(totalcost, data[month_position]['usage_data']['active_users'], subscription_name)

            if totalper:
                totalperdollars = '<small> ${:.2f}</small>'.format(totalper)
                subcells.append(totalperdollars + est)
            else:
                subcells.append('<small> N/A</small>')

            totalpersess = calc_cost_per(totalcost, data[month_position]['usage_data']['user_sessions'], subscription_name)

            if totalpersess:
                totalpersessdollars = '<small> ${:.2f}</small>'.format(totalpersess)
                subsubcells.append(totalpersessdollars + est)
            else:
                subsubcells.append('<small> N/A</small>')
            
            if month_position == data_len - 1:
                first_month_data = data[0]['cost_data']
                first_month_results = [x for x in first_month_data if x['name'] == subscription_name]
                first_month_subscription_data = first_month_results[0] if len(first_month_results) else None
                total_cost_data = first_month_subscription_data['total'] if first_month_subscription_data else 0

                if total_cost_data == 0:
                    reduction = 0
                    subreduction = 0
                    subsubreduction = 0
                else:
                    reduction = (1 - (totalcost/total_cost_data)) * 100
                    calc_cost_per_0 = calc_cost_per(total_cost_data, data[0]['usage_data']['active_users'], subscription_name)
                    
                    second_month_data = data[1]
                    second_month_results = [x for x in second_month_data['cost_data'] if x['name'] == subscription_name]
                    second_month_subscription_data = second_month_results[0] if len(second_month_results) else None
                    
                    calc_cost_per_1 = calc_cost_per(second_month_subscription_data['total'], second_month_data['usage_data']['user_sessions'], subscription_name)

                    if calc_cost_per_0 == 0 or calc_cost_per_1 == 0:
                        subreduction = None
                        subsubreduction = None
                    else:
                        subreduction = (1 - totalper/calc_cost_per_0) * 100
                        subsubreduction = (1 - totalpersess/calc_cost_per_1) * 100
                
                trend = calculate_trend(reduction, 0)
                subtrend = calculate_trend(subreduction, 0)
                subsubtrend = calculate_trend(subsubreduction, 0)

        if reduction < 0:
            cells.append('({:.2f}%)'.format(reduction * -1))
        else:
            cells.append('{:.2f}%'.format(reduction))
        
        if subreduction is None:
            subcells.append ('N/A')
        elif subreduction < 0:
            subcells.append('<small>({:.2f}%)</small>'.format(subreduction * -1))
        else:
            subcells.append('<small>{:.2f}%</small>'.format(subreduction))

        if subsubreduction is None:
            subsubcells.append ('N/A')
        elif subsubreduction < 0:
            subsubcells.append('<small>({:.2f}%)</small>'.format(subsubreduction * -1))
        else:
            subsubcells.append('<small>{:.2f}%</small>'.format(subsubreduction))

        cells.append(trend)
        subcells.append(subtrend)
        subsubcells.append(subsubtrend)

        #For html file: Only add subs that have data over $100
        if maxcost > 100:  
            rows.append(cells)
            rows.append(subcells)
            rows.append(subsubcells)

    #AWS data
    aws_cost_data = data[-1]['aws_cost_data']
    
    for subscription in aws_cost_data:
        cells = []
        app_name = subscription['account']
        cells.append(app_name)
        cells.append('AWS')
        cells.append('Total Cost')

        subcells = ['AWS', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A']
        subsubcells = ['AWS', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A']

        for month_position in range(data_len):
            month_data = data[month_position]['aws_cost_data']
            results = [x for x in month_data if x['account'] == app_name]
            subscription_data = results[0] if len(results) else None

            totalcost = subscription_data['total'] if subscription_data else None

            if not totalcost:
                cells.append('N/A')
            else:
                totals[month_position] += totalcost
                totaldollars =  '${:.2f}'.format(totalcost)
                cells.append(totaldollars)
            
            if month_position == data_len - 1:
                trend = subscription_data['trend']

        if trend < 0:
            cells.append('{:.2f}%'.format(trend * -1))
            cells.append('&#8595')
        elif trend == 0:
            cells.append(' 0.00% ')
            cells.append('&#8596')
        else:
            cells.append('({:.2f}%)'.format(trend))
            cells.append('&#8593')

        rows.append(cells)
        rows.append(subcells)
        rows.append(subsubcells)

    #add total row
    cells = []
    cells.append('<b>Total</b>')
    cells.append('')
    cells.append('<b>Total Cost</b>')


    total_len = len(totals)

    for x in range(total_len):
        est = ''

        if ests[x]:
            est = '<b> (est)</b>'

        cells.append('<b>${:.2f}'.format(totals[x]) + est + '</b>')
    
    reduction = (1 - totals[total_len-1]/totals[0]) * 100

    if reduction < 0:
        cells.append('<b>({:.2f}%)</b>'.format(reduction * -1))
    else:
        cells.append('<b>{:.2f}%</b>'.format(reduction))

    trend = calculate_trend(totals[total_len - 2], totals[total_len - 1])
    cells.append(trend)
    rows.append(cells)

    #column alignments
    align = ['left', 'left', 'left']
    
    for i in range(data_len):
        align.append('right')
    
    align.append('right')
    align.append('center')

    generated_table = generate_html_cloud_cost_table(rows, headings, align, 3)
    
    return generated_table