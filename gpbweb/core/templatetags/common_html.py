from django import template
from django.utils.safestring import mark_safe
from django.utils.html import escape

register = template.Library()

def firstupper(value):
    """ Convierte la primera letra de un string a mayuscula"""
    if not isinstance(value, (str, unicode,)): return s
    else: return mark_safe(value[0].upper() + value[1:])

register.filter('first_upper', firstupper)
