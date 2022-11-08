# 기존의 형용사 동사 추출에 활용되던 rahinomorph 와 komoran 대신 Okt(custom_konlpy)를 활용해 시간 대폭 감축
# custom_konlpy 라이브러리를 추가 설치해야하며 여기에 필요한 사용자 사전을 따로 build할 필요가 있음

from Theme.import_db import import_data
from Theme.preprocessing import *
import numpy as np
import pandas as pd
from konlpy.tag import Mecab
from ckonlpy.tag import Twitter
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
import time, pickle

from kiwipiepy import Kiwi, Option
kiwi = Kiwi(options=Option.INTEGRATE_ALLOMORPH)
userDictPath = './wordreplace/kiwidict.txt'
kiwi.load_user_dictionary(userDictPath)
kiwi.prepare()

mecab = Mecab(dicpath="C:\\mecab\\mecab-ko-dic")
twitter = Twitter(use_twitter_dictionary=False)
okt_dict = pd.read_csv('.\\wordreplace\\okt_dict.csv', encoding='cp949')
okt_dict['word'] = okt_dict['word'].astype('str')
for i in range(okt_dict.shape[0]):
    twitter.add_dictionary(okt_dict.iloc[i,0], okt_dict.iloc[i,1])
print('Load user dictionary')


def import_stopword():
    # 불용어 사전 import
    stopwords = []
    with open('../Stopwords/stopwords_list_game.txt', 'r') as f:
        lines = f.readlines()
        for line in lines:
            stopwords.append(line[:-1].strip())
    return stopwords

#품사 지정 function 정의

def tokenizer(raw):
    return np.array([word+"다" for (word, pos, s, e) in kiwi.analyze(raw)[-1][0] if pos in ['VA', 'VV'] and len(word)>1])

def mecab_tokenizer(raw):
    return [
        word for word, tag in mecab.pos(raw,flatten=True)
            if (len(word) > 1 and tag in ["NNG"]) #중요한 한글자 단어는 조건문으로 따로 추가
        ]

def mecab_tokenizer2(raw):
    tokenlist = [
        word for word, tag in mecab.pos(raw,flatten=True)
            if ((len(word) > 1) & (tag in ["NNP"]))
        ]

    for word, tag in mecab.pos(raw, flatten=True):
        if ((word in ['ost', 'bgm','cg','imax','srpg','rpg', 'mmorpg']) & (tag in ["SL"])): #자주 출현할 수 있는 외래어 리스트를 따로 지정함
            tokenlist.append(word)

    return tokenlist

def Okt_tokenizer(raw):
    tokenlist = []
    for wordtag in twitter.pos(raw, norm=True, stem=True):
        if wordtag[1] in ['Adjective', 'Verb', 'Hashtag']:
            tokenlist.append(wordtag[0])
    return tokenlist


def bigram_tokenizer(raw, option=2): #Bigram tokenizer
    ngram = []
    filtered_ngram = []
    pos_list = mecab.pos(raw)
    for t in range(0, len(pos_list) - (option - 1)):
        ngram.append(tuple(pos_list[t:t + option]))
    for ((word1, pos1), (word2, pos2)) in ngram:
        if any((word1 in stopwords, word2 in stopwords)):
            pass
        elif pos1 in ["NNG", "NNP", "VA", "VV", "XR", "MAG"] and pos2 in ["NNG", "NNP", "VA", "VV", "XR"] and len(word1) + len(word2) > 2:
            if pos2 in ['VA', 'VV']:
                word2 = word2 + '다'
                filtered_ngram.append(word1 + " " +word2)
            else:
                filtered_ngram.append(word1 + " " +word2)

    return filtered_ngram

