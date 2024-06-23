import re

def is_row_null(row):
    is_null = False
    
    if row[0] == 'AWS':
        is_null = True
    elif re.match('.*Cost\/((Active User)|(User Session)).*', row[1], re.IGNORECASE):
        new_row = row[:]
        new_row.pop(1)
        new_row.pop(0)
        new_row.pop(-1)
        new_row.pop(-1)
        
        for entry in new_row:
            if not 'N/A' in entry:
                return is_null
            
        is_null = True

    return is_null