# 특정 날짜 기준으로 분할 된 matrix 2개를 load해 각각에 대해 연관어/감성어 network table을 도출
# 원문 추출을 위해 기존의 corpus dataframe을  지정 날짜 기준으로 분할해 함수 parameter로 넣어줌

import pandas as pd
from Theme import keyword_chart_test

def split_networktable(before_corpus_df, after_corpus_df, before_tdm, after_tdm, centernode, min_df=10, related_threshold=.5, second_dep = 7): #캠페인 기간 전의 matrix와 기간 후의 matrix를 입력으로 받아 network table 을 각각 return

    before_df = keyword_chart_test.importing_df(before_tdm, 10)

    # networktable2(result_df, cnt_tdm, corpus_df, centerword, min_df, related_threshold, second_dep):
    before_network = keyword_chart_test.networktable2(before_df, before_tdm, before_corpus_df, centernode, min_df=min_df, related_threshold=related_threshold, second_dep = second_dep)

    after_df = keyword_chart_test.importing_df(after_tdm, 10)
    after_network = keyword_chart_test.networktable2(after_df, after_tdm, after_corpus_df, centernode,  min_df=min_df, related_threshold=related_threshold, second_dep = second_dep)

    return before_network, after_network

if __name__ =="__main__":
    contents_name = "브라운더스트"

    before_corpus_df = pd.read_csv('../matrix/before_'+ contents_name + "_corpus_df.csv")
    after_corpus_df = pd.read_csv('../matrix/after_' + contents_name + "_corpus_df.csv")

    before_tdm = pd.read_pickle('../matrix/before_'+ contents_name + "_count_tdm.pkl")
    after_tdm = pd.read_pickle('../matrix/after_'+ contents_name + "_count_tdm.pkl")

    before_network, after_network = split_networktable(before_corpus_df, after_corpus_df, before_tdm, after_tdm, contents_name) #각각 save
    print(before_network.head())
    print('\n')
    print(after_network.head())

    before_network.to_csv("../results/브라운더스트_Scenario_camp_beforenet.csv", index = False)
    after_network.to_csv('../results/브라운더스트_Scenario_camp_afternet.csv', index = False)
