from datetime import datetime

from GetData import links, get_laws
import pandas as pd
from sqlalchemy import create_engine
from ConnectDB import connect_postgresql
import NLP


def prepare_df():
    df = get_laws(links['О персональных данных'])
    pd.set_option('display.max_columns', None)
    print(df)
    #return NLP.analyze_data(df)


def add_data(data):
    conn = connect_postgresql()
    engine = create_engine('postgresql+psycopg2://postgres:ksusha170402@localhost/postgres')

    data.to_sql('data', engine, if_exists='replace', index=False)
    conn.close()

prepare_df()