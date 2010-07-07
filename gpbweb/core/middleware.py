# coding: utf-8
from gpbweb.core.models import Compra
from gpbweb.core.urls import anual_expression, mensual_expression, periodo_expression
import re
from django.conf import settings
from django import http
from django.core.urlresolvers import resolve


class StripDateRangeMiddleware(object):

    def process_request(self, request):
        request.gpb_base_url = request.path
        request.gpb_date_range = ''
        for r in [r'^(.*)/' + exp + '$' for exp in periodo_expression, mensual_expression, anual_expression]:
            m = re.match(r, request.path)
            if m is not None:
                request.gpb_base_url = m.groups()[0] + '/'
                if request.gpb_base_url == '/': request.gpb_base_url = ''
                request.gpb_date_range = '/'.join(m.groups()[1:])
                print request.gpb_date_range
                return None


class DateLimitsMiddleware:
    """ Hacer que las fechas maxima y minima de Compras este en request """
    
    def process_request(self, request):
        if request.path.startswith('/admin'):
            return None

        request.fecha_minima = Compra.objects.order_by('fecha')[:1][0].fecha
        request.fecha_maxima = Compra.objects.order_by('-fecha')[:1][0].fecha


class SmartAppendSlashMiddleware(object):
    """
    "SmartAppendSlash" middleware for taking care of URL rewriting.

    This middleware appends a missing slash, if:
    * the SMART_APPEND_SLASH setting is True
    * the URL without the slash does not exist
    * the URL with an appended slash does exist.
    Otherwise it won't touch the URL.
    """

    def process_request(self, request):
        """
        Rewrite the URL based on settings.SMART_APPEND_SLASH
        """

        # Check for a redirect based on settings.SMART_APPEND_SLASH
        host = http.get_host(request)
        old_url = [host, request.path]
        new_url = old_url[:]
        # Append a slash if SMART_APPEND_SLASH is set and the resulting URL
        # resolves.
        if settings.SMART_APPEND_SLASH: 
            if (not old_url[1].endswith('/')) and not _resolves(old_url[1]) and _resolves(old_url[1] + '/'):
                new_url[1] = new_url[1] + '/'
                if settings.DEBUG and request.method == 'POST':
                    raise RuntimeError, "You called this URL via POST, but the URL doesn't end in a slash and you have SMART_APPEND_SLASH set. Django can't redirect to the slash URL while maintaining POST data. Change your form to point to %s%s (note the trailing slash), or set SMART_APPEND_SLASH=False in your Django settings." % (new_url[0], new_url[1])
            else:
                if (old_url[1].endswith('/')) and _resolves(old_url[1][:-1]):
                    new_url[1] = old_url[1][:-1]
                    
            if new_url != old_url:
                # Redirect
                if new_url[0]:
                    newurl = "%s://%s%s" % (request.is_secure() and 'https' or 'http', new_url[0], new_url[1])
                else:
                    newurl = new_url[1]
                if request.GET:
                    newurl += '?' + request.GET.urlencode()
                return http.HttpResponsePermanentRedirect(newurl)

        return None

def _resolves(url):
    try:
        resolve(url)
        return True
    except http.Http404:
        return False
