from django import template
from .models import *


register = template.Library()

@register.filter
def length_is_right(value):
    option = Option.objects.filter(question_id=int(value))
    i = 0
    for x in option:
        if x.is_right:
            i += 1
            
    return int(i)