def trigram_tokenizer(raw, option = 3): #Trigram tokenizer
    ngram = []
    filtered_ngram = []

    pos_list = mecab.pos(raw)
    for t in range(0, len(pos_list) - (option - 1)):
        ngram.append(tuple(pos_list[t:t + option]))

    find_pos = ["NNG", "NNP", "VA", "VV", "XR", "MAG", "JKG", "JKS", "JKO", "JKB"]
    jobusa = ["JKG", "JKS", "JKO", "JKB", "MAG"]
    for ((word1, pos1), (word2, pos2), (word3, pos3)) in ngram:
        if any((word1 in stopwords, word2 in stopwords, word3 in stopwords)) or (len(word1) + len(word2) + len(word3)) == 3:
            pass
        elif pos1 in find_pos and pos2 in find_pos and pos3 in find_pos and all((pos1 not in jobusa, pos3 not in jobusa)):
            if pos3 in ['VA', 'VV']:
                word3 = word3 + '다'
                if pos2 in ['JKB','JKG', 'JKS', 'JKO']:
                    filtered_ngram.append(word1 + word2 + " " + word3)
                else:
                    filtered_ngram.append(word1 + " " + word2 + " " + word3)
            else:
                if pos2 in ['JKB', 'JKG', 'JKS', 'JKO']:
                    filtered_ngram.append((word1 + word2 + " " + word3))
                else:
                    filtered_ngram.append(word1 + " " + word2 + " " + word3)

    return filtered_ngram


def ngram_mat(doc_to_mat, min_df = 5, ngram = 2, tf_idf = False):
    if ngram == 2:
        if tf_idf == False:
            vectorizer = CountVectorizer(tokenizer=bigram_tokenizer, min_df=min_df)
        else:
            vectorizer = TfidfVectorizer(tokenizer=bigram_tokenizer, min_df=min_df)
        cnt_to_vec = vectorizer.fit_transform(doc_to_mat)
        features = vectorizer.get_feature_names()
        ngram_df = pd.DataFrame(cnt_to_vec.toarray(), columns=features)
        print("bi-gram word extraction")

    elif ngram == 3:
        if tf_idf == False:
            vectorizer = CountVectorizer(tokenizer=trigram_tokenizer, min_df=min_df)
        else:
            vectorizer = TfidfVectorizer(tokenizer=trigram_tokenizer, min_df=min_df)
        cnt_to_vec = vectorizer.fit_transform(doc_to_mat)
        features = vectorizer.get_feature_names()
        ngram_df = pd.DataFrame(cnt_to_vec.toarray(), columns=features)
        print("tri-gram word extraction")

    return ngram_df

