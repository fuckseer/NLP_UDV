from flask import Flask, render_template, request
from flask_paginate import Pagination, get_page_parameter
from GetData import get_laws_from_database
from NLP import extract_json
import MakeGraph



app = Flask(__name__, template_folder='templates')


max_text_length = 100


@app.route('/')
def index():
    page = request.args.get(get_page_parameter(), type=int, default=1)
    per_page = 10
    offset = 0 if page == 1 else (page-1) * per_page
    laws_data_dict = get_laws_from_database(offset, per_page)
    print(type(laws_data_dict))
    print(laws_data_dict)
    laws_data_dict['Текст'] = laws_data_dict['Текст'].apply(
        lambda x: x if (isinstance(x, str) and len(x) <= max_text_length)
        else (x[:max_text_length] + '...' if isinstance(x, str) else x)
    )
    for row in laws_data_dict.iterrows():
        print(row[1]['Упоминаемые законы'])
    total = 500
    pagination = Pagination(page=page, total=total, per_page=per_page)

    return render_template('index.html', table_html=laws_data_dict, bs_version=4, pagination=pagination,
                           max_text_length=max_text_length)

@app.route('/graph')
def make_graph():
    laws_data_dict = get_laws_from_database(0, per_page=100)
    for _, row in laws_data_dict.iterrows():
        MakeGraph.add_node(row, MakeGraph.graph, MakeGraph.color_map, MakeGraph.html_template)
        MakeGraph.add_edges(row, MakeGraph.graph)
    MakeGraph.visualize_graph()
if __name__ == '__main__':
    app.run(debug=True)
