from utils.convert_svg_to_png import svg_to_png

compliance_svg = '''
    <svg width="150" height="14">
        <rect width="150" height="14" fill="#FF8080" />
        <rect width="100" height="14" fill="#A0A0A0" />
        <rect width="50" height="14" fill="#88FF88" />
        <text x="116" y="11" fill="#000000" font-size="10px">FAIL</text>
        <text x="65" y="11" fill="#000000" font-size="10px">SKIP</text>
        <text x="12" y="11" fill="#000000" font-size="10px">PASS</text>
    </svg>
'''

def compliance_sub(png = True):
    compliance_html_code = svg_to_png(compliance_svg) if png else compliance_svg
    return compliance_html_code