# 전체 문서 상에서 긍정 단어 / 부정 단어의 list 및 count를 추출
# 긍정 단어 / 부정 단어의 리스트를 받아 matrix에서 flitering 진행 후 network table 구축

import pandas as pd
from Theme import extract_sentiment,keyword_chart_test

# importing_df(cnt_tdm, first_dep = 10)
# networktable2(result_df, cnt_tdm, corpus_df, center_node,  min_df=10, related_threshold=.5, second_dep = 7)
# voc_sent(review_pos, sent_dict) -> sentiment_df(corpus_df, cnt_tdm, positive_tdm, negative_tdm)

def network_df(cnt_tdm, corpus_df, centerword):
    result_df = keyword_chart_test.importing_df(cnt_tdm, 10)
    network_df = keyword_chart_test.networktable2(result_df, cnt_tdm, corpus_df, centerword,  min_df=10, related_threshold=.5, second_dep = 7)
    return network_df

def sentimentword_df(cnt_tdm, corpus_df, sent_dict):
    positive_tdm, negative_tdm = extract_sentiment.voc_sent(cnt_tdm, sent_dict)
    posworddf, negworddf = extract_sentiment.sentiment_df(corpus_df, cnt_tdm, positive_tdm, negative_tdm)
    posworddf.loc[:, 'label'] = 'positive'
    negworddf.loc[:, 'label'] = 'negative'
    posworddf.columns = ['word', 'count', 'documents', 'label']
    negworddf.columns = ['word', 'count', 'documents', 'label']
    sentiword_df = posworddf.append(negworddf)
    sentiword_df = sentiword_df.loc[sentiword_df['count']>0, :]
    return sentiword_df

if __name__ == "__main__":
    cnt_tdm = pd.read_pickle('../matrix/브라운더스트_count_tdm.pkl')
    corpus_df = pd.read_csv('../matrix/브라운더스트_raw_sentlabel.csv')
    # 0 : positive , 1 : negative , 2 : neutral
    cnt_tdm['sentiment_label'] = corpus_df['sentiment_label'].values
    sentiment_dict = extract_sentiment.import_sentdic()

    positive_corpus = corpus_df.loc[corpus_df['sentiment_label'] == 0, :].reset_index(drop=True)
    negative_corpus = corpus_df.loc[corpus_df['sentiment_label'] == 1, :].reset_index(drop=True)
    neutral_corpus = corpus_df.loc[corpus_df['sentiment_label'] == 2, :].reset_index(drop=True)

    center_node = '브라운더스트'

    # positive
    positive_tdm = cnt_tdm.loc[cnt_tdm['sentiment_label'] == 0, :].reset_index(drop=True)
    del positive_tdm['sentiment_label']
    positive_network = network_df(cnt_tdm= positive_tdm, corpus_df= positive_corpus, centerword=center_node)
    positive_sentiment = sentimentword_df(cnt_tdm= positive_tdm, corpus_df= positive_corpus, sent_dict=sentiment_dict)

    positive_network.to_csv("../results/브라운더스트_Scenario_voc_positive_network.csv", index = False)
    positive_sentiment.to_csv("../results/브라운더스트_Scenario_voc_positive_sentiword.csv", index = False)

    # negative
    negative_tdm = cnt_tdm.loc[cnt_tdm['sentiment_label'] == 1, :].reset_index(drop=True)
    del negative_tdm ['sentiment_label']
    negative_network = network_df(cnt_tdm=negative_tdm , corpus_df= negative_corpus, centerword = center_node)
    negative_sentiment = sentimentword_df(cnt_tdm=negative_tdm , corpus_df= negative_corpus, sent_dict = sentiment_dict)

    negative_network.to_csv("../results/브라운더스트_Scenario_voc_negative_network.csv", index=False)
    negative_sentiment.to_csv("../results/브라운더스트_Scenario_voc_negative_sentiword.csv", index=False)

    # neutral
    neutral_tdm = cnt_tdm.loc[cnt_tdm['sentiment_label'] == 2, :].reset_index(drop=True)
    del neutral_tdm['sentiment_label']
    neutral_network = network_df(cnt_tdm=neutral_tdm, corpus_df=neutral_corpus, centerword=center_node)
    neutral_sentiment = sentimentword_df(cnt_tdm=neutral_tdm, corpus_df=neutral_corpus, sent_dict=sentiment_dict)

    neutral_network.to_csv("../results/브라운더스트_Scenario_voc_neutral_network.csv", index=False)
    neutral_sentiment.to_csv("../results/브라운더스트_Scenario_voc_neutral_sentiword.csv", index=False)
