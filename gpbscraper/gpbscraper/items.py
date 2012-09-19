# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/topics/items.html

from scrapy.item import Item, Field
from scrapy.contrib.loader.processor import TakeFirst, MapCompose, Join
import string, re

from datetime import date

spanish_date = lambda day,month,year: date(int(year),int(month),int(day))

MONEY_RE = re.compile(r'([\d\.]*),(\d+)')

def parse_money(value):
    pesos, centavos = MONEY_RE.match(value.strip()).groups()
    pesos = pesos.replace('.', '')
    return float("%s.%s" % (pesos if pesos != '' else 0, centavos))

class ProveedorItem(Item):
    nombre = Field(output_processor=TakeFirst())
    domicilio = Field(output_processor=TakeFirst())
    cuit = Field(output_processor=TakeFirst())
    localidad = Field(output_processor=TakeFirst())

class CompraItem(Item):
    orden_compra = Field(output_processor=TakeFirst())
    fecha = Field(output_processor=lambda x: spanish_date(*(x[0].split('/'))).strftime('%Y-%m-%d'))
    importe = Field(output_processor=lambda x: parse_money(x[0]))
    proveedor = Field(output_processor=TakeFirst())
    suministro = Field(output_processor=TakeFirst())
    destino = Field(output_processor=TakeFirst())
    # LPRI: Lic.Privada
    # LPUB: Lic. Publica
    # CODI: Compra directa unico proveedor
    # CDVP: Compra directa varios proveedores
    # CONC: Concurso de precios
    tipo_compra = Field(output_processor=TakeFirst())
    anio = Field(output_processor=TakeFirst())
    compra_linea_items = Field()
    tipo = Field(output_processor=TakeFirst())

class CompraLineaItem(Item):
    cantidad = Field(output_processor=TakeFirst())
    unidad_medida = Field(output_processor=TakeFirst())
    importe = Field(output_processor=lambda x: parse_money(x[0]))
    importe_total = Field(output_processor=lambda x: parse_money(x[0]))
    detalle = Field(output_processor=TakeFirst())
    anio = Field(output_processor=TakeFirst())



