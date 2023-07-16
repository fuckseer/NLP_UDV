import requests
from bs4 import BeautifulSoup
import pandas as pd


links = {
    'Федеральный закон':' https://apisearch.rg.ru/filter?query=%7B%22article%22:%7B%22priority%22:10,%22size%22:1,%22phrase%22:%22%22,%22source_type%22:%22document%22,%22fields%22:[%22id%22,%22url%22,%22images%22,%22title%22,%22link_title%22,%22announce%22,%22label%22,%22is_adv%22,%22tags%22,%22publish_at%22,%22source_type%22],%22sort%22:%22publish_at:desc%22,%22date%22:[631152000,1689089191],%22doctype_slug%22:[%22fedzakon%22]%7D%7D',
    'Конституция':'https://apisearch.rg.ru/filter?query=%7B%22article%22:%7B%22priority%22:10,%22size%22:1,%22phrase%22:%22%22,%22source_type%22:%22document%22,%22fields%22:[%22id%22,%22url%22,%22images%22,%22title%22,%22link_title%22,%22announce%22,%22label%22,%22is_adv%22,%22tags%22,%22publish_at%22,%22source_type%22],%22sort%22:%22publish_at:desc%22,%22date%22:[631152000,1689090895],%22doctype_slug%22:[%22main%22]%7D%7D',
    'Постановление': 'https://apisearch.rg.ru/filter?query=%7B%22article%22:%7B%22priority%22:10,%22size%22:1,%22phrase%22:%22%22,%22source_type%22:%22document%22,%22fields%22:[%22id%22,%22url%22,%22images%22,%22title%22,%22link_title%22,%22announce%22,%22label%22,%22is_adv%22,%22tags%22,%22publish_at%22,%22source_type%22],%22sort%22:%22publish_at:desc%22,%22date%22:[631152000,1689091592],%22doctype_slug%22:[%22postanov%22]%7D%7D',
    'Указ': 'https://apisearch.rg.ru/filter?query=%7B%22article%22:%7B%22priority%22:10,%22size%22:1,%22phrase%22:%22%22,%22source_type%22:%22document%22,%22fields%22:[%22id%22,%22url%22,%22images%22,%22title%22,%22link_title%22,%22announce%22,%22label%22,%22is_adv%22,%22tags%22,%22publish_at%22,%22source_type%22],%22sort%22:%22publish_at:desc%22,%22date%22:[631152000,1689093793],%22doctype_slug%22:[%22ukaz%22]%7D%7D',
    'Приказ': 'https://apisearch.rg.ru/filter?query=%7B%22article%22:%7B%22priority%22:10,%22size%22:1,%22phrase%22:%22%22,%22source_type%22:%22document%22,%22fields%22:[%22id%22,%22url%22,%22images%22,%22title%22,%22link_title%22,%22announce%22,%22label%22,%22is_adv%22,%22tags%22,%22publish_at%22,%22source_type%22],%22sort%22:%22publish_at:desc%22,%22date%22:[631152000,1689093856],%22doctype_slug%22:[%22prikaz%22]%7D%7D',
    'Cообщение':'https://apisearch.rg.ru/filter?query=%7B%22article%22:%7B%22priority%22:10,%22size%22:1,%22phrase%22:%22%22,%22source_type%22:%22document%22,%22fields%22:[%22id%22,%22url%22,%22images%22,%22title%22,%22link_title%22,%22announce%22,%22label%22,%22is_adv%22,%22tags%22,%22publish_at%22,%22source_type%22],%22sort%22:%22publish_at:desc%22,%22date%22:[631152000,1689094036],%22doctype_slug%22:[%22soobshenie%22]%7D%7D',
    'Распоряжение': 'https://apisearch.rg.ru/filter?query=%7B%22article%22:%7B%22priority%22:10,%22size%22:1,%22phrase%22:%22%22,%22source_type%22:%22document%22,%22fields%22:[%22id%22,%22url%22,%22images%22,%22title%22,%22link_title%22,%22announce%22,%22label%22,%22is_adv%22,%22tags%22,%22publish_at%22,%22source_type%22],%22sort%22:%22publish_at:desc%22,%22date%22:[631152000,1689094128],%22doctype_slug%22:[%22raspr%22]%7D%7D',
    'Законопроект': 'https://apisearch.rg.ru/filter?query=%7B%22article%22:%7B%22priority%22:10,%22size%22:1,%22phrase%22:%22%22,%22source_type%22:%22document%22,%22fields%22:[%22id%22,%22url%22,%22images%22,%22title%22,%22link_title%22,%22announce%22,%22label%22,%22is_adv%22,%22tags%22,%22publish_at%22,%22source_type%22],%22sort%22:%22publish_at:desc%22,%22date%22:[631152000,1689094196],%22doctype_slug%22:[%22zakonoproekt%22]%7D%7D'
}


def get_laws(link, type):
    response = requests.get(link)
    print('Количество символов',len(response.text))
    data_json = response.json()
    hits = data_json.get('hits', {}).get('hits', [])
    results = []
    for hit in hits:
        source = hit.get("_source", {})
        doc_id = source.get("id", "")
        title = source.get("title", "")
        publish_at = source.get("publish_at", "")
        url = source.get("url", "")
        results.append((doc_id, title, publish_at, url, type))
    return results

def get_law_text(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    law_text_elements = soup.find('div', class_='PageDocumentContent_text__6yNRz')
    if law_text_elements is None:
        return ''
    law_text = law_text_elements.get_text(separator=' ')
    law_text = law_text.replace('\n', ' ').replace('\r', '')
    return law_text.strip()

def get_news(df):
    url = 'https://apisearch.rg.ru/filter?query=%7B%22article%22:%7B%22priority%22:10,%22size%22:100,%22phrase%22:%22%22,%22source_type%22:%22document%22,%22fields%22:[%22id%22,%22url%22,%22images%22,%22title%22,%22link_title%22,%22announce%22,%22label%22,%22is_adv%22,%22tags%22,%22publish_at%22,%22source_type%22],%22sort%22:%22publish_at:desc%22,%22date%22:[631152000,1689272139]%7D%7D'
    type = ''
    news = get_laws(url,type)
    news_df = pd.DataFrame(news, columns=['ID', 'Название закона', 'Дата', 'Ссылка', 'Вид закона'])
    old_rows = []
    for index, row in news_df.iterrows():
        law_name = row['Название закона']

        if not df['Название закона'].str.contains(law_name).any():
            news_df = news_df['Ссылка'].apply(lambda x: "https://rg.ru/documents" + x)
            news_df['Текст'] = news_df['Ссылка'].apply(get_law_text)

        else:
            old_rows.append(index)

    news_df = news_df.drop(old_rows)
    return pd.concat([df, news_df], ignore_index=True)
