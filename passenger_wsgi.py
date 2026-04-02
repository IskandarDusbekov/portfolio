import os
import sys
from pathlib import Path

from django.core.wsgi import get_wsgi_application


# Project root (folder containing this file)
PROJECT_ROOT = Path(__file__).resolve().parent

# Ensure project is importable when running under Passenger
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# WSGI callable for Passenger
application = get_wsgi_application()
