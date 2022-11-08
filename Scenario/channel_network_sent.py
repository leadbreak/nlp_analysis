# channel 별 단어 network table 구축
# term-document matrix 에서 channel column merging
# channel 별로 matrix split 후 동일 작업 반복 진행
# 전체 단어에 대한 network table과 sentiment count table return

import pandas as pd
from Theme import import_db, preprocessing, keyword_chart_test, extract_sentiment

def get_channel_column(contents_name):
    task_list = import_db.get_task_list(contents_name)
    corpus_df = import_db.import_channel_data(task_list)
    tmp_df = preprocessing.preprocessing(corpus_df)
    return tmp_df

def split_matrix_channel(channel, matrix):
    split_matrix = matrix.loc[matrix['channel'] == channel, :]
    return split_matrix

def channel_keyword(corpus_df, matrix, center_node): #분할된 matrix를 받아서 network table return
    matrix = matrix.iloc[:,:-1]
    result_df = keyword_chart_test.importing_df(matrix, 10)
    networkdf = keyword_chart_test.networktable2(result_df, matrix, corpus_df, center_node, min_df=10, related_threshold=.5, second_dep = 7)
    return networkdf

def channel_sentiment(corpus_df ,matrix):
    matrix = matrix.iloc[:, :-1]
    sent_dict = extract_sentiment.import_sentdic()
    positive_tdm, negative_tdm = extract_sentiment.voc_sent(matrix, sent_dict)
    posworddf, negworddf = extract_sentiment.sentiment_df(corpus_df, matrix, positive_tdm, negative_tdm)
    sentidf = posworddf.append(negworddf)
    return sentidf

if __name__ == '__main__':
    center_node = "브라운더스트"
    channel_df = get_channel_column(center_node)
    cnt_tdm = pd.read_pickle('../matrix/'+ center_node + '_count_tdm.pkl')
    print(channel_df.shape,cnt_tdm.shape)

    cnt_tdm['channel'] = channel_df['channel'].values # channel list
    print(cnt_tdm['channel'].value_counts())

    channels = list(channel_df['channel'].unique())

    for ch in channels:
        print(ch)
        split_matrix = split_matrix_channel(ch,cnt_tdm).reset_index(drop=True)
        channel_corpus = channel_df.loc[channel_df['channel'] == ch, :].reset_index(drop=True)

        channel_network = channel_keyword(corpus_df = channel_corpus, matrix = split_matrix, center_node= center_node)
        channel_senti = channel_sentiment(corpus_df = channel_corpus, matrix = split_matrix)

        channel_network.to_csv('../results/브라운더스트_Scenario_'+ ch +'_network.csv', index= False)
        channel_senti.to_csv('../results/브라운더스트_Scenario_' + ch + '_sentiment.csv', index=False)