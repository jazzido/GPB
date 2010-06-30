from django import template
from datetime import datetime
import re

register = template.Library()

class MesesNode(template.Node):
    def __init__(self, varname, current=datetime.now(), start_year=datetime.now().year):
        self.current_time = current
        self.varname = varname

    def render(self, context):
        context[self.varname] = []
        for y in reversed(range(start_year, self.current_time.year+1)):
            context[self.varname] = [datetime(y, m, 1) for m in reversed(range(1, self.current_time.month+1 if self.current_time.year == y else 12+1))]
        return ''

def do_meses(parser, token):
    try:
        # Splitting by None == splitting by spaces.
        tag_name, arg = token.contents.split(None, 1)
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires arguments" % token.contents.split()[0]

    m = re.search(r'from (?P<start>.+) until (?P<until_year>.+) as (?P<variable_name>\w+)', arg)
    

    

