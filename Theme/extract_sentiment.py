import numpy as np
import pandas as pd
import collections
import time
from Theme.extract_rawtext import easy_extraction

#시각화 packages
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import font_manager, rc
import plotly.graph_objects as go
import squarify

font_name = font_manager.FontProperties(fname="C:\\Windows\\Fonts\\malgun.ttf").get_name()
rc('font', family=font_name)


def import_sentdic():
    print('Import sentiment lexicon')
    sent_dict = pd.read_csv('../Sentiment_dict/SentiWord_Dict.txt', sep= '\t') #감성어 사전
    # 사전에 미리 지정된 감성 점수가 아닌 긍/부정/중립으로 label로 다시 정의
    sent_dict['label_score'] = np.where(sent_dict.score < 0, -1, 0)
    sent_dict.loc[sent_dict.score > 0, 'label_score'] = 1

    return sent_dict


def voc_sent(review_pos, sent_dict):
    # 사전 내 감성 단어와 dtm 내 단어를 mapping 시켜 긍정 단어 와 부정 단어만 포함된 dataframe을 만든 후 Return
    positive_word = sent_dict.loc[sent_dict['label_score']==1,'word']
    negative_word = sent_dict.loc[sent_dict['label_score']==-1, 'word']

    positive_tdm = review_pos.loc[:,review_pos.columns.isin(positive_word)].reset_index(drop=True)
    negative_tdm = review_pos.loc[:,review_pos.columns.isin(negative_word)].reset_index(drop=True)

    return positive_tdm, negative_tdm

def sentiment_df(corpus_df, cnt_tdm, positive_tdm, negative_tdm):
    # 각각의 dataframe의 column 방향 summation
    # pos_words, count / neg_words, count column을 가지는 단어 합계 테이블 추출
    # 각 단어별로 대표 문서를 가지는 documents column 추가

    print("Extract positive / negative word count table ")
    posworddf = positive_tdm.sum(axis=0).sort_values(ascending=False).reset_index()
    posworddf.columns = ['pos_words', 'count']

    negworddf = negative_tdm.sum(axis=0).sort_values(ascending=False).reset_index()
    negworddf.columns = ['neg_words', 'count']

    documents = []
    for word in posworddf['pos_words'].values:
        word = word.split()
        ex_doc = easy_extraction(corpus_df, cnt_tdm, word)
        documents.append(ex_doc)
    posworddf['documents'] = documents

    documents = []
    for word in negworddf['neg_words'].values:
        word = word.split()
        ex_doc = easy_extraction(corpus_df, cnt_tdm, word)
        documents.append(ex_doc)
    negworddf['documents'] = documents

    return posworddf, negworddf


def total_sent_viz(worddf, wordnum):
    plt.figure(figsize=(12, 12))
    plt.rc('font', size=16)
    matplotlib.rcParams['text.color'] = 'black'
    my_values = worddf.iloc[:wordnum + 1, 1]  # 상위 count 30개의 단어 추출
    cmap = matplotlib.cm.Greens
    mini = min(my_values)
    maxi = max(my_values)
    norm = matplotlib.colors.Normalize(vmin=mini, vmax=maxi)
    colors = [cmap(norm(value)) for value in my_values]
    squarify.plot(sizes=worddf.iloc[:wordnum, 1], label=worddf.iloc[:wordnum, 0], alpha=.9, color=colors)
    plt.axis('off')
    plt.show()


def viz_pos(posworddf, wordnum):
    #긍정어 시각화
    plt.figure(figsize = (12,12))
    plt.rc('font', size=16)
    matplotlib.rcParams['text.color'] = 'black'
    my_values = posworddf.iloc[:wordnum+1, 1] #상위 count 30개의 단어 추출
    cmap = matplotlib.cm.Blues
    mini=min(my_values)
    maxi=max(my_values)
    norm = matplotlib.colors.Normalize(vmin=mini, vmax=maxi)
    colors = [cmap(norm(value)) for value in my_values]
    squarify.plot(sizes = posworddf.iloc[:wordnum, 1], label = posworddf.iloc[:wordnum,0], alpha=.9 , color=colors )
    plt.axis('off')
    plt.show()

