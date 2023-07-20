import re
from datetime import datetime

import requests
from bs4 import BeautifulSoup
import pandas as pd
from ConnectDB import connect_postgresql
import locale
from NLP import get_date, get_text, extract_law_names, find_law_link

links = {
    'О персональных данных': 'http://pravo.gov.ru/proxy/ips/?doc_itself=&nd=102108261&page=1&rdk=31'
    }


def get_laws(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    return soup

def get_laws_from_database(offset, per_page):
    conn = connect_postgresql()
    cursor = conn.cursor()

    sql_query = f'SELECT "ID", "Название закона", ' \
                '"Дата", "Ссылка", "Вид закона", "Текст", ' \
                '"Токены", "Обработанный текст", "Номер темы", ' \
                '"Утратившие силу", "Упоминаемые законы" ' \
                f"FROM data LIMIT {per_page} OFFSET {offset};"

    cursor.execute(sql_query)

    laws_data = cursor.fetchall()

    cursor.close()
    conn.close()

    return laws_data


def get_law_from_gov(url):
    response = requests.get(url)

    if response.status_code == 200:

        soup = BeautifulSoup(response.content, 'html.parser')
        doc_id = url.split('nd=')[1].split('&')[0]
        doc_title = soup.find('title').getText()
        date_element = soup.find_all('p', class_='I')[-2]
        date = get_date(date_element.text)
        paragraphs = soup.find_all('p')
        text = get_text(paragraphs)
        doc_links = soup.find_all('a', class_='doclink')
        referenced_laws = ['{} ({})'.format(link.getText(), link['href']) for link in doc_links]
        referenced_laws = ' '.join(referenced_laws)
        print(referenced_laws)
        #print(referenced_laws)
        #laws = extract_law_names(text)
        #for law in laws:
        #    law['url'] = find_law_link(law['prefix_match'], referenced_laws)
        #laws = find_next_law_link(laws,referenced_laws)
        #print(laws)

        data = {
            'ID': [doc_id],
            'Название закона': [doc_title],
            'Дата': [date],
            'Ссылка': [url],
            'Текст': [text],
            'Упоминаемые законы': [referenced_laws]
        }

        return pd.DataFrame(data)
    else:
        return f'Ошибка запроса: {response.status_code}'

def get_law_info(ID):
    url = f'http://pravo.gov.ru/proxy/ips/?doc_itself=&vkart=card&nd={ID}&page=1&rdk=31'
    responce = requests.get(url)
    soup = BeautifulSoup(responce.content, 'html.parser')
    status = soup.find('div', class_='DC_status').text
    key_words = soup.find('div', id='klsl', class_='wrapper').text
    table_rows = soup.find_all('tr')
    categories_dict = {}
    for row in table_rows:
        cells = row.find_all('td')
        if len(cells) == 2:
            code = cells[0].text.strip()
            name = cells[1].text.strip()
            categories_dict[code] = name

    return status, key_words, categories_dict

def get_referenced_laws(ID):
    url = f'http://pravo.gov.ru/proxy/ips/?docrefs.xml=&oid={ID}&refs=1'
    responce = requests.get(url)
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

get_referenced_laws(102108261)