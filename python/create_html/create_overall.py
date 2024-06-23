from utils.configuration import load_configuration
from utils.convert_svg_to_png import svg_to_png
from utils.set_traffic_lights import *
from create_html.set_traffic_light_note import set_traffic_light_note

notes = load_configuration('./data/notes.json')

availability_svg = '''
        <svg width="800" height="80">
            <rect x="5" y="0" rx="15" ry="15" width="660" height="60" fill="#CCCCCC" />
            <rect x="15" y="10" rx="15" ry="15" width="125" height="40" fill="#000000" />
            <circle cx="40" cy="30" r="13" fill="$avail_red$" />
            <circle cx="77" cy="30" r="13" fill="$avail_yellow$" />
            <circle cx="114" cy="30" r="13" fill="$avail_green$" />
            <text fill="#000000" font-weight="bold" font-size="26" x="150" y="30">AVAILABILITY</text>
            <text fill="#000000" font-size="13" x="150" y="50">$availability_note$</text>
        </svg>
    '''

performance_svg = '''
    <svg width="800" height="80">
        <rect x="5" y="0" rx="15" ry="15" width="660" height="60" fill="#CCCCCC" />
        <rect x="15" y="10" rx="15" ry="15" width="125" height="40" fill="#000000" />
        <circle cx="40" cy="30" r="13" fill="$perform_red$" />
        <circle cx="77" cy="30" r="13" fill="$perform_yellow$" />
        <circle cx="114" cy="30" r="13" fill="$perform_green$" />
        <text fill="#000000" font-weight="bold" font-size="26" x="150" y="30">PERFORMANCE</text>
        <text fill="#000000" font-size="13" x="150" y="50">$performance_note$</text>
    </svg>
'''

cost_svg = '''
    <svg width="800" height="80">
        <rect x="5" y="0" rx="15" ry="15" width="660" height="60" fill="#CCCCCC" />
        <rect x="15" y="10" rx="15" ry="15" width="125" height="40" fill="#000000" />
        <circle cx="40" cy="30" r="13" fill="$cost_red$" />
        <circle cx="77" cy="30" r="13" fill="$cost_yellow$" />
        <circle cx="114" cy="30" r="13" fill="$cost_green$" />
        <text fill="#000000" font-weight="bold" font-size="26" x="150" y="30">COST</text>
        <text fill="#000000" font-size="13" x="150" y="50">$cost_note$</text>
    </svg>
'''

security_svg = '''
    <svg width="800" height="80">
        <rect x="5" y="0" rx="15" ry="15" width="660" height="60" fill="#CCCCCC" />
        <rect x="15" y="10" rx="15" ry="15" width="125" height="40" fill="#000000" />
        <circle cx="40" cy="30" r="13" fill="$sec_red$" />
        <circle cx="77" cy="30" r="13" fill="$sec_yellow$" />
        <circle cx="114" cy="30" r="13" fill="$sec_green$" />
        <text fill="#000000" font-weight="bold" font-size="26" x="150" y="30">SECURITY</text>
        <text fill="#000000" font-size="13" x="150" y="50">$security_note$</text>
    </svg>
'''

overall = {
    'availability': {
        'svg' : availability_svg,
        'key' : 'avail'
    },
    'performance': {
        'svg' : performance_svg,
        'key' : 'perform'
    },
    'cost': {
        'svg' : cost_svg,
        'key' : 'cost'
    },
    'security': {
        'svg' : security_svg,
        'key' : 'sec'
    }
}


def create_overall(data, png = True):
    availability_data, availability_light = set_availability_light(data)
    performance_data, performance_light = set_performance_light(data)
    cost_data, cost_light = set_cost_light(data)
    traffic_lights = {
        'security': set_security_light(data),
        'availability': availability_light,
        'performance' : performance_light,
        'cost': cost_light
    }

    traffic_lights_note = {
        'security': set_traffic_light_note('security', traffic_lights['security']),
        'availability': set_traffic_light_note('availability', traffic_lights['availability']),
        'performance' : set_traffic_light_note('performance', traffic_lights['performance']),
        'cost': set_traffic_light_note('cost', traffic_lights['cost'])
    }

    overall_html_code = ''

    for entry in overall.keys():
        temp_entry = overall[entry]
        temp_overall = temp_entry['svg'].replace(f'${entry}_note$',traffic_lights_note[entry])
        temp_overall = replace_traffic_light(temp_overall,temp_entry['key'],traffic_lights[entry])
        overall_html_code += svg_to_png(temp_overall) if png else temp_overall
    
    teams_metrics = {
        'availability' : availability_data,
        'performance' : performance_data,
        'cost' : cost_data
    }
    return teams_metrics, overall_html_code

