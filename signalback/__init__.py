try:
    from .local_settings import *
except ImportError, e:
    print "Unable to find local_settings.py file."