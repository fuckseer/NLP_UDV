import locale

import pandas as pd
from gensim import corpora, models
from gensim.corpora import Dictionary
from gensim.models import LdaModel
from gensim.topic_coherence.indirect_confirmation_measure import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import re
import nltk

nltk.download('wordnet')
nltk.download('punkt')
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from pymorphy3 import MorphAnalyzer

from sklearn.metrics.pairwise import  pairwise_distances

import spacy
import ru_core_news_sm

from MakeGraph import visualize_graph


def process_text(text):
    stop_words = set(stopwords.words('russian'))
    morph = MorphAnalyzer()

    # Токенизация текста
    tokens = word_tokenize(text)
    # Оставляем только буквенные токены
    tokens = [word for word in tokens if word.isalpha()]
    # Приводим все токены к нижнему регистру
    tokens = [word.lower() for word in tokens]
    # Удаляем стоп-слова
    tokens = [word for word in tokens if not word in stop_words]
    # Лемматизация токенов
    tokens = [morph.normal_forms(word)[0] for word in tokens]

    return tokens


def join_list(tab):
    return " ".join((''.join(l) for l in tab))


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


#def extract_organization(text):
#    nlp = ru_core_news_sm.load()
#    doc = nlp(text)
#    organizations = [ent.text for ent in doc.ents if ent.label_ == 'ORG']
#    return organizations[0] if organizations else None


r'"(.*?)"'
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
            law_names.append({'law_name': law_name, 'prefix_match': match.group(), 'url': None})

    return law_names

def find_law_link(prefix_match, referenced_laws):

    law_name = re.search(r'"(.*?)"', prefix_match).group(1)
    link_pattern = re.compile(r'\((.*?)\)')
    links = link_pattern.findall(referenced_laws)
    for link in links:
        if law_name in link:
            return link
    return None

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


def create_references_df(df):
    references_df = pd.DataFrame(columns=['Found_Law_Index', 'Name_Index'])
    for i, law_names in enumerate(df['Упоминаемые законы']):
        if law_names:
            law_names = [name.strip() for name in law_names.split(',')]
            for law_name in law_names:
                pattern = re.escape(law_name)
                regex = re.compile(pattern, re.IGNORECASE)
                for j, name in enumerate(df['Название закона']):
                    if i != j:
                        match = regex.search(name)
                        if match:
                            references_df.at[i, 'Found_Law_Index'] = i
                            references_df.at[i, 'Name_Index'] = j
                            break
    return references_df

def get_date(text):
    pattern = r"(\d{2}\s\w+\s\d{4})"
    date = re.search(pattern, text)
    date = date.group(1) if date else None
    locale.setlocale(locale.LC_TIME, 'ru_RU')
    return pd.to_datetime(date, format='%d %B %Y', errors='coerce')


def get_text(text):
    text = ' '.join(paragraph.get_text() for paragraph in text)
    text = ' '.join(text.split())
    text = text.replace('\n', ' ')
    return text.replace('\n\n', '\n')

def analyze_data(df):
    tokens = df['Текст']
    tokens = tokens.apply(lambda token: process_text(token))
    tokens = [[token for token in sublist if token not in ['ст', 'n']] for sublist in tokens]
    tokens = pd.Series(tokens)
    df['Токены'] = tokens
    df["Обработанный текст"] = tokens.apply(join_list)
    name = df['Название закона'].apply(lambda text: process_text(text))
    name = pd.Series(name)

    df['Номер темы'] = get_clastering_LDA(name)
    #df['Кем принят'] = df['Текст'].apply(extract_organization)
    df['Утратившие силу'] = df['Текст'].str.extract(r'утратившим силу (.+?) \(', expand=False)
    df['Упоминаемые законы'] = extract_law_names(df)

    duplicates_df = find_duplicate_quotes_tfidf(df)
    references_df = create_references_df(df)
    print(df)
    print(duplicates_df)
    print(references_df)
    visualize_graph(df, duplicates_df,references_df)
    return df




