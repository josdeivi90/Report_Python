import re
from utils.fix_align import fix_align
from utils.check_rows import is_row_null

def performance_table(rows, headings, align, rowspan, classname = None):

    assert len(headings) == len(rows[0])

    # output the headers
    th_block = '<table><thead>'
    col = 0
    for head in headings:
        th_block += '<th style=\'text-align:'+align[col]+'\'>'+head+'</th>'
        col += 1
    th_block += '</thead>'
    td_block = ''
    rownum = 1
    for row in rows:
        if classname is None:
            td_block += '<tr>'
        else:
            td_block += '<tr class=\''+classname+' table\'>'
        col = 0
        for i in range(len(row)):
            colorstyle = trend_color(headings[i],row[i],row[1])
            if col == 0: ## or col==1 
                if ((rownum%rowspan)==1): 
                    td_block += '<td style=\'text-align:'+align[col]+colorstyle+'\' rowspan=\''+str(rowspan)+'\'>'+row[i]+'</td>'
            else:
                if 'bgcolor' in row[i]:
                    td_block += row[i]
                else:
                    td_block += '<td style=\'text-align:'+align[col]+colorstyle+'\'>'+row[i]+'</td>'
            col += 1
        td_block += '</tr>'
        rownum += 1
    if classname == 'env':
        output = ''+th_block+td_block
    else: 
        output = ''+th_block+td_block+'</table>'
    return output

def simple_table(rows, headings, align, rowclasses = None):

    assert len(headings) == len(rows[0])

    # output the headers
    th_block = '<table><thead>'
    col = 0
    rowcounter = 0
    for head in headings:
        th_block += '<th style=\'text-align:'+align[col]+'\'>'+head+'</th>'
        col += 1
    th_block += '</thead>'
    td_block = ''
    for row in rows:
        boldness = ''
        if row[0]=='Total':
            boldness=';font-weight: bold'
        if rowclasses is None:
            td_block += '<tr>'
        else:  
            td_block += '<tr class=\''+rowclasses[rowcounter]+' table\'>'
        rowcounter += 1
        col = 0
        for i in range(len(row)):
            if 'bgcolor' in row[i]:
                td_block += row[i]
            else:
                colorstyle = trend_color(headings[i],row[i],'')
                td_block += '<td style=\'text-align:'+align[col]+colorstyle+boldness+'\'>'+row[i]+'</td>'
            col += 1
        td_block += '</tr>'


    output = ''+th_block+td_block+'</table>'
    return output

def trend_color(column,value, metric):
    colorstyle=''
    if column == 'Trend' or metric=='MTBF':
        if '&#8593' in value:
            colorstyle=';color:green'
        elif '&#8595' in value:
            colorstyle=';color:red'
    elif column == ' Trend ' or column == ' Current Trend':
        if '&#8593' in value:
            colorstyle=';color:red'
        elif '&#8595' in value:
            colorstyle=';color:green'
    return colorstyle



def generate_html_cloud_cost_table(rows, headings, align, rowspan):

    assert len(headings) == len(rows[0])

    # output the headers
    th_block = '<table><thead>'
    col = 0
    
    for head in headings:
        th_block += '<th style=\'text-align:'+align[col]+'\'>'+head+'</th>'
        col += 1
    th_block += '</thead>'
    td_block = ''
    rownum = 1
    
    for row in rows:
        td_block += '<tr>'
        col = 0
        len_row = len(row)
        
        null_row = is_row_null(row)
        # Since all rows have different lengths, we need to fix the alignment for each one
        new_align = fix_align(align, len_row) if not null_row else align

        for i in range(len_row):
            
            if len(headings) != len (row) and headings[i] == headings[-2]:
                heading_position = headings[-1]
            else:
                heading_position = headings[i]

            colorstyle = trend_color(heading_position, row[i], row[1])
            is_provider_name = True if re.match('AWS|Azure', row[col], re.IGNORECASE) else False
            
            if col == 0 or is_provider_name:
                if rownum%rowspan == 1: 
                    td_block += '<td style=\'text-align:'+new_align[col]+colorstyle+'\' rowspan=\''+str(rowspan)+'\'>'+row[i]+'</td>'
            elif not null_row:
                td_block += '<td style=\'text-align:'+new_align[col]+colorstyle+'\'>'+row[i]+'</td>'
            col += 1
        td_block += '</tr>'
        rownum += 1
        output = ''+th_block+td_block+'</table>'

    return output
