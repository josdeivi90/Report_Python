import os

def days_in_month(month, year):
    DAYS_IN_MONTH = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    if ((month == 2) and ((year % 400 == 0) or (year % 100 != 0)) and (year % 4 == 0)):
        return 29
    else:
        return DAYS_IN_MONTH[month-1]