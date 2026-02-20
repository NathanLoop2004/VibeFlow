"""Sync: copiar migraciones faltantes de public.django_migrations → app.django_migrations"""
import psycopg2, os, dotenv
dotenv.load_dotenv()
conn = psycopg2.connect(
    host=os.getenv('DB_HOST'),
    port=6543,
    dbname='postgres',
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
)
conn.autocommit = True
cur = conn.cursor()

missing = [
    ('accounts', '0004_modules_families_subfamilies'),
    ('accounts', '0005_recordings'),
    ('accounts', '0006_songs_fingerprints'),
    ('accounts', '0007_songs_terabox'),
    ('accounts', '0008_enable_rls_public'),
    ('accounts', '0009_drop_public_duplicates'),
]

for app, name in missing:
    cur.execute(
        "INSERT INTO app.django_migrations (app, name, applied) "
        "SELECT app, name, applied FROM public.django_migrations "
        "WHERE app = %s AND name = %s "
        "ON CONFLICT DO NOTHING",
        (app, name)
    )
    print(f"  ✓ {app}/{name}")

print("\nDone. Verificando...")
cur.execute("SELECT count(*) FROM app.django_migrations")
print(f"Total registros en app.django_migrations: {cur.fetchone()[0]}")
conn.close()
