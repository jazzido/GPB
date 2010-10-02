from scrapy.contrib.exporter import JsonLinesItemExporter
import datetime
import simplejson

def handler(obj):
    if isinstance(obj, datetime.datetime):
        return obj.isoformat()
    else:
        raise TypeError, 'Object of type %s with value of %s is not JSON serializable' % (type(Obj), repr(Obj))


class TypedJsonLinesItemExporter(JsonLinesItemExporter):
    """
Like JsonLinesItemExporter but each line adds the item type.

Example:
['LegisladorItem', {...LegisladorItem data...}]
"""

    def export_item(self, item):
        itemtype = item.__class__.__name__
        itemdict = dict(self._get_serialized_fields(item))
        self.file.write(self.encoder.encode([itemtype, itemdict]) + '\n')

    def serialize_field(self, field, name, value):
        if name == 'fecha':
            return value.isoformat()
        return JsonLinesItemExporter.serialize_field(self, field, name, value)
        

        

