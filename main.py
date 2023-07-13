from AddData import prepare_df
import pandas as pd

df = pd.DataFrame(columns=['ID', 'Название закона', 'Дата', 'Ссылка', 'Вид закона'])

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
     prepare_df(df)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
