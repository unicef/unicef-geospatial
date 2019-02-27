import warnings

NAME = 'unicef-geospatial'
VERSION = __version__ = '0.2.0a0'
__author__ = ''

# UserWarning: The psycopg2 wheel package will be renamed from release 2.8;
warnings.simplefilter("ignore", UserWarning, 144)
