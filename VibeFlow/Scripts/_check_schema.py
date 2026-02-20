import django, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'VibeFlow.settings'
django.setup()
from django.db import connection
c = connection.cursor()
c.execute("SELECT schemaname, tablename FROM pg_tables WHERE tablename IN ('songs','fingerprints')")
for r in c.fetchall():
    print(r)
c.close()
