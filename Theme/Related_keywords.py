# 도출된 matrix 를 기반으로 특정 단어와 연관도가 높은 단어 리스틀 return
#1) 특정 단어가 포함된 문서만 filtering
#2) 1번 문서집합에서 포함된 i번째 단어에 대해 (filtering한 문서 집합에서 단어 출현 수 / 전체 문서 집합 상에서 해당 단어의 출현 수) 을 계산
#  이 때, 전체 Frequency 자체가 낮은 경우에는 분모에 해당하는 출현 수가 적기 때문에 연관도가 적더라도 score값이 높아져 순위가 올라갈 수 있으므로 최소 출현 횟수를 제한해주는 파라미터를 설정해줘야 함
#3) score가 높은 순으로 sorting 후 N 개 단어 추출

import pandas as pd

def related_keyword(matrix, word, min_df, num): # Matrix, 지정 단어, 최소 출현수, 결과 도출 단어 수
    print('전체 matrix shape : ', matrix.shape)
    total_words_sum = matrix.sum(axis=0)
    min_words = total_words_sum[total_words_sum > min_df].index

    filtering_tdm = matrix.loc[matrix[word] >= 1, min_words]
    print('filtered matrix shape : ', filtering_tdm.shape)

    filter_words_sum = filtering_tdm.sum(axis=0)

    score_df = filter_words_sum / count_tdm.loc[:, min_words].sum(axis=0)
    score_df = pd.DataFrame(score_df.reset_index())
    score_df.columns = ['word', 'score']
    score_df = score_df.sort_values(by='score', ascending=False)

    return score_df.iloc[1:num,:]

if __name__ == "__main__":
    count_tdm = pd.read_csv('../matrix/브라운더스트_count_tdm.csv')
    keyword = "재미"
    print(related_keyword(count_tdm,keyword,20,20))
