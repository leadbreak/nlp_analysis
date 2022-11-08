from Theme.import_db import import_data
from Theme.preprocessing import *
import pandas as pd
from PyKomoran import *
import rhinoMorph
from konlpy.tag import Mecab
from sklearn.feature_extraction.text import CountVectorizer
import time


mecab = Mecab(dicpath="C:\\mecab\\mecab-ko-dic")
rn = rhinoMorph.startRhino()
komoran = Komoran("STABLE")
komoran.set_user_dic('./wordreplace/dic.user')

def import_stopword():
    # 불용어 사전 import
    stopwords = []
    with open('../Stopwords/stopwords_list_game.txt', 'r') as f:
        lines = f.readlines()
        for line in lines:
            stopwords.append(line[:-1].strip())
    return stopwords

#품사 지정 function 정의
def mecab_tokenizer(raw):
    return [
        word for word, tag in mecab.pos(raw,flatten=True)
            if len(word) > 1 and tag in ["NNG"]
        ]

def mecab_tokenizer2(raw):
    tokenlist = [
        word for word, tag in mecab.pos(raw,flatten=True)
            if ((len(word) > 1) & (tag in ["NNP"]))
        ]

    for word, tag in mecab.pos(raw, flatten=True):
        if ((word in ['ost', 'bgm','cg','imax']) & (tag in ["SL"])):
            tokenlist.append(word)

    return tokenlist

def rhino_tokenizer1(raw):
    tokenlist = list(rhinoMorph.onlyMorph_list(rn, raw, pos=['VA'], eomi=True))
    if len(tokenlist) ==0:
        for word, tag in mecab.pos(raw,flatten=True):
            if tag in ["VA"] and word not in stopwords:
                tokenlist.append(word+"다")
            if "VA+" in tag and word not in stopwords:
                va = komoran.get_morphes_by_tags(word, tag_list=['VA'])
                if len(va) > 0:
                    tokenlist.append(va[0]+"다")
    return tokenlist

def komoran_tokenizer(raw): #품사 지정
    tokenlist = []
    for word in komoran.get_morphes_by_tags(raw, tag_list=['VV']):
        if word not in stopwords:
            tokenlist.append(word+'다')
    return tokenlist


# count vectorizer
def Postagging_count(doc_to_mat, min_df = 10):

    vectorizer = CountVectorizer(tokenizer=mecab_tokenizer, min_df=min_df, ngram_range=(1, 1), stop_words=stopwords)
    cnt_to_vec = vectorizer.fit_transform(doc_to_mat)
    features = vectorizer.get_feature_names()
    nouns_df = pd.DataFrame(cnt_to_vec.toarray(), columns=features)

    vectorizer = CountVectorizer(tokenizer=mecab_tokenizer2, min_df=min_df, ngram_range=(1, 1), stop_words=stopwords)
    cnt_to_vec = vectorizer.fit_transform(doc_to_mat)
    features = vectorizer.get_feature_names()
    uqnouns_df = pd.DataFrame(cnt_to_vec.toarray(), columns=features)

    vectorizer = CountVectorizer(tokenizer=rhino_tokenizer1, min_df=min_df, ngram_range=(1, 1), stop_words=stopwords)
    cnt_to_vec = vectorizer.fit_transform(doc_to_mat)
    features = vectorizer.get_feature_names()
    adjec_df = pd.DataFrame(cnt_to_vec.toarray(), columns=features)

    vectorizer = CountVectorizer(tokenizer=komoran_tokenizer, min_df=min_df, ngram_range=(1, 1), stop_words=stopwords)
    cnt_to_vec = vectorizer.fit_transform(doc_to_mat)
    features = vectorizer.get_feature_names()
    verb_df = pd.DataFrame(cnt_to_vec.toarray(), columns=features)

    return nouns_df, uqnouns_df, adjec_df, verb_df

def get_pos_cnt(corpus_df):
    print("Construct document-term matrix...")
    # 한글자만 들어간 문서를 제거함. > 내용 분석에서 제외하는 부분, 버즈량 count는 원본 데이터 상에서 날짜별로 count
    strat_time = time.time()

    doc_to_mat = list(corpus_df['user_text'].values)
    nouns_df, uqnouns_df, adjec_df, verb_df = Postagging_count(doc_to_mat)

    # 품사 중복 tagging 제거
    # 같은 단어라도 문장 내 역할에 따라 품사가 다르게 인식되어 다르게 컬럼을 구성하므로 값을 합쳐줘야함
    same_tdm1 = pd.concat([nouns_df, uqnouns_df], join= 'inner')
    duplicate_token = list(same_tdm1.columns)
    nouns_df.loc[:,duplicate_token] = nouns_df.loc[:,duplicate_token] + uqnouns_df.loc[:,duplicate_token]
    uqnouns_df = uqnouns_df.loc[:,~uqnouns_df.columns.isin(duplicate_token)]

    same_tdm2 = pd.concat([adjec_df, verb_df], join= 'inner')
    duplicate_token2 = list(same_tdm2.columns)
    adjec_df.loc[:,duplicate_token2] = adjec_df.loc[:,duplicate_token2] + verb_df.loc[:,duplicate_token2]
    verb_df = verb_df.loc[:,~verb_df.columns.isin(duplicate_token2)]

    # tdm 저장
    count_tdm = pd.concat([nouns_df, uqnouns_df, adjec_df,verb_df], axis=1)
    print('구축된 count 기반 document-term matrix 크기', count_tdm.shape)


    print(time.time() - strat_time, ' sec spent for vecetorizing')
    return count_tdm

def save_pos_df(df):
    count_tdm = get_pos_cnt(df)
    count_tdm.to_csv('../matrix/'+ str(input("save file name? : ")) + '_count_tdm.csv', index= False)
    print('Matrix saved...')

#단어 count table 추출
def extract_count_table(tdm):
    cnt_keyword = tdm.sum(axis=0).sort_values(ascending=False)
    cnt_df = cnt_keyword.reset_index()
    cnt_df.columns = ['word', 'count']
    return cnt_df

if __name__ == "__main__":

    contents_name = "브라운더스트"
    task_list = get_task_list(contents_name)
    contents_df = import_data(task_list)
    corpus_df = preprocessing(contents_df)
    corpus_df.to_csv("../matrix/"+ contents_name +"_raw.csv", index=False)

    stopwords = import_stopword()
    for add_stop in str(input('Add stop words, split white space : ')).split():
        stopwords.append(add_stop)

    # corpus_df = include_words(corpus_df) #customizinig for text filtering
    # corpus_df = exclude_words(corpus_df)

    min_df = 10 # minimum document setting, change by corpus size
    save_pos_df(corpus_df)

    count_word_table = extract_count_table(pd.read_csv('../matrix/'+ contents_name +'_count_tdm.csv'))
    count_word_table.to_csv('../results/'+ contents_name +'_word_cnt.csv', index = False)
    print('Save Document-term matrix')