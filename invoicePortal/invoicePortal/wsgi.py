"""
WSGI config for invoicePortal project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

import os
import sys

sys.path.append('D:\\Spring 2024\\Capstone\\InvoiceProcessing')

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'invoicePortal.settings')

application = get_wsgi_application()
