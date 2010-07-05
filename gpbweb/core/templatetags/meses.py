from django import template
from datetime import datetime, date
import re

register = template.Library()

class MesesNode(template.Node):
    def __init__(self, start_varname, end_varname, template_varname):
        self.start_var = template.Variable(start_varname)
        self.end_var = template.Variable(end_varname)
        self.template_varname = template_varname

    def render(self, context):
        meses = []
        start = self.start_var.resolve(context)#.date()
        end = self.end_var.resolve(context)#.date()

        m = start.month
        y = start.year
        d = date(y, m, 1)
        while True:
            if d > end: break
            meses.append(d)
            m += 1
            if m % 12 == 1:
                y += 1
            d = date(y, m % 12 if m % 12 != 0 else 12, 1)
        
        context[self.template_varname] = meses
        return ''

def do_meses(parser, token):
    try:
        # Splitting by None == splitting by spaces.
        tag_name, _from, start_varname, _until, end_varname, _as, template_varname = token.contents.split(None, 6)
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires arguments" % token.contents.split()[0]

    return MesesNode(start_varname, end_varname, template_varname)
    
register.tag('month_range', do_meses)

    

