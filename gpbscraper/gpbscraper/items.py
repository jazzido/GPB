# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/topics/items.html

from scrapy.item import Item, Field

class ProveedorItem(Item):
    # define the fields for your item here like:
    # name = Field()
    nombre = Field()
    domicilio = Field()
    cuit = Field()
    localidad = Field()

class CompraItem(Item):
    orden_compra = Field()
    # TODO aca un input processor que parsee la fecha
    fecha = Field()
    # TODO aca un input processor que convierta los strings tipo "12.123,00" a un numero normal
    importe = Field()
    suministro = Field()
    proveedor = Field()
    destino = Field()
    # XXX lista de dicts?
    compra_lineas = Field()