# count vectorizer
def Postagging_count(doc_to_mat, min_df = 5, tf_idf_mode = False):
    starttime  = time.time()
    if tf_idf_mode == False:
        vectorizer = CountVectorizer(tokenizer=mecab_tokenizer, min_df=min_df, ngram_range=(1, 1), stop_words=stopwords)
    else:
        vectorizer = TfidfVectorizer(tokenizer=mecab_tokenizer, min_df=min_df, ngram_range=(1, 1), stop_words=stopwords)
    cnt_to_vec = vectorizer.fit_transform(doc_to_mat)
    features = vectorizer.get_feature_names()
    nouns_df = pd.DataFrame(cnt_to_vec.toarray(), columns=features)
    print("vectorizing 1 : " , time.time() - starttime)

    starttime = time.time()
    if tf_idf_mode == False:
        vectorizer = CountVectorizer(tokenizer=mecab_tokenizer2, min_df=min_df, ngram_range=(1, 1), stop_words=stopwords)
    else:
        vectorizer = TfidfVectorizer(tokenizer=mecab_tokenizer2, min_df=min_df, ngram_range=(1, 1), stop_words=stopwords)
    cnt_to_vec = vectorizer.fit_transform(doc_to_mat)
    features = vectorizer.get_feature_names()
    uqnouns_df = pd.DataFrame(cnt_to_vec.toarray(), columns=features)
    print("vectorizing 1 : ", time.time() - starttime)

    starttime = time.time()
    if tf_idf_mode == False:
        vectorizer = CountVectorizer(tokenizer=tokenizer, min_df=min_df, ngram_range=(1, 1), stop_words=stopwords)
    else:
        vectorizer = TfidfVectorizer(tokenizer=tokenizer, min_df=min_df, ngram_range=(1, 1), stop_words=stopwords)
    cnt_to_vec = vectorizer.fit_transform(doc_to_mat)
    adver_features = vectorizer.get_feature_names()
    adjecverb_df = pd.DataFrame(cnt_to_vec.toarray(), columns=adver_features)
    print("vectorizing 1 : ", time.time() - starttime)

    filtered_words = {}
    for tok in adver_features:
        for word, tag in mecab.pos(tok, flatten=True):
            if len(word) > 1 and tag in ["NNG"] and word in nouns_df.columns:
                if word in list(filtered_words.keys()):
                    filtered_words[word] += adjecverb_df.loc[:, tok]
                else:
                    filtered_words[word] = adjecverb_df.loc[:, tok]
    filtered_df = pd.DataFrame.from_dict(filtered_words)
    adjusted_nouns = nouns_df.copy()
    adjusted_nouns.loc[:, filtered_df.columns] = nouns_df.loc[:, filtered_df.columns] - filtered_df
    adjusted_nouns[adjusted_nouns < 0] = 0
    for c in adjusted_nouns.columns:
        if adjusted_nouns.loc[:,c].sum(axis=0) < min_df:
            del adjusted_nouns[c]

    return adjusted_nouns, uqnouns_df, adjecverb_df

def Postagging_tfidf(doc_to_mat, min_df): #For sentiment classification modeling
    starttime  = time.time()

    vectorizer_noun = TfidfVectorizer(tokenizer=mecab_tokenizer, min_df=min_df, ngram_range=(1, 2), stop_words=stopwords)
    cnt_to_vec = vectorizer_noun.fit_transform(doc_to_mat)
    features = vectorizer_noun.get_feature_names()
    nouns_df = pd.DataFrame(cnt_to_vec.toarray(), columns=features)
    print("vectorizing 1 : " , time.time() - starttime)

    starttime = time.time()
    vectorizer_adv = TfidfVectorizer(tokenizer=Okt_tokenizer, min_df=5, ngram_range=(1, 1), stop_words=stopwords)
    cnt_to_vec = vectorizer_adv.fit_transform(doc_to_mat)
    adver_features = vectorizer_adv.get_feature_names()
    adjecverb_df = pd.DataFrame(cnt_to_vec.toarray(), columns=adver_features)
    print("vectorizing 2 : ", time.time() - starttime)

    filtered_words = {}
    for tok in adver_features: #한 개의 단어에 대해 두개의 품사 인식을 방지하기 위한 line
        for word, tag in mecab.pos(tok, flatten=True):
            if len(word) > 1 and tag in ["NNG"] and word in nouns_df.columns:
                if word in list(filtered_words.keys()):
                    filtered_words[word] += adjecverb_df.loc[:, tok]
                else:
                    filtered_words[word] = adjecverb_df.loc[:, tok]
    filtered_df = pd.DataFrame.from_dict(filtered_words)
    adjusted_nouns = nouns_df.copy()
    adjusted_nouns.loc[:, filtered_df.columns] = nouns_df.loc[:, filtered_df.columns] - filtered_df
    adjusted_nouns[adjusted_nouns < 0] = 0

    pickle.dump(vectorizer_noun, open("./vectorizer_noun.pickle", "wb"))
    pickle.dump(vectorizer_adv, open("./vectorizer_adv.pickle", "wb"))

    return adjusted_nouns, adjecverb_df