def viz_neg(negworddf,wordnum):
    # 부정어 시각화
    plt.figure(figsize = (12,12))
    plt.rc('font', size=16)
    my_values = negworddf.iloc[:wordnum+1, 1] #상위 count 30개의 단어 추출
    cmap = matplotlib.cm.Reds
    mini=min(my_values)
    maxi=max(my_values)
    norm = matplotlib.colors.Normalize(vmin=mini, vmax=maxi)
    colors = [cmap(norm(value)) for value in my_values]
    squarify.plot(sizes = negworddf.iloc[:wordnum, 1], label = negworddf.iloc[:wordnum,0], alpha=.7 , color=colors )
    plt.axis('off')
    plt.show()

def posneg_df(posworddf, negworddf):
    posworddf.loc[:,'label'] = 'positive'
    negworddf.loc[:,'label'] = 'negative'

    posworddf.columns = ['word', 'count', 'documents', 'label']
    negworddf.columns = ['word', 'count', 'documents', 'label']
    return posworddf.append(negworddf)


def sentiment_sunburst(sentiment_df):
    node_list = list(sentiment_df['word'])
    node_list.append('positive')
    node_list.append('negative')

    label_list = list(sentiment_df['label'])
    label_list.append('')
    label_list.append('')

    valist = list(sentiment_df['count'])
    positive_sum = sentiment_df.loc[sentiment_df['label'] == 'positive', 'count'].sum()
    negative_sum = sentiment_df.loc[sentiment_df['label'] == 'negative', 'count'].sum()

    valist.append(positive_sum)
    valist.append(negative_sum)

    fig = go.Figure()
    fig.add_trace(go.Sunburst(
        ids=node_list,
        labels=node_list,
        parents=label_list,
        domain=dict(column=1),
        values=valist,
        branchvalues="total",
        maxdepth=2))
    fig.update_layout(
        margin=dict(t=0, l=0, r=0, b=0),
        font=dict(
            size=20
        )
    )

    if positive_sum >= negative_sum:
        fig.update_layout(sunburstcolorway=["royalblue", "Indianred"])
    else:
        fig.update_layout(sunburstcolorway=["Indianred", "royalblue"])
    fig.show()

def sentiment_treemap(sentiment_df):
    node_list = list(sentiment_df['word'])
    node_list.append('positive')
    node_list.append('negative')

    label_list = list(sentiment_df['label'])
    label_list.append('')
    label_list.append('')

    valist = list(sentiment_df['count'])
    positive_sum = sentiment_df.loc[sentiment_df['label'] == 'positive', 'count'].sum()
    negative_sum = sentiment_df.loc[sentiment_df['label'] == 'negative', 'count'].sum()

    valist.append(positive_sum)
    valist.append(negative_sum)

    fig = go.Figure()
    fig.add_trace(go.Treemap(
        labels=node_list,
        parents=label_list,
        domain=dict(column=1),
        values=valist,
        branchvalues="total"
    )
    )

    fig.update_layout(
        margin=dict(t=0, l=0, r=0, b=0),
        font=dict(
            size=18
        )
    )

    if positive_sum >= negative_sum:
        fig.update_layout(treemapcolorway = ["royalblue", "Indianred"])
    else:
        fig.update_layout(treemapcolorway = ["Indianred", "royalblue"])
    fig.show()

    fig.show()

if __name__ == "__main__":
    start_time = time.time()
    sent_dict = import_sentdic() #감성 사전 import
    contents_name = "외신"

    corpus_df = pd.read_csv('../matrix/'+ contents_name +"_raw.csv")
    review_pos = pd.read_pickle('../matrix/'+ contents_name + '_count_tdm.pkl')  # term-document matrix
    del review_pos['걸리다']

    positive_tdm, negative_tdm = voc_sent(review_pos, sent_dict)
    posworddf, negworddf = sentiment_df(corpus_df, review_pos, positive_tdm, negative_tdm) #긍정 단어, 부정 단어 count table

    posworddf.to_csv('../results/'+contents_name+'_positive.csv')
    negworddf.to_csv('../results/' + contents_name + '_negative.csv')

    sentimentwords = posneg_df(posworddf.iloc[:10,:], negworddf.iloc[:10,:]) #각각 top n위 까지 지정해 시각화
    sentiment_sunburst(sentimentwords)
    # #sentiment_treemap(sentimentwords)
    # print(time.time() - start_time , ' sec spent for extracting sentiment word')