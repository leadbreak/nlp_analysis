# 특정 날짜 기준 전 / 후의 문서량 순위
# 날짜를 입력값으로 받아서 2개의 table 을 return

import pandas as pd
from Theme import import_db, import_multiple_db, buzz_trend

def split_rank(start_date, daily_rank_df): #날짜 설정, 순위 table
    daily_rank_df.index = pd.to_datetime(daily_rank_df.index)
    before_rank_df = daily_rank_df.loc[daily_rank_df.index < start_date, :]
    after_rank_df = daily_rank_df.loc[daily_rank_df.index >= start_date, :]
    return  before_rank_df, after_rank_df

def channel_ratio_change(contents_df, start_date):
    contents_df['date'] = pd.to_datetime(contents_df['date'])
    before_df = contents_df.loc[contents_df['date'] < start_date, :]
    after_df = contents_df.loc[contents_df['date'] >= start_date, :]

    before_ratio = before_df['channel'].value_counts().reset_index()
    before_ratio.columns = ['channel', 'counts']

    after_ratio = after_df['channel'].value_counts().reset_index()
    after_ratio.columns = ['channel', 'counts']

    return before_ratio, after_ratio


if __name__ == "__main__":
    contents_list = ['브라운더스트', '소녀전선', '랑그릿사', '데일리판타지', '붕괴3rd', '파이널블레이드']
    setting_date = '2019-01-01' #setting campaign date

    df_list = import_multiple_db.get_df_list(contents_list)
    daily_total_df = buzz_trend.competitive_agg_date(df_list, contents_list)
    daily_rank_df = buzz_trend.get_rank_df(daily_total_df)

    before_rank_df, after_rank_df = split_rank(setting_date, daily_rank_df)

    task_list = import_db.get_task_list('브라운더스트')
    dataframe = import_db.import_channel_data(task_list)
    print(dataframe.head())
    before_ch_df, after_ch_df = channel_ratio_change(dataframe,setting_date)

    print(before_rank_df.head())
    print(after_rank_df.head())
    print(before_ch_df)
    print(after_ch_df)
