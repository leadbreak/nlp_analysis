# document-term matrix 에서 특정 word set을 입력받으면 해당 단어의 time series count table을 return
# matrix를 만들기 전에 전처리된 문서 집합 : corpus
# matrix : document-term matrix
# start_date, end_date : 지정 날짜
# word : 리스트 형태의 단어
# default setting
# 최근 1달 , 4주 동안의 키워드 순위 30위까지
# Frequency 포함
# 4개의 컬럼 내에서 30개의 단어가 frequency 순위대로 포함되야 함

import pandas as pd
import datetime

def get_week_of_month(df_line):
    year = df_line.year
    month = df_line.month
    day = df_line.day

    d = datetime.datetime(year, month, day)
    return (d.day - 1) // 7 + 1

def word_timeseries(corpus, matrix, week_num = 13, word_num=20): #week num : 기간 설정, word_num : 단어 수
    count_tdm_date = matrix.copy()
    count_tdm_date['date'] = corpus['date']
    count_tdm_date['date'] = pd.to_datetime(count_tdm_date['date'])

    del corpus, matrix
    count_tdm_date = count_tdm_date.sort_values(by='date', ascending=False).reset_index(drop=True)
    count_tdm_date['weeknum'] = count_tdm_date.loc[:, 'date'].apply(get_week_of_month)
    count_tdm_date['month'] = count_tdm_date['date'].dt.strftime('%Y-%m')
    count_tdm_date['month_week'] = count_tdm_date['month'].astype('str') + '-' + count_tdm_date['weeknum'].astype('str')

    del count_tdm_date['date'], count_tdm_date['month'], count_tdm_date['weeknum']

    tmp_dict = {}
    for k, group in count_tdm_date.groupby(['month_week']):
        count_df = group.iloc[:, :-1].sum(axis=0).reset_index()
        count_df.columns = ['word', 'freq']
        # print(count_df)
        tmp_dict[k] = list(zip(count_df.sort_values(by='freq', ascending=False).iloc[:word_num, 0].values,
                               count_df.sort_values(by='freq', ascending=False).iloc[:word_num, 1].values))

    df_dict = {}
    for week in count_tdm_date['month_week'].unique()[:week_num]:
        df_dict[week] = tmp_dict[week]
    df = pd.DataFrame(df_dict)
    return df
    # weekly agg sum

def keyword_trend(corpus, matrix, week_num = 12, word_num=10): #week num : 기간 설정, word_num : 단어 수
    count_tdm_date = matrix.copy()
    count_tdm_date['date'] = corpus['date']
    count_tdm_date['date'] = pd.to_datetime(count_tdm_date['date'])

    del corpus, matrix
    count_tdm_date = count_tdm_date.sort_values(by='date', ascending=False).reset_index(drop=True)
    count_tdm_date['weeknum'] = count_tdm_date.loc[:, 'date'].apply(get_week_of_month)
    count_tdm_date['month'] = count_tdm_date['date'].dt.strftime('%Y-%m')
    count_tdm_date['month_week'] = count_tdm_date['month'].astype('str') + '-' + count_tdm_date['weeknum'].astype('str')
    del count_tdm_date['weeknum'], count_tdm_date['month']

    tdm_filtered = count_tdm_date.loc[count_tdm_date['month_week'].isin(count_tdm_date['month_week'].unique()[:week_num]), :]
    keywords = list(tdm_filtered.iloc[:, :-1].sum(axis=0).sort_values(ascending=False)[:word_num].index)

    keyword_trends = tdm_filtered.groupby(['month_week'])[keywords].sum().sort_index(ascending=True)
    keyword_trends_filtered = keyword_trends.div(keyword_trends.sum(axis=1), axis=0) * 100
    return keyword_trends_filtered


if __name__ == "__main__":
    contents_name = "브라운더스트"
    corpus = pd.read_csv("../matrix/"+contents_name+"_raw.csv")
    tdm = pd.read_pickle("../matrix/"+contents_name+"_count_tdm.pkl")

    keyword_rank = word_timeseries(corpus, tdm, week_num = 13, word_num=20)
    print(keyword_rank.head())
    keyword_rank.to_csv('../results/브라운더스트_weekly_keyword.csv', index = False)
    keywordtrend = keyword_trend(corpus, tdm, week_num=13, word_num=5)
    print(keywordtrend.head())
    keywordtrend.to_csv('../results/브라운더스트_keyword_trend.csv', index= False)