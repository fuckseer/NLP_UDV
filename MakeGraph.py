import random
from pyvis.network import Network

graph = Network(directed=True)

html_template = """
<div style="background-color: #f9f9f9; padding: 10px;">
  <h3>{name}</h3>
  <p>Date: {date}</p>
  <p>Link: <a href="{link}" target="_blank">{link}</a></p>
</div>
"""

color_map = {
    'Действует': 'green',
    'Действует с изменениями': 'yellow',
    'Утратил силу': 'brown'
}

#def get_color(color_map):
#    for i in range(-1, 116):
#        color = "#{:06x}".format(random.randint(0, 0xFFFFFF))
#        color_map[i] = color
#    return color_map


def visualize_graph():
    graph.show_buttons(filter_=['nodes'])
    graph.show('graph.html')


def add_node(row, graph, color_map, html_template):
    cluster = row['Cтатус']
    name = row['Название закона']
    date = row['Дата']
    link = row['Ссылка']

    color = color_map.get(cluster, 'gray')
    node_id = row['ID']
    graph.add_node(node_id, label='', title=html_template.format(name=name, date=date, link=link),
                   color=color, physics=False)


def add_edges(row, graph):
    direct_connection = row['Прямые связи']
    for connection in direct_connection:
        target_node_id = connection['ID']
        if target_node_id in graph.get_nodes():
            graph.add_edge(row['ID'], target_node_id, color='red', physics=False)

    reverse_connection = row['Обратные связи']
    if reverse_connection is not None:
        for connection in reverse_connection:
            target_node_id = connection['ID']
            if target_node_id in graph.get_nodes():
                graph.add_edge(target_node_id, row['ID'], color='blue', physics=False)

    referenced_laws = row['Упоминаемые законы']
    if referenced_laws is not None:
        for connection in referenced_laws:
            target_node_id = connection['ID']
            if target_node_id in graph.get_nodes():
                graph.add_edge(row['ID'], target_node_id, color='purple', physics=False)



