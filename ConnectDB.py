import psycopg2


def connect_postgresql(host, port,
                       dbname, user,
                       password):
    try:
        conn = psycopg2.connect(host=host,
                                port=port,
                                dbname=dbname,
                                user=user,
                                sslmode='prefer',
                                connect_timeout=10,
                                password=password)
    except:
        print('Can`t establish connection to database')

    return conn
