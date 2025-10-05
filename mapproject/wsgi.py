"""
WSGI config for mapproject project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

# Set Vercel environment
os.environ.setdefault('VERCEL', '1')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vercel_settings')

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()

# Auto-migrate for in-memory database
try:
    from django.core.management import execute_from_command_line
    execute_from_command_line(['manage.py', 'migrate', '--run-syncdb'])
except:
    pass  # Ignore errors during migration

# Vercel requires either 'app' or 'handler' variable
app = application
handler = application
