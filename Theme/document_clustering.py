# 경쟁사를 포함하는 모든 게임 문서를 기반으로 하는 document clustering
# Preprocessing, Vetorizing, Finding optimal number of clusters, Document clustering using Spherical K-means

from Theme.preprocessing import preprocessing
from Theme.vetorizing_tdm import import_stopword
import pandas as pd
import numpy as np
from scipy import sparse
from sklearn.feature_extraction.text import TfidfVectorizer
from soyclustering import SphericalKMeans
from kneed import KneeLocator
import time
from konlpy.tag import Mecab
mecab = Mecab(dicpath="C:\\mecab\\mecab-ko-dic")

def merging_all_corpus(contents_list):
    # 경쟁사를 포함하는 모든 문서를 통합하고 game 이라는 label column 생성
    df1 = pd.read_csv('../raw_data/'+contents_list[0]+'.csv')
    df1['game'] = contents_list[0]
    for game in contents_list[1:]:
        new_game_df = pd.read_csv('../raw_data/'+game+'.csv')
        new_game_df['game'] = game
        df1 = df1.append(new_game_df)

    all_corpus_df = df1.reset_index(drop=True)

    all_corpus_df = preprocessing(all_corpus_df)
    all_corpus_df['user_text'] = all_corpus_df['user_text'].astype('str')
    all_corpus_df['text_len'] = all_corpus_df['user_text'].apply(len)
    filtered_docs = all_corpus_df.loc[all_corpus_df['text_len'] >= 11, :]
    print(filtered_docs .shape)
    print(filtered_docs ['game'].value_counts())

    return filtered_docs

def mecab_tokenizer(raw):
    return [
        word for word, tag in mecab.pos(raw,flatten=True)
            if (len(word) > 1 and tag in ["NNG", "NNP"]) #중요한 한글자 단어는 조건문으로 따로 추가
        ]

def bigram_tokenizer(raw, option=2): #Bigram tokenizer
    ngram = []
    filtered_ngram = []
    pos_list = mecab.pos(raw)
    for t in range(0, len(pos_list) - (option - 1)):
        ngram.append(tuple(pos_list[t:t + option]))
    for ((word1, pos1), (word2, pos2)) in ngram:
        if any((word1 in stopwords, word2 in stopwords)):
            pass
        elif pos1 in ["NNG", "NNP", "VA"] and pos2 in ["NNG", "NNP"] and (len(word1) + len(word2)) > 3:
            filtered_ngram.append(word1 + " " +word2)

    return filtered_ngram


def vectorizing(doc_to_mat,stopwords):
    vectorizer = TfidfVectorizer(tokenizer=mecab_tokenizer, min_df=20, ngram_range=(1, 1), stop_words=stopwords,
                                 max_features=1000)
    cnt_to_vec = vectorizer.fit_transform(doc_to_mat)
    features = vectorizer.get_feature_names()
    review_tdm = pd.DataFrame(cnt_to_vec.toarray(), columns=features)

    vectorizer2 = TfidfVectorizer(tokenizer=bigram_tokenizer, min_df=20, stop_words=stopwords)
    cnt_to_vec2 = vectorizer2.fit_transform(doc_to_mat)
    features2 = vectorizer2.get_feature_names()
    review_tdm2 = pd.DataFrame(cnt_to_vec2.toarray(), columns=features2)

    review_tdm = pd.concat([review_tdm, review_tdm2], axis=1)

    return review_tdm

def finding_optimal_k(review_tdm):
    trial_dict = {}
    start_time = time.time()
    for i in range(1, 31):
        Sum_of_squared_distances = []
        K = range(2, 13)
        for k in K:
            spherical_kmeans = SphericalKMeans(
                n_clusters=k,
                max_iter=50,
                verbose=0,
                sparsity=None,
                tol=1e-7,
                init='similar_cut',
                n_jobs=-1
            )
            spherical_kmeans = spherical_kmeans.fit(sparse.csr_matrix(review_tdm.values))
            Sum_of_squared_distances.append(spherical_kmeans.inertia_)
        trial_dict[i] = Sum_of_squared_distances
    print(time.time() - start_time, 'spent for measuring distance by number of clusters')

    tmp_df = pd.DataFrame.from_dict(trial_dict)
    kn = KneeLocator(range(2, 13), tmp_df.median(axis=1), curve='convex', direction='decreasing')
    return kn.elbow


