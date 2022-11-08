#연관 단어 시각화
#document-term matrix (count 기반)
from Theme import extract_sentiment
from Theme.extract_rawtext import easy_extraction
import pandas as pd
import time, os

#시각화 packages
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib import font_manager, rc

font_name = font_manager.FontProperties(fname="C:\\Windows\\Fonts\\malgun.ttf").get_name() # 시각화시 한글 설정
rc('font', family=font_name)

def importing_df(cnt_tdm, result_num):
    cnt_keyword = cnt_tdm.sum(axis=0).sort_values(ascending = False)
    result_df = pd.DataFrame(cnt_keyword[:result_num].reset_index())
    result_df.columns = ['keyword', 'cnt']
    return result_df

# first depth 시각화를 위한 network data table 구성

def networktable(corpus_df, result_df, cnt_tdm, centerword):
    center_node = []
    for i in range(len(result_df['keyword'])):
        center_node.append(centerword) #중심에 있을 contents 이름

    # network 관계를 구성할 table 지정
    network_df = pd.DataFrame({'from': center_node, 'to':result_df['keyword']})
    network_df['depth'] = 1
    network_df = network_df.append({'from':centerword, 'to':centerword, 'depth':0}, ignore_index=True)
    network_df = network_df.sort_values(by='depth')

    #만들어진 network 관계 dataframe에서 depth 를 추가하는 과정
    lev1_list = list(network_df.loc[network_df['depth'] == 1, 'to'])

    for depone_keyword in lev1_list:
        cnt_keyword = cnt_tdm.loc[cnt_tdm[depone_keyword] > 0, :]
        cnt_keyword = cnt_keyword.loc[:,~cnt_keyword.columns.isin(network_df['to'])].sum(axis=0).sort_values(ascending = False)
        norm_df = (cnt_keyword - cnt_keyword.min()) / (cnt_keyword.max() - cnt_keyword.min())
        related_keyword = list(norm_df[norm_df > 0.7].index) # setting threshold
        if len(related_keyword)>=5: # 최대 5개의 2depth 단어까지 허용
            related_keyword = related_keyword[:4]
        for word in related_keyword:
            network_df = network_df.append({'from':depone_keyword, 'to': word, 'depth':2}, ignore_index=True)

    result_list = list()
    first_node_word = list(network_df.loc[network_df['depth'] == 1, 'to'].values)[:3]
    first_text_list = easy_extraction(corpus_df, cnt_tdm, first_node_word)
    result_list.append(first_text_list)
    one_depth_words = network_df.loc[network_df['depth'] == 1, 'to'].values

    for word in one_depth_words:
        word = word.split()
        text_list = easy_extraction(corpus_df, cnt_tdm, word)
        result_list.append(text_list)

    tmp_df = network_df.loc[network_df['depth'] == 2, :]
    two_depth_words = (tmp_df['from'] + " " + tmp_df['to']).values
    for word in two_depth_words:
        word = word.split()
        text_list = easy_extraction(corpus_df, cnt_tdm, word)
        result_list.append(text_list)

    network_df['documents'] = result_list

    return network_df

def sentiment_network(corpus_df, cnt_tdm, result_num, centerword):
    sentiment_dict = extract_sentiment.import_sentdic()
    columns = [word for word in cnt_tdm.columns if word in sentiment_dict['word'].values]
    filtered_cnt_tdm = cnt_tdm.loc[:, columns]
    result_df = importing_df(filtered_cnt_tdm, result_num)
    network_df = networktable(corpus_df, result_df, filtered_cnt_tdm, centerword)
    return network_df


# 2-depth network
def wordnetwork(network_df):
    carac = pd.DataFrame({'ID':network_df['to'], 'depth': list(network_df['depth'])})
    # Build graph
    G=nx.from_pandas_edgelist(network_df, 'from', 'to')
    d = nx.degree(G)
    carac= carac.set_index('ID')
    carac=carac.reindex(G.nodes())
    carac['depth']= pd.Categorical(carac['depth'])

    plt.figure(figsize=(15,12))

    pos = nx.spring_layout(G,k=9.,iterations=2500, seed=1)
    nx.draw(G, pos, with_labels = True,  font_family=font_name,
            node_size=[9000 - (value*3000) for value in network_df['depth']],
            font_size=15,
            font_color ='w',
            node_shape='o',
            linewidths = 5.,
            node_color=carac['depth'].cat.codes,
            width=1.,
            font_weight='bold',
            style='dashed',
            alpha=0.97,
            cmap=plt.cm.Set1)
    plt.show()


if __name__ == "__main__":
    cnt_tdm = pd.read_pickle('../matrix/Exclusive_pants_count_tdm.pkl')  # 파일 형태로 불러옴 (임시)
    start_time = time.time()
    center_node = "Exclusive_pants"
    corpus_df = pd.read_csv("../matrix/Exclusive_pants_raw.csv")
    print(corpus_df.shape)
    networkdf = networktable(corpus_df, importing_df(cnt_tdm, 10), cnt_tdm, center_node)  # keyword network table
    # networkdf.to_csv('../results/wconcept_fr_network_table.csv', index = False) # 원문까지 포함한 network table

    print(networkdf)
    # sentiment_df = sentiment_network(corpus_df, cnt_tdm, 10, center_node)
    # sentiment_df.to_csv('../matrix/브라운더스트_sentnet_table.csv', index= False) # 원문까지 포함한 감성단어 network table
    # print(sentiment_df)
    wordnetwork(networkdf)  # 네트워크 시각화
    print(time.time() - start_time, ' sec spent for viz')