def get_pos_cnt(corpus_df,matrix_mode):
    print("Construct document-term matrix...")
    # 한글자만 들어간 문서를 제거함. > 내용 분석에서 제외하는 부분, 버즈량 count는 원본 데이터 상에서 날짜별로 count
    strat_time = time.time()

    doc_to_mat = list(corpus_df['user_text'].values)
    nouns_df, uqnouns_df, adjecverb_df = Postagging_count(doc_to_mat, tf_idf_mode=matrix_mode)

    # 품사 중복 tagging 제거
    # 같은 단어라도 문장 내 역할에 따라 품사가 다르게 인식되어 다르게 컬럼을 구성하므로 값을 합쳐줘야함
    same_tdm1 = pd.concat([nouns_df, uqnouns_df], join= 'inner')
    duplicate_token = list(same_tdm1.columns)
    nouns_df.loc[:,duplicate_token] = nouns_df.loc[:,duplicate_token] + uqnouns_df.loc[:,duplicate_token]
    uqnouns_df = uqnouns_df.loc[:,~uqnouns_df.columns.isin(duplicate_token)]

    same_tdm2 = pd.concat([adjecverb_df, uqnouns_df], join='inner')
    duplicate_token2 = list(same_tdm2.columns)
    adjecverb_df.loc[:, duplicate_token2] = adjecverb_df.loc[:, duplicate_token2] + uqnouns_df.loc[:, duplicate_token2]
    uqnouns_df = uqnouns_df.loc[:, ~uqnouns_df.columns.isin(duplicate_token2)]

    # tdm 저장
    count_tdm = pd.concat([nouns_df, uqnouns_df, adjecverb_df], axis=1)
    print('구축된 count 기반 document-term matrix 크기', count_tdm.shape)

    # 품사별 count table 저장 임시
    nouns_cnt = extract_count_table(nouns_df)
    nouns_cnt.to_csv("../results/브라운더스트_Theme_keyword_nouns.csv", index = False, encoding='cp949')
    uqnouns_cnt = extract_count_table(uqnouns_df)
    uqnouns_cnt.to_csv("../results/브라운더스트_Theme_keyword_uqnouns.csv", index = False, encoding='cp949')
    adverb_cnt = extract_count_table(adjecverb_df)
    adverb_cnt.to_csv("../results/브라운더스트_Theme_keyword_adverb.csv", index = False, encoding='cp949')

    print(time.time() - strat_time, ' sec spent for vecetorizing')
    return count_tdm

def vectorizing_text(test_text):
    doc_to_mat = test_text
    # print(doc_to_mat)
    vectorizer_n = pickle.load(open("./vectorizer_noun.pickle", "rb"))
    vectorizer_v = pickle.load(open("./vectorizer_adv.pickle", "rb"))

    test_vec1 = vectorizer_n.transform(doc_to_mat)
    features1 = vectorizer_n.get_feature_names()

    test_vec2 = vectorizer_v.transform(doc_to_mat)
    features2 = vectorizer_v.get_feature_names()

    nouns_df = pd.DataFrame(test_vec1.toarray(), columns=features1)
    adverb_df = pd.DataFrame(test_vec2.toarray(), columns=features2)

    filtered_words = {}
    for tok in features2:  # 한 개의 단어에 대해 두개의 품사 인식을 방지하기 위한 line
        for word, tag in mecab.pos(tok, flatten=True):
            if len(word) > 1 and tag in ["NNG"] and word in nouns_df.columns:
                if word in list(filtered_words.keys()):
                    filtered_words[word] += adverb_df.loc[:, tok]
                else:
                    filtered_words[word] = adverb_df.loc[:, tok]
    filtered_df = pd.DataFrame.from_dict(filtered_words)
    adjusted_nouns = nouns_df.copy()
    adjusted_nouns.loc[:, filtered_df.columns] = nouns_df.loc[:, filtered_df.columns] - filtered_df
    adjusted_nouns[adjusted_nouns < 0] = 0

    test_tdm = pd.concat([adjusted_nouns, adverb_df], axis=1)
    return test_tdm