def document_clustering(filtered_docs, review_tdm, min_df, k):
    iter = 0
    spherical_kmeans = SphericalKMeans(
        n_clusters=k,
        max_iter=50,
        verbose=0,
        sparsity=None,
        tol=1e-7,
        init='similar_cut',
        random_state=77
    )

    while True:
        clustered_docs2 = spherical_kmeans.fit_predict(sparse.csr_matrix(review_tdm.values))
        review_tdm['cluster_label'] = clustered_docs2
        iter += 1
        if review_tdm['cluster_label'].value_counts().min() > (review_tdm.shape[0] * min_df):
            print(spherical_kmeans.inertia_)
            break
        else:
            del review_tdm['cluster_label']

        if iter > 1000:
            print('CannotFound cluster meeting min_df')

    print('clustering finished')
    filtered_docs['cluster_label'] = review_tdm['cluster_label'].values

    word_tmplist = review_tdm.columns[:-1]

    topicword_df_list = []
    for n, group in review_tdm.groupby(['cluster_label']):
        word_dict = {}
        print('cluster # : ', n)
        for word in word_tmplist:
            score = (group[word].sum(axis=0) / review_tdm[word].sum(axis=0)) * np.log(group[word].sum(axis=0) + 1e-10)
            word_dict[word] = score
        tmp_df = pd.DataFrame(np.zeros((len(list(word_dict.keys())), 2)), columns=['word', 'score'])

        tmp_df['word'] = list(word_dict.keys())
        tmp_df['score'] = list(word_dict.values())
        tmp_df['cluster_label'] = n
        tmp_df = tmp_df.sort_values(by='score', ascending=False)[:20].reset_index(drop=True)
        print(tmp_df)

        topicword_df_list.append(tmp_df)

    topic_score_df = pd.concat(topicword_df_list, axis=0)

    game_topcis_df = filtered_docs.groupby(['game'])['cluster_label'].value_counts(normalize=True).unstack()
    game_topcis_df = game_topcis_df.reset_index()

    game_topcis_df.iloc[:, 1:] = game_topcis_df.iloc[:, 1:] * 100
    topics = game_topcis_df.columns[1:]

    for col in topics:
        game_topcis_df[col] = (game_topcis_df[col] - game_topcis_df[col].min()) / (game_topcis_df[col].max() - game_topcis_df[col].min())
    game_topcis_df.iloc[:, 1:] = game_topcis_df.iloc[:, 1:] * 100

    return game_topcis_df, topic_score_df

if __name__ == '__main__':
    contents_list = ['브라운더스트','소녀전선', '붕괴', '파이널블레이드', '랑그릿사', '데일리판타지']
    filtered_docs = merging_all_corpus(contents_list)

    doc_to_mat = filtered_docs['user_text'].values
    stopwords = import_stopword()
    # 브라운더스트 랑그릿사 데일리 판타지 소녀전선 붕괴 파이널 블레이드 소녀 전선 리니지 대하 더스 라그 주세 나용 랑그 릿사 군요 리뷰
    for add_stop in str(input('Add stop words, split white space : ')).split():
        stopwords.append(add_stop)

    review_tdm = vectorizing(doc_to_mat,stopwords)

    print('Determine optimal number of clusters k')
    min_df = 0.05
    ck = finding_optimal_k(review_tdm)
    print('Optimal number of clusters : ' , ck)

    game_topcis_df, topic_score_df = document_clustering(filtered_docs, review_tdm, min_df, ck)

    game_topcis_df.to_csv("../results/브라운더스트_Scenario_topic_ratio.csv", index = False)
    topic_score_df.to_csv("../results/브라운더스트_Theme_keyword_topicword.csv", index = False)
    print('Complete!')