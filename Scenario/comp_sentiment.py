# 경쟁 contents 한개를 추가해 전체 감성 단어 count table 2개를 return
# 본 브랜드와 경쟁사 브랜드에 해당하는 모든 corpus file 과 matrix를 저장한 상태를 가정함

from Theme.extract_sentiment import import_sentdic, voc_sent, sentiment_df, posneg_df
import pandas as pd
import os


def extract_sentiment_tables(corpus_df1, corpus_df2, df1, df2, word_num):
    # word_num 표시할 단어의 수, 긍정 부정 각각 적용
    sentdict = import_sentdic()

    positive_tdm1, negative_tdm1 = voc_sent(df1, sentdict)
    posworddf1, negworddf1 = sentiment_df(corpus_df1, df1, positive_tdm1, negative_tdm1)
    sentimentwords1 = posneg_df(posworddf1.iloc[:word_num, :], negworddf1.iloc[:word_num, :])

    positive_tdm2, negative_tdm2 = voc_sent(df2, sentdict)
    posworddf2, negworddf2 = sentiment_df(corpus_df2, df2, positive_tdm2, negative_tdm2)
    sentimentwords2 = posneg_df(posworddf2.iloc[:word_num, :], negworddf2.iloc[:word_num, :])

    return sentimentwords1, sentimentwords2

if __name__ == "__main__":
    contents1 = "브라운더스트"
    contents2 = "랑그릿사"

    if os.path.isfile('../matrix/' + contents1 + '_count_tdm.pkl') and os.path.isfile(
            '../matrix/' + contents1 + '_raw.csv'):
        corpus_df1 = pd.read_csv('../matrix/' + contents1 + '_raw.csv')
        df1 = pd.read_pickle('../matrix/' + contents1 + '_count_tdm.pkl')
    else:
        print("Cannot find corpus file or matrix")

    if os.path.isfile('../matrix/' + contents2 + '_count_tdm.pkl') and os.path.isfile(
            '../matrix/' + contents2 + '_raw.csv'):
        corpus_df2 = pd.read_csv('../matrix/' + contents2 + '_raw.csv')
        df2 = pd.read_pickle('../matrix/' + contents2 + '_count_tdm.pkl')
    else:
        print("Cannot find corpus file or matrix")


    senti_cnt1, senti_cnt2 = extract_sentiment_tables(corpus_df1, corpus_df2, df1, df2, word_num=10)

    print("브라운더스트 감성 단어 count table")
    print(senti_cnt1)

    print("\n랑그릿사 감성 단어 count table")
    print(senti_cnt2)
    senti_cnt1['contents_name'] = contents1
    senti_cnt2['contents_name'] = contents2
    df = senti_cnt1.append(senti_cnt2)
    df.to_csv("../results/브라운더스트_Scenario_comp_sentiment.csv")