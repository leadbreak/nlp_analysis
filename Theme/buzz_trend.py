"""
요일별, 시간대별 버즈량 table
요일 index ~ Monday=0, Sunday=6.
시간대는 data frame 의 date column에서 Timeline 형태이면 aggregate
"""

import pandas as pd
from Theme import import_multiple_db

def agg_date(df,set_start, set_end): # 날짜별로 문서량 count
    df['date'] = pd.to_datetime(df['date'])
    df = df.loc[(df['date']>= set_start)&(df['date'] <= set_end), :]
    daily_agg = df.groupby(['date'])['user_name'].count().reset_index()
    daily_agg.columns = ['date', 'amount_of_buzz']
    return daily_agg

def competitive_agg_date(df_list, contents_list):
    #경쟁 콘텐츠 문서집합까지 포함해 날짜 별 콘텐츠별 버즈량 table 도출
    #column name 이 콘텐츠 이름들로 구성될 수 있도록 날짜 기준으로 merging

    aggdf_list = []
    for i,df in enumerate(df_list):
        df['date'] = pd.to_datetime(df['date'])
        daily_agg = df.groupby(df['date'].dt.date)['user_name'].count().reset_index()
        daily_agg.columns = ['date', str(contents_list[i])]
        aggdf_list.append(daily_agg)

    daily_total_df = aggdf_list[0]
    for d in aggdf_list[1:]:
        daily_total_df = pd.merge(daily_total_df, d, how = 'left', on = 'date')

    daily_total_df['comp_avg'] = daily_total_df.iloc[:,2:].mean(axis = 1)
    daily_total_df = daily_total_df.fillna(0)
    return daily_total_df

def get_rank_df(df): #
    tmp_df = df.copy()
    del tmp_df['comp_avg']
    #tmp_df = tmp_df.set_index('date')
    daily_rank = tmp_df.iloc[:,1:].rank(1, ascending=False, method='max') # chart옵션에 따라 ascending 조정
    return daily_rank

def agg_time(df): # 시간대별로 문서량 count
    df['date'] = pd.to_datetime(df['date'])
    time_agg = df.groupby(df['date'].dt.hour)['user_name'].count().reset_index()
    time_agg.columns = ['time', 'amount_of_buzz']
    return time_agg

def agg_dayofweek(df): # 요일별로 문서량 count
    df['date'] = pd.to_datetime(df['date'])
    dayof_agg = df.groupby(df['date'].dt.dayofweek)['user_name'].count().reset_index()
    dayof_agg.columns = ['day_of_week', 'amount_of_buzz']
    return dayof_agg

if __name__ == '__main__':
    contents_list = ['브라운더스트', '소녀전선', '랑그릿사', '데일리판타지', '붕괴3rd', '파이널블레이드']

    df_list = import_multiple_db.get_df_list(contents_list)
    df = df_list[0] #contents_list 에서 첫번째 콘텐츠의 corpus data
    daily_total_df = competitive_agg_date(df_list, contents_list)
    #daily_rank_df = get_rank_df(daily_total_df)
    #daily_rank_df.to_csv('buzz_ranking_time.csv') #save table
    daily_total_df.to_csv('../results/Buzz_trend.csv', index = False) #save table
    #print(df.tail())

