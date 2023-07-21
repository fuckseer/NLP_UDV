import locale

import numpy as np
import pandas as pd
from gensim import corpora, models
from gensim.corpora import Dictionary
from gensim.models import LdaModel, Word2Vec
from gensim.topic_coherence.indirect_confirmation_measure import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import re
import nltk

nltk.download('wordnet')
nltk.download('punkt')
from nltk.tokenize import word_tokenize

from sklearn.metrics.pairwise import  pairwise_distances
def make_word2vec(keywords):
    keywords_tokens = word_tokenize(keywords)
    model = Word2Vec(keywords_tokens, vector_size=100, window=5, min_count=1, workers=-1)

def get_keyword_vector(keyword, model):
    if keyword in model.wv.key_to_index:
        return model.wv[keyword]
    else:
        return None
def get_similarity(vector1, vector2):
    if vector1 is None or vector2 is None:
        return None
    return cosine_similarity(vector1.reshape(1, -1), vector2.reshape(1, -1))[0, 0]


def get_clastering_LDA(tokens):
    mydict = Dictionary(tokens)
    corpus = [mydict.doc2bow(text) for text in tokens]
    lda_model = LdaModel(corpus=corpus, id2word=mydict, num_topics=12)

    topic_list = []
    doc_topics = lda_model[corpus]

    for doc in doc_topics:
        topic = max(doc, key=lambda x: x[1])[0]
        topic_list.append(topic)

    return topic_list


def extract_law_names(text):
    prefix_pattern = r'\b от \d+ \w+ \d+ года № \d+-ФЗ\b'
    law_names = []

    # Находим все совпадения с префиксом
    prefix_matches = re.finditer(prefix_pattern, text)

    for match in prefix_matches:
        # Извлекаем позицию совпадения
        start_position = match.start()
        end_position = match.end()

        # Ищем закон, следующий за датой, игнорируя многочисленные пробелы и теги
        law_name_match = re.search(r'"(.*?)"', text[end_position:])
        if law_name_match:
            law_name = law_name_match.group(1)
            law_names.append({'law_name': law_name, 'prefix_match': match.group(), 'ID': None})

    return law_names

def find_law_link(prefix_match, referenced_laws):
    for text in referenced_laws:
        if text['Текст'].startswith(prefix_match):
            url_parts = text['Ссылка'].split('&')
            nd_value = next((part.split('=')[1] for part in url_parts if part.startswith('nd=')), None)
            return nd_value if nd_value else ''

def get_link(ID, type):
    links = {
        'Текст закона':f'http://pravo.gov.ru/proxy/ips/?doc_itself=&nd={ID}&page=1&rdk=31',
        'Информация о законе': f'http://pravo.gov.ru/proxy/ips/?doc_itself=&vkart=card&nd={ID}&page=1&rdk=31',
        'Прямые связи': f'http://pravo.gov.ru/proxy/ips/?docrefs.xml=&oid={ID}&refs=1',
        'Обратные связи': f'http://pravo.gov.ru/proxy/ips/?docrefs.xml&add=1&startnum=1&endnum=2000&oid={ID}&refs=0'
    }
    return links[type]

def find_duplicate_quotes_tfidf(df):
    vectorized = TfidfVectorizer()
    tfidf_matrix = vectorized.fit_transform(df['Текст'])
    similarity_matrix = 1 - pairwise_distances(tfidf_matrix, metric='cosine')
    duplicates = []
    n_docs = len(df)
    for i in range(n_docs):
        duplicate_indices = [j for j in range(n_docs) if similarity_matrix[i, j] > 0.99 and i != j]

        if duplicate_indices:
            duplicate = {
                'Law Index': i,
                'Duplicate Indices': duplicate_indices,
                'Duplicate Text': df.iloc[i]['Текст']
            }
            duplicates.append(duplicate)

    duplicates_df = pd.DataFrame(duplicates)
    return duplicates_df


def get_date(text):
    pattern = r'\d{2}\.\d{2}\.\d{4}'
    date = re.search(pattern, text)
    date = date.group() if date else None
    locale.setlocale(locale.LC_TIME, 'ru_RU')
    return pd.to_datetime(date, dayfirst=True)


def get_text(text):
    text = ' '.join(paragraph.get_text() for paragraph in text)
    text = ' '.join(text.split())
    text = text.replace('\n', ' ')
    return text.replace('\n\n', '\n')


    #df['Номер темы'] = get_clastering_LDA(name)
    #df['Кем принят'] = df['Текст'].apply(extract_organization)
    #df['Утратившие силу'] = df['Текст'].str.extract(r'утратившим силу (.+?) \(', expand=False)
