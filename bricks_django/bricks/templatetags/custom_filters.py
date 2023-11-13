from django import template
from django.urls import reverse

register = template.Library()

@register.filter(name='is_dark_color')

def is_dark_color(value):
    # Extract RGB values from the format RGB(255, 255, 255)
    rgb_values = [int(val) for val in value[4:-1].split(',')]
    
    # Calculate brightness using the same formula
    brightness = (rgb_values[0] * 299 + rgb_values[1] * 587 + rgb_values[2] * 114) / 1000
    
    return "#FFFFFF" if brightness < 128 else "#000000"

@register.simple_tag
def build_sort_link(sort_field, label, current_sort, current_order, request_get, referring_view):
    # Create a dictionary to represent the current query parameters
    query_dict = request_get.dict()
    
    # Determine the order for this link
    if sort_field == current_sort:
        # If the current sort field matches, toggle the order
        new_order = 'desc' if current_order == 'asc' else 'asc'
    else:
        # If it's a different sort field, default to ascending order
        new_order = 'asc'

    # Update the query parameters with the new sort and order
    query_dict['sort'] = sort_field
    query_dict['order'] = new_order

    # Use reverse to get the URL for the current view
    current_url = reverse(referring_view)

    # Set the query string of the URL to the updated query parameters
    query_string = '&'.join([f"{key}={value}" for key, value in query_dict.items()])
    current_url = f"{current_url}?{query_string}"
    
    return current_url