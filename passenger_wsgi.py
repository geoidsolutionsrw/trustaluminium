import sys, os
sys.path.insert(0, '/home4/cpozehmk/virtualenv/aluminium_app/3.8/lib/python3.8/site-packages')
sys.path.insert(0, '/home4/cpozehmk/aluminium_app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trust_aluminium.settings')
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
