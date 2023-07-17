from datetime import datetime

from GetData import links, get_laws, get_law_text
import pandas as pd
from sqlalchemy import create_engine
from ConnectDB import connect_postgresql
import NLP


def prepare_df():
    all_results = []
    df = pd.DataFrame(columns=['ID', 'Название закона', 'Дата', 'Ссылка', 'Вид закона'])

    for key, link in links.items():
        results = get_laws(link, key)
        all_results.append(results)

    for result_group in all_results:
        temp_df = pd.DataFrame(result_group, columns=['ID', 'Название закона', 'Дата', 'Ссылка', 'Вид закона'])
        df = pd.concat([df, temp_df], ignore_index=True)

    df['Ссылка'] = df['Ссылка'].apply(lambda x: "https://rg.ru/documents" + x)
    df['Текст'] = df['Ссылка'].apply(get_law_text)
    df['Дата'] = df['Дата'].apply(lambda x: datetime.fromtimestamp(x).strftime('%Y-%m-%d'))

    return NLP.analyze_data(df)


def add_data(data):
    conn = connect_postgresql()
    engine = create_engine('postgresql+psycopg2://postgres:ksusha170402@localhost/postgres')

    data.to_sql('data', engine, if_exists='replace', index=False)
    conn.close()
