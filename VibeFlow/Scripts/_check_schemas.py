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
cur.execute("""
SELECT schemaname, tablename, indexname FROM pg_indexes
WHERE schemaname IN ('app','public')
ORDER BY schemaname, tablename, indexname
""")
for r in cur.fetchall():
    print(f'{r[0]:8} {r[1]:40} {r[2]}')
conn.close()
