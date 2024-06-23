import uuid
from cairosvg import svg2png

def svg_to_png(svg_code):
    random_uid = uuid.uuid4()
    image_name = f'{random_uid}.png'
    image_path = f'images/{image_name}'
    
    svg2png(bytestring = svg_code, write_to = f'./report/{image_path}')
    html_code = f'<img src="{image_path}" alt="{image_name}">'
    
    return html_code
