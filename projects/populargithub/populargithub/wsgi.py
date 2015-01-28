"""
WSGI config for populargithub project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/howto/deployment/wsgi/
"""

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "populargithub.settings")

from django.core.wsgi import get_wsgi_application
from whitenoise.django import DjangoWhiteNoise
application = get_wsgi_application()
application = DjangoWhiteNoise(application)

# TODO: Use tornado web server
# How to set up django to run on the tornado web server:
# https://github.com/bdarnell/django-tornado-demo/tree/master/testsite
# since we're using angular there is very little reason to use the django templating system.
# beyond that this will allow us to put in an asynchronous status bar showing the queue processing.