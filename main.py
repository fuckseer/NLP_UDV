from flask import Flask, render_template, request
from flask_paginate import Pagination, get_page_parameter
from GetData import get_laws_from_database

app = Flask(__name__, template_folder='templates')


@app.route('/')
def index():
    page = request.args.get(get_page_parameter(), type=int, default=1)
    per_page = 10
    offset = 0 if page == 1 else (page-1) * per_page
    laws_data = get_laws_from_database(offset, per_page)
    columns = ['ID', 'Название закона', 'Дата',
               'Ссылка', 'Вид закона', 'Текст', 'Токены', 'Обработанный текст', 'Номер темы',
               'Утратившие силу', 'Упоминаемые законы']
    laws_data_dict = [dict(zip(columns, row)) for row in laws_data]
    total = 800
    pagination = Pagination(page=page, total=total, per_page=per_page)

    return render_template('index.html', laws_data=laws_data_dict, bs_version=4, pagination=pagination)


if __name__ == '__main__':
    app.run(debug=True)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
