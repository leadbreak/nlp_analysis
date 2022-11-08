import pickle
import numpy as np
import pandas as pd
from Theme import import_db, preprocessing
from Theme.vetorizing_tdm import import_stopword
from Theme.extract_sentiment import import_sentdic
import time, os

from kiwipiepy import Kiwi
kiwi = Kiwi()
userDictPath = './wordreplace/kiwidict.txt'
kiwi.load_user_dictionary(userDictPath)
kiwi.prepare()

from keras import models,layers
from keras.preprocessing.text import Tokenizer
from keras.preprocessing import sequence

def tokenizer(raw,stopwords):
    return np.array([word for (word, pos, s, e) in kiwi.analyze(raw)[0][0] if pos in ['NNG', 'NNP', 'VA', 'VV', 'XR','MAG', 'SL'] and word not in stopwords])

def keras_tokenizer(text_list, sequence_length = 100):
    tokenizer = Tokenizer(num_words=10000) #num_words: the maximum number of words to keep, based on word frequency.
    tokenizer.fit_on_texts(text_list)

    X_data_index = tokenizer.texts_to_sequences(text_list)
    X_data = sequence.pad_sequences(X_data_index, maxlen=sequence_length) # sequence length 개의 단어 조합으로 구성된 n X num_word matrix
    return X_data, tokenizer

def LSTM_model():
    annmodel = models.Sequential()
    annmodel.add(layers.Embedding(9999, 128, input_length=100))
    annmodel.add(layers.LSTM(128))
    annmodel.add(layers.Dense(1, activation='sigmoid'))
    annmodel.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    return annmodel

def non_sentiment_doc(tdm, sentiment_words):
    # 감성 단어가 포함되지 않은 문서의 index list 를 return
    sentiment_docs = tdm.loc[:,tdm.columns.isin(sentiment_words)]
    return list(sentiment_docs.loc[(sentiment_docs==0).all(axis=1)].index)

def get_sentiment_label(test_corpus, tokenizer, model, nonsent_index):
    # corpus 를 tokenizing 하고 학습된 모델로 tagging 작업을 진행
    test_index = tokenizer.texts_to_sequences(test_corpus)
    test_data = sequence.pad_sequences(test_index, maxlen=100)
    predict_prob_arr = model.predict(np.array(test_data))
    corpus_df['sentiment_prob'] = predict_prob_arr.reshape(-1)

    corpus_df['sentiment_label'] = np.where(corpus_df['sentiment_prob'] >= 0.55, 1, 0)
    corpus_df.loc[((corpus_df['sentiment_label'] == 0) & (corpus_df['sentiment_prob'] >= 0.45)), 'sentiment_label'] = 2
    corpus_df.loc[nonsent_index,'sentiment_label'] = 2

    return corpus_df

def sentiment_trend(corpus_df):
    # tagging 된 corpus 를 받아서 일자별로 aggregate
    corpus_df['date'] = pd.to_datetime(corpus_df['date'])
    corpus_df['date'] = corpus_df['date'].dt.date
    sentiment_timeline = corpus_df.groupby(['date'])['sentiment_label'].value_counts().unstack().fillna(0)
    sentiment_timeline.columns = ['positive', 'negative', 'neutral']
    return sentiment_timeline

if __name__ == "__main__":
    # 전처리된 corpus 파일과 tdm 파일 load
    # tdm 을 기반으로 감성 단어가 1개도 포함되지 않은 문서 번호를 저장
    # corpus 파일을 LSTM 모델에 맞게 tokenizing 진행
    # 학습된 모델로 각 문서별로 sentiment 분류 확률 return
    # 확률값을 기반으로 긍정 부정 중립을 태깅하고 이전에 감성 단어가 포함되지 않은 문서는 마지막에 중립 태깅

    review_pos = pd.read_pickle('../matrix/'+"브라운더스트"+"_count_tdm.pkl")

    if os.path.isfile("../matrix/브라운더스트_raw.csv"):
        corpus_df = pd.read_csv("../matrix/브라운더스트_raw.csv")
    else:
        task_list = import_db.get_task_list('브라운더스트')
        contents_df = import_db.import_data(task_list)
        corpus_df = preprocessing.preprocessing(contents_df)
        corpus_df.to_csv('../matrix/브라운더스트_raw.csv')

    with open('./keras_tokenizer.pickle', 'rb') as tok:
        fit_tokenizer = pickle.load(tok)
    loaded_model = pickle.load(open('./lstm_learning.h5', 'rb'))


    stopwords = import_stopword()
    sent_df = import_sentdic()
    test_corpus = list(corpus_df.loc[:, 'user_text'].values)
    for i, document in enumerate(test_corpus):
        test_corpus[i] = ' '.join(tokenizer(document, stopwords))

    sentiment_words = sent_df['word'].values
    nonsent_index = non_sentiment_doc(review_pos,sentiment_words)

    sentiment_corpus = get_sentiment_label(test_corpus, fit_tokenizer, loaded_model, nonsent_index)
    sentiment_corpus.to_csv("../matrix/브라운더스트_raw_sentlabel.csv", index = False)
    sentiment_timeline_df = sentiment_trend(sentiment_corpus)

    sentiment_timeline_df.to_csv('../results/'+'브라운더스트'+'_sentiment_timeline.csv')
