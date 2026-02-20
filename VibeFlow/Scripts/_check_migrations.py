import psycopg2, os, dotenv
dotenv.load_dotenv()
conn = psycopg2.connect(
    host=os.getenv('DB_HOST'),
    port=6543,
    dbname='postgres',
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
)
cur = conn.cursor()

print("=== public.django_migrations ===")
cur.execute("SELECT id, app, name FROM public.django_migrations ORDER BY id")
pub = cur.fetchall()
for r in pub:
    print(f"  {r[0]:4}  {r[1]:20} {r[2]}")

print(f"\nTotal public: {len(pub)}")

print("\n=== app.django_migrations ===")
cur.execute("SELECT id, app, name FROM app.django_migrations ORDER BY id")
app_rows = cur.fetchall()
for r in app_rows:
    print(f"  {r[0]:4}  {r[1]:20} {r[2]}")

print(f"\nTotal app: {len(app_rows)}")

# Check diff
pub_set = {(r[1], r[2]) for r in pub}
app_set = {(r[1], r[2]) for r in app_rows}
missing_in_app = pub_set - app_set
missing_in_pub = app_set - pub_set

if missing_in_app:
    print(f"\n>>> En public pero NO en app ({len(missing_in_app)}):")
    for m in sorted(missing_in_app):
        print(f"  {m[0]:20} {m[1]}")

if missing_in_pub:
    print(f"\n>>> En app pero NO en public ({len(missing_in_pub)}):")
    for m in sorted(missing_in_pub):
        print(f"  {m[0]:20} {m[1]}")

conn.close()
