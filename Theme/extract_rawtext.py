# 단어 선택 시 해당 단어를 포함하는 대표 문서를 추출
# 전체 문서 상에서 대표 문서를 뽑는 방법 : word count 기반 , word tf-idf 기반

import pandas as pd
import os
from Theme import import_db, preprocessing


#from Theme import vetorizing_tfidf

def easy_extraction(corpus_df, count_tdm, search_wordlist): #count tdm에서 입력받은 단어리스트에 대해 대표 문서를 추출하는 방법
    try:
        filter_vect = count_tdm.loc[(count_tdm[search_wordlist] > 0).all(axis=1), search_wordlist]
        filter_vect['cnt_sum'] = filter_vect.sum(axis=1)
        filter_vect['norm_score'] = (filter_vect['cnt_sum'] - filter_vect['cnt_sum'].min()) / (filter_vect['cnt_sum'].max() - filter_vect['cnt_sum'].min())
        filter_vect.loc[filter_vect['norm_score'] > .9, 'cnt_sum'] = 1

        corpus_df = pd.merge(corpus_df, filter_vect, how='left', left_index=True, right_index=True)
        corpus_df['user_text'] = corpus_df['user_text'].astype('str')
        corpus_df['text_length'] = corpus_df['user_text'].apply(lambda x: len(x) if len(x) <= 100 else 0)

        corpus_df['filter_score'] = corpus_df['text_length'] * corpus_df['cnt_sum']
        corpus_df = corpus_df.sort_values(by='filter_score', ascending=False)

        text_list = list()
        for text in corpus_df['user_text'][:3]: # 뽑을 원문서 수 조절 가능
            text_list.append(text)

        return text_list
        #return corpus_df['user_text'][:3] #return 할 대표 text 3건
    except KeyError:
        print("해당 단어는 Buzz 상에 없거나 출현 횟수가 너무 낮습니다.")



if __name__ == "__main__":

    if os.path.isfile("../matrix/브라운더스트_raw.csv"):
        corpus_df = pd.read_csv("../matrix/브라운더스트_raw.csv")
    else:
        task_list = import_db.get_task_list('브라운더스트')
        contents_df = import_db.import_data(task_list)
        corpus_df = preprocessing.preprocessing(contents_df)
        corpus_df.to_csv('../matrix/브라운더스트_raw.csv')

    count_tdm = pd.read_csv('../matrix/브라운더스트_count_tdm.csv')



    print(corpus_df.shape)
    print(count_tdm.shape)
    """
    sent_dict = import_sentdic()
    treemap = extract_sent(count_tdm, sent_dict)
    document_df2 = sentiment_documnet(treemap[:5])
    print(document_df2)
    """
    #easy_extraction(corpus_df, count_tdm, search_wordlist)