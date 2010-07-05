from gpbweb.core.models import Compra

class DateLimitsMiddleware:
    """ Hacer que las fechas maxima y minima de Compras este en request """
    
    def process_request(self, request):
        if request.path.startswith('/admin'):
            return None

        request.fecha_minima = Compra.objects.order_by('fecha')[:1][0].fecha
        request.fecha_maxima = Compra.objects.order_by('-fecha')[:1][0].fecha
