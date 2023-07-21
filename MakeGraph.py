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

color_map = {}
for i in range(-1, 116):
    color = "#{:06x}".format(random.randint(0, 0xFFFFFF))
    color_map[i] = color


def visualize_graph():
    graph.show_buttons(filter_=['nodes'])
    graph.show('graph.html')


def add_node(row, graph, color_map,html_template):
    cluster = row['Статус']
    name = row['Название закона']
    date = row['Дата']
    link = row['Ссылка']
    color = color_map.get(cluster, 'gray')
    node_id = row.name
    graph.add_node(node_id, label='', title=html_template.format(name=name, date=date, link=link), color=color)


def add_edges(row, graph):
    direct_connection = row['Прямые связи']
    for connection in direct_connection:
        target_node_id = connection['ID']
        graph.add_edge(row.name, target_node_id)

    reverse_connection = row['Обратные связи']
    for connection in reverse_connection:
        target_node_id = connection['ID']
        graph.add_edge(target_node_id, row.name)

    referenced_laws = row['Упоминаемые законы']
    for connection in referenced_laws:
        target_node_id = connection['ID']
        graph.add_edge(row.name, target_node_id)



