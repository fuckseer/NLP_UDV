import psycopg2


try:
    conn = psycopg2.connect(host='localhost',
                            port=5432,
                            dbname='postgres',
                            user='postgres',
                            sslmode='prefer',
                            connect_timeout=10,
                            password='ksusha170402')
except:
    print('Can`t establish connection to database')