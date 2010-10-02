DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'OPTIONS': {
            'autocommit': False,
         },
        'NAME': 'gpb_mdq',                      # Or path to database file if using sqlite3.
        'USER': 'gpb',                      # Not used with sqlite3.
        'PASSWORD': 'gpbgpb',                  # Not used with sqlite3.
        'HOST': 'localhost',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '5432',                      # Set to empty string for default. Not used with sqlite3.
    }
}
