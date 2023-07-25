import re
from datetime import datetime
import time


import requests
from bs4 import BeautifulSoup
import pandas as pd
from ConnectDB import connect_postgresql
import locale
from NLP import get_date, get_text, extract_law_names, find_law_link, get_link, get_keyword_vector

links = {
    'О персональных данных': 'http://pravo.gov.ru/proxy/ips/?doc_itself=&nd=102108261&page=1&rdk=31',
    'О безопасности критической информационной инфраструктуры Российской Федерации': 'http://pravo.gov.ru/proxy/ips/?doc_itself=&nd=102439340&page=1&rdk=0',
    'О связи': 'http://pravo.gov.ru/proxy/ips/?doc_itself=&nd=102082548&page=1&rdk=92',
    'Об инностранных инвестициях' : 'http://pravo.gov.ru/proxy/ips/?doc_itself=&nd=102060945&page=1&rdk=21',
    'Об информации, информационных технологиях и о защите информации':'http://pravo.gov.ru/proxy/ips/?doc_itself=&nd=102108264&page=1&rdk=69'
    }


def get_laws_from_database(offset, per_page):
    conn = connect_postgresql()
    cursor = conn.cursor()

    sql_query = f'SELECT "ID", "Статус", ' \
                '"Название закона", "Ссылка", "Вид закона", "Текст", ' \
                '"Токены", "Обработанный текст", "Номер темы", ' \
                '"Утратившие силу", "Упоминаемые законы" ' \
                f"FROM data LIMIT {per_page} OFFSET {offset};"

    cursor.execute(sql_query)

    laws_data = cursor.fetchall()

    cursor.close()
    conn.close()

    return laws_data


def get_laws(url):
    response = requests.get(url, timeout=20)

    if response.status_code == 200:

        soup = BeautifulSoup(response.content, 'html.parser')
        doc_id = url.split('nd=')[1].split('&')[0]
        doc_title = soup.find('title').getText()
        if 'Текст документа отсутствует' not in soup.text:
            #date_element = soup.find_all('p', class_='I')[-1]
            #date = get_date(date_element.text)
            paragraphs = soup.find_all('p')
            text = get_text(paragraphs)
            doc_links = soup.find_all('a', class_='doclink')
            referenced_laws = [{'Текст': link.getText(), 'Ссылка': link['href']} for link in doc_links]
            for entry in referenced_laws:
                entry['Текст'] = entry['Текст'].replace('\xa0', ' ')
            laws = extract_law_names(text)
            for law in laws:
                law['ID'] = find_law_link(law['prefix_match'].strip(), referenced_laws)
        else:
            date = None
            text = None
            laws = None
        straight_connection = get_connections(doc_id, 'Прямые связи')
        back_connection = get_connections(doc_id, 'Обратные связи')

        status, date, key_words, categories_dict = get_law_info(doc_id)

        data = {
            'ID': [doc_id],
            'Cтатус': [status],
            'Название закона': [doc_title],
            'Дата': [date],
            'Ссылка': [url],
            'Ключевые слова': [key_words],
            'Области законодательства': [categories_dict],
            'Текст': [text],
            'Упоминаемые законы': [laws],
            'Прямые связи': [straight_connection],
            'Обратные связи': [back_connection]
        }

        return pd.DataFrame(data)
    else:
        return f'Ошибка запроса: {response.status_code}'


def get_law_info(ID):
    url = get_link(ID, 'Информация о законе')
    responce = requests.get(url, timeout=20)
    soup = BeautifulSoup(responce.content, 'html.parser')
    status = soup.find('div', class_='DC_status').text
    date = get_date(soup.text)
    key_words = soup.find('div', id='klsl', class_='wrapper')
    if key_words:
        key_words = key_words.text
        table_rows = soup.find_all('tr')
        categories_dict = {}
        for row in table_rows:
            cells = row.find_all('td')
            if len(cells) == 2:
                code = cells[0].text.strip()
                name = cells[1].text.strip()
                categories_dict[code] = name
    else:
        key_words = None
        categories_dict = None
    return status, date, key_words, categories_dict


def get_connections(ID, type):
    url = get_link(ID, type)
    max_retries = 10
    retry_delay = 10
    for attempt in range(max_retries):
        try:
            responce = requests.get(url, timeout=60)
            if responce.status_code == 200:
                soup = BeautifulSoup(responce.content, 'html.parser')
                result = []

                for reference_elem in soup.find_all('reference'):
                    reference_dict = {}

                    refkind = reference_elem.find('refkind').text
                    oid = reference_elem.find('docname').get('oid')
                    rdk = reference_elem.find('docname').get('rdk')
                    docname_text = reference_elem.find('docname').text.strip()
                    docannot = reference_elem.find('docannot').text

                    docname_parts = docname_text.split(' от ')
                    doc_type = docname_parts[0]
                    doc_date = docname_parts[1].split(' № ')[0]

                    reference_dict['Вид'] = refkind
                    reference_dict['ID'] = oid
                    reference_dict['Тип'] = doc_type
                    reference_dict['Дата'] = doc_date
                    reference_dict['Название закона'] = docannot

                    result.append(reference_dict)
                return result
            else:
                print(responce.status_code)

        except requests.exceptions.RequestException as e:
            print(e)

        time.sleep(retry_delay)
    print(f'Не удалось получить ответ от {url} после {max_retries} попыток')

# for law in laws:
#    key_words = law['key_words'].split()
#    law['keyword_vectors'] = [get_keyword_vector(keyword) for keyword in key_words]