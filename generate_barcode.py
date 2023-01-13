import barcode
from PIL import Image
from barcode.writer import ImageWriter

def generate_barcode(bar_code):
    my_code = barcode.get('code128', bar_code, writer=ImageWriter())
    my_code.save('new', {"module_width":0.6, "module_height":30, "font_size": 20, "text_distance": 8.0, "quiet_zone": 6.5})
    new_file = Image.open('new.png')
    return new_file