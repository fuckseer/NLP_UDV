from AddData import prepare_df
import pandas as pd
from flask import Flask, render_template, request
from flask_paginate import Pagination, get_page_parameter
from GetData import get_laws_from_database

app = Flask(__name__, template_folder='templates')

@app.route('/')
def index():
     page = request.args.get(get_page_parameter(), type=int, default=1)
     per_page = 10
     offset = (page - 1) * per_page
     laws_data = get_laws_from_database(offset, per_page)
     total = 40000
     pagination = Pagination(page=page, total=total,per_page=per_page, css_framework='bootstrap4')
     return render_template('index.html', laws_data=laws_data, pagination=pagination)

@app.route('/laws')
def show_df():


if __name__ == '__main__':
     app.run(debug=True)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
