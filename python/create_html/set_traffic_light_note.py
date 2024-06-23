traffic_light_notes = {
    'security' : {
        'green' : 'Production secure score 80% or greater',
        'yellow' : 'Production secure score between 60% and 80%',
        'red' : 'Production secure score less than 60%'
    },
    'availability' : {
        'green' : 'All apps at 99.99% available or better',
        'yellow' : 'At least one app availability is less than 99.99%, but greater than 99%',
        'red' : 'At least one app availability falls below 99%'
    },
    'performance' : {
        'green' : 'Most incident metrics are in acceptable range',
        'yellow' : 'Some incident metrics trending in wrong direction',
        'red' : 'Several incident metrics are in unacceptable ranges'
    },
    'cost' : {
        'green' : 'Costs are under 110% of budget',
        'yellow' : 'Costs are between 110% and 150% of budget',
        'red' : 'Costs are over 150% of budget'
    }
}

def set_traffic_light_note(whichlight, color):
    note = traffic_light_notes[whichlight][color]
    return note