from flask import Flask, render_template, request
from flask_paginate import Pagination, get_page_parameter
from GetData import get_laws_from_database
from NLP import extract_json



app = Flask(__name__, template_folder='templates')


@app.route('/')
def index():
    page = request.args.get(get_page_parameter(), type=int, default=1)
    per_page = 10
    offset = 0 if page == 1 else (page-1) * per_page
    laws_data_dict = get_laws_from_database(offset, per_page)
    print(type(laws_data_dict))
    print(laws_data_dict)
    table_html = laws_data_dict.to_html(classes='table table-bordered', index=False)
    total = len(laws_data_dict)
    pagination = Pagination(page=page, total=total, per_page=per_page)

    return render_template('index.html', table_html=table_html, bs_version=4, pagination=pagination)


if __name__ == '__main__':
    app.run(debug=True)
