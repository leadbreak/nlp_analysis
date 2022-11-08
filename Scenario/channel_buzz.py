# 채널별 문서 분포 ratio
# DB 에서 channel column을 포함한 table을 받아야 함

from Theme import import_db
import pandas as pd

def channel_ratio(corpus_df): #채널별 문서 aggregate count
    ratio_df = corpus_df.groupby(['channel'])['user_text'].count().reset_index()
    ratio_df.columns = ['channel', 'count']
    return  ratio_df

def channel_trend(corpus_df):
    corpus_df['date'] = pd.to_datetime(corpus_df['date'], utc =True)
    trend_channel = corpus_df.groupby(corpus_df['date'].dt.date)['channel'].value_counts().unstack().fillna(0).reset_index()
    return trend_channel

if __name__ == "__main__":
    task_list = import_db.get_task_list('브라운더스트')
    corpus_df = import_db.import_channel_data(task_list)
    ratio_df = channel_ratio(corpus_df)
    print(ratio_df)
    trend_ch = channel_trend(corpus_df)
    print(trend_ch)

    ratio_df.to_csv('../results/브라운더스트_Scenario_channel_ratio.csv', index = False)
    trend_ch.to_csv("../results/브라운더스트_Scenario_channel_trend.csv", index = False)