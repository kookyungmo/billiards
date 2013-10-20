import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = 'billiards.settings'

path = os.path.dirname(os.path.abspath(__file__)) + '/billiards'
if path not in sys.path:
    sys.path.insert(1, path)

from django.core.handlers.wsgi import WSGIHandler
from bae.core.wsgi import WSGIApplication

application = WSGIApplication(WSGIHandler())