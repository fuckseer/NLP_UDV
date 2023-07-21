from datetime import datetime

from GetData import links, get_laws
import pandas as pd
from sqlalchemy import create_engine
from ConnectDB import connect_postgresql
import NLP
from MakeGraph import graph, visualize_graph, add_node, add_edges, color_map, html_template, status_map

def prepare_df(link):
    df = get_laws(link)
    pd.set_option('display.max_columns', None)
    print(df)
    for _, row in df.iterrows():
        print(row)
        add_node(row, graph, color_map, html_template)
    result_df = pd.DataFrame()
    for col in ['Прямые связи', 'Обратные связи', 'Упоминаемые законы']:
        for laws in df[col]:
            for law in laws:
                print(law['ID'], col)
                url = NLP.get_link(law['ID'], 'Текст закона')
                temp_df = get_laws(url)
                for _, entry in temp_df.iterrows():
                    add_node(entry, graph, color_map, html_template)
                print(temp_df)
                result_df = pd.concat([result_df, temp_df])

    final_df = pd.concat([df, result_df], ignore_index=True)
    for _, row in final_df.iterrows():
        add_edges(row, graph)
    print(final_df)
    visualize_graph()
    return final_df


def add_data(data):
    conn = connect_postgresql()
    engine = create_engine('postgresql+psycopg2://postgres:ksusha170402@localhost/postgres')

    data.to_sql('data', engine, if_exists='replace', index=False)
    conn.close()


add_data(prepare_df(links['О персональных данных']))