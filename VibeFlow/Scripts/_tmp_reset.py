import os, sys, django, bcrypt
sys.path.insert(0, r'C:\Users\Usuario\Desktop\VibeFlow')
os.environ['DJANGO_SETTINGS_MODULE'] = 'VibeFlow.settings'
django.setup()
from django.db import connection

password = 'Borjaelias2004'
new_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

with connection.cursor() as c:
    c.execute("UPDATE app.users SET password_hash = %s, updated_at = NOW() WHERE email = %s", [new_hash, 'jinderloop@gmail.com'])
    print('Filas actualizadas:', c.rowcount)

# Verificar que se guardó correctamente
with connection.cursor() as c:
    c.execute("SELECT password_hash FROM app.users WHERE email = %s", ['jinderloop@gmail.com'])
    row = c.fetchone()
    stored_hash = row[0]
    print('Hash guardado:', stored_hash)
    print('Verificacion:', bcrypt.checkpw(password.encode(), stored_hash.encode()))
