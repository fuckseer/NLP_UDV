import random
from pyvis.network import Network


def visualize_graph(df, duplicates_df, references_df):
    # Создаем экземпляр класса Network
    graph = Network(directed=True)

    # Создаем HTML-шаблон для отображения подробной информации о законе
    html_template = """
    <div style="background-color: #f9f9f9; padding: 10px;">
      <h3>{name}</h3>
      <p>Date: {date}</p>
      <p>Link: <a href="{link}" target="_blank">{link}</a></p>
    </div>
    """

    color_map = {}
    for i in range(-1, 116):
        color = "#{:06x}".format(random.randint(0, 0xFFFFFF))
        color_map[i] = color

    for i, row in df.iterrows():
        cluster = row['Номер темы']
        name = row['Название закона']
        date = row['Дата']
        link = row['Ссылка']
        color = color_map.get(cluster, 'gray')
        graph.add_node(i, label='', title=html_template.format(name=name, date=date, link=link), color=color)

    # Добавляем связи на основе duplicates_df только если он не пустой
    if not duplicates_df.empty:
        for i, row in duplicates_df.iterrows():
            law_index = row['Law Index']
            duplicate_indices = row['Duplicate Indices']
            for duplicate_index in duplicate_indices:
                graph.add_edge(law_index, duplicate_index, color='purple')

    # Добавляем связи на основе references_df только если он не пустой
    if not references_df.empty:
        for i, row in references_df.iterrows():
            found_law_index = row['Found_Law_Index']
            name_index = row['Name_Index']
            graph.add_edge(found_law_index, name_index, color='blue')

    # Отображаем граф
    graph.show_buttons(filter_=['nodes'])
    graph.show('graph.html')
