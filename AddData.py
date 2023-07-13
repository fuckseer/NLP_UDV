from GetData import links, get_laws, get_law_text
import pandas as pd

all_results = []
df = pd.DataFrame()

for key, link in links.items():
    results = get_laws(link, key)
    all_results.append(results)

columns = ['ID', 'Название закона', 'Дата', 'Ссылка', 'Вид закона']
df = pd.DataFrame(columns=columns)

for result_group in all_results:
    temp_df = pd.DataFrame(result_group, columns=columns)
    df = pd.concat([df, temp_df], ignore_index=True)

df['Ссылка'] = df['Ссылка'].apply(lambda x: "https://rg.ru/documents" + x)
df['Текст'] = df['Ссылка'].apply(get_law_text)
