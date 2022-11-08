# 분석 contents의 document-term matrix 에 날짜 column을 merging, 사용자가 지정한 날짜 기준으로 matrix를 split
# 콘텐츠이름_날짜_after/before_count_tdm.csv 로 각각 저장

import pandas as pd
from Theme import import_db, preprocessing


def split_matrix(contents_name, setting_date, start_date):
    task_list = import_db.get_task_list(contents_name)
    corpus_df = import_db.import_data(task_list)
    print('파일을 불러옵니다.', '파일 크기 : ', corpus_df.shape)
    corpus_df = preprocessing.preprocessing(corpus_df)
    corpus_df['date'] = pd.to_datetime(corpus_df['date'])
    cnt_tdm = pd.read_pickle('../matrix/'+contents_name+'_count_tdm.pkl')
    print('Matrix shape',cnt_tdm.shape)
    cnt_tdm['date'] = corpus_df['date'].values
    cnt_tdm['date'] = pd.to_datetime(cnt_tdm['date'])

    before_corpus = corpus_df.loc[((corpus_df['date'] > start_date)&(corpus_df['date'] < setting_date)), :]
    after_corpus = corpus_df.loc[corpus_df['date'] >= setting_date, :]

    before_tdm = cnt_tdm.loc[((cnt_tdm['date'] > start_date)&(cnt_tdm['date'] < setting_date)), :]
    after_tdm = cnt_tdm.loc[cnt_tdm['date'] >= setting_date, :]
    del before_tdm['date']
    del after_tdm['date']

    print('# of documents before campaign', before_tdm.shape[0])
    print('# of documents after campaign', after_tdm.shape[0])

    before_tdm.to_pickle('../matrix/before_'+ contents_name +'_count_tdm.pkl')
    before_corpus.to_csv('../matrix/before_'+ contents_name +'_corpus_df.csv', index = False)
    after_tdm.to_pickle('../matrix/after_'+ contents_name +'_count_tdm.pkl')
    after_corpus.to_csv('../matrix/after_' + contents_name + '_corpus_df.csv', index=False)


if __name__ == "__main__":
    contents_name = "브라운더스트"
    setting_date = '2019-07-01'
    start_date = '2019-01-01'
    split_matrix(contents_name = contents_name, setting_date = setting_date, start_date=start_date)
    print("Split matrix based on campaign date")