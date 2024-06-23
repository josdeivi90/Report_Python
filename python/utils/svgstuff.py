from utils.convert_svg_to_png import svg_to_png

def draw_compliance_bar(passed, failed, skipped, png = True):
    total = passed+failed+skipped
    p_ratio = passed/total
    f_ratio = failed/total
    s_ratio = skipped/total
    p_wide = passed>9
    f_wide = failed>9
    s_wide = skipped>9
    output_str = '<svg width="100" height="15">'
    output_str += '<rect width="100" height="15" fill="#FF8080" />'
    output_str += f'<rect width="{str(int((s_ratio+p_ratio)*100))}" height="15" fill="#A0A0A0" />'
    output_str += f'<rect width="{str(int(p_ratio*100))}" height="15" fill="#80FF80" />'
    if (passed>0):
        output_str += f'<text x="{str((int(p_ratio*100)/2)-(3*(p_wide+1)))}" y="11" fill="#000000" font-size="10px">{str(passed)}</text>'
    if (skipped>0):
        output_str += f'<text x="{str(int(p_ratio*100)+(int((s_ratio)*100)/2)-(3*(s_wide+1)))}" y="11" fill="#000000" font-size="10px">{str(skipped)}</text>'
    if (failed>0):
        output_str += f'<text x="{str(100-(int((f_ratio)*100)/2)-(3*(f_wide+1)))}" y="11" fill="#000000" font-size="10px">{str(failed)}</text>'
    output_str += '</svg>'
    output_str = svg_to_png(output_str) if png else output_str
    return output_str

def draw_security_bar(value, png = True):
    label = '{:.2f}%'.format(value)
    output_str = '<svg width="100" height="15"><defs><linearGradient id="Gradient">'
    output_str += f'<stop offset="{str(int(value))}%" stop-color="#80FF80"/><stop offset="100%" stop-color="#FF8080"/></linearGradient></defs>'
    output_str += f'<rect width="100" height="15" fill="url(#Gradient)"/><text x="35" y="11" fill="#000000" font-size="12px">{label}</text></svg>'
    output_str = svg_to_png(output_str) if png else output_str
    return output_str