# coding: utf-8
from django import template
from datetime import datetime, date
import re, calendar
from django.utils.safestring import mark_safe


register = template.Library()

class TiempoEnLetrasNode(template.Node):

    """ Node para convertir rangos de fechas a una expresión en castellano:
          - "En lo que va del año 2011"
          - "Entre los meses de X e Y de Z"
    """

    def __init__(self, start_varname, end_varname, template_varname):
        self.start_time = template.Variable(start_varname)
        self.end_time = template.Variable(end_varname)
        self.template_varname = template_varname
        
    def render(self, context):
        now = date.today()

        self.start_time = self.start_time.resolve(context).date()
        self.end_time = self.end_time.resolve(context).date()

        rv = ''

        # presente año o un año completo
        if self.start_time.month == 1 and self.start_time.day == 1 and self.end_time.day == 31 and self.end_time.month == 12:
            if self.start_time.year == now.year:
                rv = "en lo que va del <strong>año %s</strong>" % self.start_time.year
            else:
                rv = "en el <strong>año %s</strong>" % self.start_time.year
        # presente mes
        elif (now.year, now.month, 1) == (self.start_time.year, self.start_time.month, self.start_time.day) \
                and now <= date(self.end_time.year, self.end_time.month, calendar.monthrange(self.end_time.year, self.end_time.month)[1]):
            rv = "en lo que va del mes de <strong>%s de %s</strong>" % (self.start_time.strftime("%B"), self.start_time.strftime("%Y"))

        elif now > self.start_time:
            # un mes completo
            if self.start_time.month == self.end_time.month \
                and self.start_time.day == 1 \
                and self.end_time.day == calendar.monthrange(self.end_time.year, self.end_time.month)[1] \
                and self.end_time.year == self.start_time.year:

                rv = "en el mes de <strong>%s de %s</strong>" % (self.start_time.strftime("%B"), self.start_time.strftime("%Y"))
            elif self.start_time.year < self.end_time.year:
                rv = "entre <strong>%s de %s y %s de %s</strong>" % (self.start_time.strftime("%B"), self.start_time.strftime("%Y"),
                                                                                  self.end_time.strftime("%B"), self.end_time.strftime("%Y"))
            # periodo de tiempo en el mismo año
            else:
                rv = "entre <strong>%s y %s de %s</strong>" % (self.start_time.strftime("%B"), self.end_time.strftime("%B"),
                                                                   self.end_time.strftime("%Y"))

        context[self.template_varname] = mark_safe(rv)
        return ''


def do_tiempo_en_letras(parser, token):
    try:
        tag_name, start_varname, end_varname, _as, template_varname = token.contents.split(None, 4)
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires arguments" % token.contents.split()[0]

    return TiempoEnLetrasNode(start_varname, end_varname, template_varname)

register.tag('tiempo_en_letras', do_tiempo_en_letras)

