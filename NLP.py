import pandas as pd
from gensim.topic_coherence.indirect_confirmation_measure import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import re
import nltk

nltk.download('wordnet')
nltk.download('punkt')
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from pymorphy3 import MorphAnalyzer

from sklearn.decomposition import TruncatedSVD
from sklearn.cluster import KMeans

import spacy
import ru_core_news_sm



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


def get_lsi_vectors(tokens):
    tfidf_vectorized = TfidfVectorizer(max_df=0.8, min_df=5)
    tfidf_matrix = tfidf_vectorized.fit_transform(tokens)
    lsi_model = TruncatedSVD(n_components=7)
    return lsi_model.fit_transform(tfidf_matrix)


def get_clastering_KMeans(vectors, n_clusters):
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    cluster_labels = kmeans.fit_predict(vectors)
    return cluster_labels


def extract_organization(text):
    nlp = ru_core_news_sm.load()
    doc = nlp(text)
    organizations = [ent.text for ent in doc.ents if ent.label_ == 'ORG']
    return organizations[0] if organizations else None


import re


def extract_law_names(df):
    pattern = r'N\s+\d+-ФЗ\s+"(.*?)"'
    pattern2 = r'пункт\s+\d+\s+статьи\s+\d+\s+части\s+\w+\s+(.*?)(?=\()'

    df['Упоминаемые законы'] = ''

    for i, text in enumerate(df['Текст']):
        matches = re.findall(pattern, text)
        filtered_matches = [match for match in matches if match not in df['Name'][i]]

        matches2 = re.findall(pattern2, text)
        filtered_matches.extend(matches2)

        if filtered_matches:
             df.at[i, 'Упоминаемые законы'] = ', '.join(filtered_matches)

        return df['Упоминаемые законы']


def find_duplicate_quotes_tfidf(df):
    vectorized = TfidfVectorizer()
    tfidf_matrix = vectorized.fit_transform(df['Текст'])
    similarity_matrix = cosine_similarity(tfidf_matrix)
    duplicates = []
    n_docs = len(df)
    for i in range(n_docs):
        duplicate_indices = [j for j in range(n_docs) if similarity_matrix[i, j] > 0.99 and i != j]

        if duplicate_indices:
            duplicate = {
                'Law Index': i,
                'Duplicate Indices': duplicate_indices,
                'Duplicate Text': df.iloc[i]['Text']
            }
            duplicates.append(duplicate)

    duplicates_df = pd.DataFrame(duplicates)
    return duplicates_df


def create_references_df(df):
    references_df = pd.DataFrame(columns=['Found_Law_Index', 'Name_Index'])
    for i, law_name in enumerate(df['Упомянутые законы']):
        if law_name:
            pattern = re.escape(law_name)
            regex = re.compile(pattern, re.IGNORECASE)
            for j, name in enumerate(df['Название закона']):
                match = regex.search(name)
                if match:
                    references_df.at[i, 'Found_Law_Index'] = i
                    references_df.at[i, 'Name_Index'] = j
                    break

    return references_df


def analyze_data(df):
    tokens = df['Текст']
    tokens = tokens.apply(lambda token: process_text(token))
    tokens = [[token for token in sublist if token not in ['ст', 'n']] for sublist in tokens]
    tokens = pd.Series(tokens)
    df['Токены'] = tokens
    df["Обработанный текст"] = tokens.apply(join_list)
    name = df['Название закона'].apply(lambda text: process_text(text))
    name = pd.Series(name)
    name = name.apply(join_list)

    lsi_vectors = get_lsi_vectors(name)

    df['Номер темы'] = get_clastering_KMeans(lsi_vectors, 12)
    df['Кем принят'] = df['Текст'].apply(extract_organization)
    df['Утратившие силу'] = df['Текст'].str.extract(r'утратившим силу (.+?) \(', expand=False)
    df['Упомянутые законы'] = extract_law_names(df)

    return df


#duplicates_df = find_duplicate_quotes_tfidf(df)
#references_df = create_references_df(df)
