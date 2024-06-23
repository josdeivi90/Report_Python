def calculate_trend(value1, value2):
    #Treat None as zero
    value1 = 0 if not value1 else value1
    value2 = 0 if not value2 else value2

    if value1 > value2:
        trend = '&#8595'
    elif value2 > value1:
        trend = '&#8593'
    else:
        trend = '&#8596'

    return trend