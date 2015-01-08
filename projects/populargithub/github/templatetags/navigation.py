from django import template
import re

register = template.Library()

@register.simple_tag
def active(request, pattern, doSpan):
    
    if re.search(pattern, request.path):
        if doSpan:
            return '<span class="sr-only">(current)</span>'
        else:
            return 'active'
    
    return ''