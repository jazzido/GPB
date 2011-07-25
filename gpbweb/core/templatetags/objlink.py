from django import template
from django.utils.safestring import mark_safe
from django.utils.html import escape


register = template.Library()

@register.filter
def objlink(obj):
    """Renders an HTML <a> the given object, using its default unicode representation and url as returned by
    its ``get_absolute_url`` method (if any)."""
    if hasattr(obj, 'get_absolute_url'):
        return mark_safe(u'<a href="%s">%s</a>' % (escape(obj.get_absolute_url()), unicode(obj)))
    else:
        return unicode(obj)

@register.filter
def tablelink(obj):
    return mark_safe(u'<a href="%s" class="tablelink"><img src="/static/img/url_icon.gif" /></a> <a href="%s">%s</a>' % (escape(obj.get_absolute_url()), 
                                                                                                                         escape(obj.get_absolute_url()),
                                                                                                                         unicode(obj)))
