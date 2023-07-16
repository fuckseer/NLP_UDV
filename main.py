from AddData import prepare_df
import pandas as pd
from flask import Flask, render_template

app = Flask(__name__, template_folder='templates')

@app.route('/')
def index():
     return render_template('index.html')
# Press the green button in the gutter to run the script.
if __name__ == '__main__':
     app.run(debug=True)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
