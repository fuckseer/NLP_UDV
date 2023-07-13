from GetData import links, get_laws, get_law_text
import pandas as pd
from sqlalchemy import create_engine
from ConnectDB import connect_postgresql
from main import df
import NLP


def prepare_df(df):
    all_results = []

    for key, link in links.items():
        results = get_laws(link, key)
        all_results.append(results)

    for result_group in all_results:
        temp_df = pd.DataFrame(result_group, columns=['ID', 'Название закона', 'Дата', 'Ссылка', 'Вид закона'])
        df = pd.concat([df, temp_df], ignore_index=True)

    df['Ссылка'] = df['Ссылка'].apply(lambda x: "https://rg.ru/documents" + x)
    df['Текст'] = df['Ссылка'].apply(get_law_text)

    return NLP.analyze_data(df)


def add_data(data):
    conn = connect_postgresql('localhost', 5432, 'postgres', 'postgres', 'ksusha170402')
    engine = create_engine('postgresql+psycopg2://postgres:ksusha170402@localhost/postgres')

    data.to_sql('data', engine, if_exists='replace', index=False)
    conn.close()

print(prepare_df(df))