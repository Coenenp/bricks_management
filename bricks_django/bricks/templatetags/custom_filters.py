from django import template

register = template.Library()

@register.filter(name='is_dark_color')

def is_dark_color(value):
    # Extract RGB values from the format RGB(255, 255, 255)
    rgb_values = [int(val) for val in value[4:-1].split(',')]
    
    # Calculate brightness using the same formula
    brightness = (rgb_values[0] * 299 + rgb_values[1] * 587 + rgb_values[2] * 114) / 1000
    
    return "#FFFFFF" if brightness < 128 else "#000000"