def save_pos_df(contents_name, df, tfidf = False):
    count_tdm = get_pos_cnt(df,matrix_mode = tfidf)
    if tfidf == False:
        count_tdm.to_pickle('../matrix/'+ str(contents_name) + '_count_tdm.pkl')
    else:
        count_tdm.to_pickle('../matrix/' + str(contents_name) + '_tfidf_tdm.pkl')
    print('Matrix saved...')

#단어 count table 추출
def extract_count_table(tdm):
    cnt_keyword = tdm.sum(axis=0).sort_values(ascending=False)
    cnt_df = cnt_keyword.reset_index()
    cnt_df.columns = ['word', 'count']
    return cnt_df

def ngram_matrix(bigram_mat, trigram_mat, ti_idf = False):
    if ti_idf == False:
        unigram_mat = pd.read_pickle('../matrix/'+contents_name+"_count_tdm.pkl")
        return pd.concat([unigram_mat, bigram_mat, trigram_mat], axis=1)
    else:
        unigram_mat = pd.read_pickle('../matrix/' + contents_name + "_tfidf_tdm.pkl")
        return pd.concat([unigram_mat, bigram_mat, trigram_mat], axis=1)

if __name__ == "__main__":
    contents_name = "마스크5부제"
    #task_list = get_task_list(contents_name)
    #contents_df = import_data(task_list)
    contents_df = pd.read_csv("../raw_data/마스크5부제.csv")
    corpus_df = preprocessing(contents_df)
    corpus_df.to_csv("../matrix/"+ contents_name +"_raw.csv", index=False)
    # print(corpus_df.shape)

    stopwords = import_stopword()
    for add_stop in str(input('Add stop words, split white space : ')).split():
        stopwords.append(add_stop)

    # corpus_df = include_words(corpus_df) #customizinig for text filtering
    # corpus_df = exclude_words(corpus_df)

    # tfidf = True 옵션 시 Tfidf matrix 생성 후 저장
    tfidf_matrix = False

    if tfidf_matrix == False:
        save_pos_df(contents_name, corpus_df, tfidf=tfidf_matrix)
        count_word_table = extract_count_table(pd.read_pickle('../matrix/' + contents_name + '_count_tdm.pkl'))
        count_word_table.to_csv('../results/' + contents_name + '_word_cnt.csv', index=False)  # Uni-gram 단어 count table
    else:
        save_pos_df(contents_name, corpus_df, tfidf=tfidf_matrix)
        tfidf_word_table = extract_count_table(pd.read_pickle('../matrix/' + contents_name + '_tfidf_tdm.pkl'))
        tfidf_word_table.to_csv('../results/' + contents_name + '_word_tfidf.csv', index=False)  # Uni-gram 단어 tfidf score table

    # N-gram extraction
    bigram_tdm = ngram_mat(doc_to_mat=list(corpus_df['user_text'].values.astype('U')), ngram=2, tf_idf=tfidf_matrix)
    bigram_cnt = extract_count_table(bigram_tdm)
    bigram_cnt.to_csv("../results/" + contents_name + "_bigram.csv", encoding='cp949',
                      index=False)  # bi-gram 단어 count table

    trigram_tdm = ngram_mat(doc_to_mat=list(corpus_df['user_text'].values.astype('U')), ngram=3, tf_idf=tfidf_matrix)
    trigram_cnt = extract_count_table(trigram_tdm)
    trigram_cnt.to_csv("../results/" + contents_name + "_trigram.csv", encoding='cp949', index=False)  # tri-gram 단어 count table

    ngram_matrix = ngram_matrix(bigram_tdm, trigram_tdm, ti_idf=False)
    ngram_matrix.to_pickle("../matrix/"+contents_name+"_ngram_tdm.pkl") #ngram 단어까지 포함한 term-document matrix 저장

    #test_text = list(corpus_df['user_text'].values)
    #print(vectorizing_text(test_text))
    print('Save Document-term matrix')