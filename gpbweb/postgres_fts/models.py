"""
Support for full-text searchable Django models using tsearch2 in PostgreSQL.

An example:

from search import SearchableModel, SearchManager
from django.db import models

class TestModel (SearchableModel):
	name = models.CharField( max_length=100 )
	description = models.TextField()
	
	# Defining a SearchManager without fields will use all CharFields and TextFields
	# objects = SearchManager()
	
	# You can pass a list of fields that should be indexed
	# objects = SearchManager( fields=('name','description') )
	
	# You may also specify fields as a dictionary, mapping each field to a weight for ranking purposes
	# see http://www.postgresql.org/docs/8.3/static/textsearch-features.html#TEXTSEARCH-MANIPULATE-TSVECTOR
	objects = SearchManager( fields={
		'name': 'A',
		'description': 'B',
	} )

# Create some test data. By default, the index field is automatically updated when save() is called.
TestModel.objects.create( name='Model One', description='Hello world, this is a test.' )
TestModel.objects.create( name='Model Two', description='Testing, testing, one two three.' )

# You can force an index update to all or some instances:
TestModel.objects.update_index()
TestModel.objects.update_index( pk=1 )
TestModel.objects.update_index( pk=[1,2] )

# Perform a search with no ranking
TestModel.objects.search( 'hello' )

# Perform a search that ranks the results, orders by the rank, and assigns the ranking
# value to the field specified by rank_field
TestModel.objects.search( 'test', rank_field='rank' )
"""

from django.db import models

class VectorField (models.Field):
	
	def __init__( self, *args, **kwargs ):
		kwargs['null'] = True
		kwargs['editable'] = False
		kwargs['serialize'] = False
		super( VectorField, self ).__init__( *args, **kwargs )
	
	def db_type( self ):
		return 'tsvector'

class SearchableModel (models.Model):
	"""
	A convience Model wrapper that provides an update_index method for object instances,
	as well as automatic index updating. The index is stored as a tsvector column on the
	model's table. A model may specify a boolean class variable, _auto_reindex, to control
	whether the index is automatically updated when save is called.
	"""
	
	search_index = VectorField()
	
	class Meta:
		abstract = True
	
	def update_index( self ):
		if hasattr( self, '_search_manager' ):
			self._search_manager.update_index( pk=self.pk )
	
	def save( self, *args, **kwargs ):
		super( SearchableModel, self ).save( *args, **kwargs )
		if hasattr( self, '_auto_reindex' ):
			if self._auto_reindex:
				self.update_index()
		else:
			self.update_index()

class SearchManager (models.Manager):
	
	def __init__( self, fields=None, config=None ):
		self.fields = fields
		self.default_weight = 'A'
		self.config = config and config or 'pg_catalog.english'
		self._vector_field_cache = None
		super( SearchManager, self ).__init__()
	
	def contribute_to_class( self, cls, name ):
		# Instances need to get to us to update their indexes.
		setattr( cls, '_search_manager', self )
		super( SearchManager, self ).contribute_to_class( cls, name )
	
	def _find_text_fields( self ):
		"""
		Return the names of all CharField and TextField fields defined for this manager's model.
		"""
		fields = [f for f in self.model._meta.fields if isinstance(f,(models.CharField,models.TextField))]
		return [f.name for f in fields]
	
	def _vector_field( self ):
		"""
		Returns the VectorField defined for this manager's model. There must be exactly one VectorField defined.
		"""
		if self._vector_field_cache is not None:
			return self._vector_field_cache
		vectors = [f for f in self.model._meta.fields if isinstance(f,VectorField)]
		if len(vectors) != 1:
			raise ValueError( "There must be exactly 1 VectorField defined for the %s model." % self.model._meta.object_name )
		self._vector_field_cache = vectors[0]
		return self._vector_field_cache
	vector_field = property( _vector_field )
	
	def _vector_sql( self, field, weight=None ):
		"""
		Returns the SQL used to build a tsvector from the given (django) field name.
		"""
		if weight is None:
			weight = self.default_weight
		f = self.model._meta.get_field( field )
		return "setweight( to_tsvector( '%s', coalesce(\"%s\",'') ), '%s' )" % (self.config, f.column, weight)
	
	def update_index( self, pk=None ):
		"""
		Updates the full-text index for one, many, or all instances of this manager's model.
		"""
		from django.db import connection
		# Build a list of SQL clauses that generate tsvectors for each specified field.
		clauses = []
		if self.fields is None:
			self.fields = self._find_text_fields()
		if isinstance( self.fields, (list,tuple) ):
			for field in self.fields:
				clauses.append( self._vector_sql(field) )
		else:
			for field, weight in self.fields.items():
				clauses.append( self._vector_sql(field,weight) )
		vector_sql = ' || '.join( clauses )
		where = ''
		# If one or more pks are specified, tack a WHERE clause onto the SQL.
		if pk is not None:
			if isinstance( pk, (list,tuple) ):
				ids = ','.join( [str(v) for v in pk] )
				where = " WHERE \"%s\" IN (%s)" % (self.model._meta.pk.column, ids)
			else:
				where = " WHERE \"%s\" = %s" % (self.model._meta.pk.column, pk)
		sql = "UPDATE \"%s\" SET \"%s\" = %s%s;" % (self.model._meta.db_table, self.vector_field.column, vector_sql, where)
		cursor = connection.cursor()
		cursor.execute( sql )
		cursor.execute( "COMMIT;" )
		cursor.close()
	
	def search( self, query, rank_field=None, rank_normalization=32 ):
		"""
		Returns a queryset after having applied the full-text search query. If rank_field
		is specified, it is the name of the field that will be put on each returned instance.
		When specifying a rank_field, the results will automatically be ordered by -rank_field.
		
		For possible rank_normalization values, refer to:
		http://www.postgresql.org/docs/8.3/static/textsearch-controls.html#TEXTSEARCH-RANKING
		"""
		ts_query = "to_tsquery('%s','%s')" % (self.config, unicode(query).replace("'","''"))
		where = "\"%s\" @@ %s" % (self.vector_field.column, ts_query)
		select = {}
		order = []
		if rank_field is not None:
			select[rank_field] = 'ts_rank( "%s", %s, %d )' % (self.vector_field.column, ts_query, rank_normalization)
			order = ['-%s' % rank_field]
		return self.all().extra( select=select, where=[where], order_by=order )

