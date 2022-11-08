# 두개의 콘텐츠를 포함하는 연관어 network table 도출
# 본 브랜드와 경쟁사 브랜드에 해당하는 모든 corpus file 과 matrix를 저장한 상태를 가정함

import pandas as pd
import numpy as np
from Theme.extract_rawtext import easy_extraction
import os
#시각화 packages
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib import font_manager, rc

font_name = font_manager.FontProperties(fname="C:\\Windows\\Fonts\\malgun.ttf").get_name() # 시각화시 한글 설정
rc('font', family=font_name)


def competive_network(corpus_df1, corpus_df2, df1, df2, word_num = 10):
    cnt_keyword1 = df1.sum(axis=0)
    cnt_keyword1 = cnt_keyword1.sort_values(ascending = False)
    result_df = pd.DataFrame(cnt_keyword1[:word_num].reset_index())
    result_df.columns = ['keyword', 'cnt']

    center_node = []
    node_name = str(input("center node name : "))
    for i in range(len(result_df['keyword'])):
        center_node.append(node_name)

    tmpdf = pd.DataFrame({'from': center_node, 'to':result_df['keyword']})
    tmpdf['depth'] = 1
    tmpdf = tmpdf.append({'from':node_name, 'to':node_name, 'depth':0}, ignore_index=True)
    tmpdf = tmpdf.sort_values(by='depth')

    result_list = list()
    first_node_word = list(tmpdf.loc[tmpdf['depth'] == 1, 'to'].values)[:3]
    first_text_list = easy_extraction(corpus_df1, df1, first_node_word)
    result_list.append(first_text_list)
    one_depth_words = tmpdf.loc[tmpdf['depth'] == 1, 'to'].values

    for word in one_depth_words:
        word = word.split()
        text_list = easy_extraction(corpus_df1, df1, word)
        result_list.append(text_list)

    tmpdf['documents'] = result_list


    #경쟁사 게임 network table 구축
    cnt_keyword2 = df2.sum(axis=0)
    cnt_keyword2 = cnt_keyword2.sort_values(ascending = False)
    result_df2 = pd.DataFrame(cnt_keyword2[:word_num].reset_index())
    result_df2.columns = ['keyword', 'cnt']

    center_node2 = []
    node_name2 = str(input("center node name : "))
    for i in range(len(result_df2['keyword'])):
        center_node2.append(node_name2)

    tmpdf2 = pd.DataFrame({'from': center_node2, 'to':result_df2['keyword']})
    tmpdf2['depth'] = 1
    tmpdf2 = tmpdf2.append({'from':node_name2, 'to':node_name2, 'depth':0}, ignore_index=True)
    tmpdf2 = tmpdf2.sort_values(by='depth')

    result_list2 = list()
    first_node_word = list(tmpdf2.loc[tmpdf2['depth'] == 1, 'to'].values)[:3]
    first_text_list = easy_extraction(corpus_df2, df2, first_node_word)
    result_list2.append(first_text_list)
    one_depth_words = tmpdf2.loc[tmpdf2['depth'] == 1, 'to'].values

    for word in one_depth_words:
        word = word.split()
        text_list = easy_extraction(corpus_df2, df2, word)
        result_list2.append(text_list)

    tmpdf2['documents'] = result_list2

    tmpdf = tmpdf.append(tmpdf2)

    return tmpdf

def viz_compnetwork(tmpdf):
    carac = pd.DataFrame({'ID': tmpdf['to'], 'depth': list(tmpdf['depth'])})  # ID: 개별 node, depth: 깊이
    size = np.where(tmpdf['depth'] == 0, 7000, 4000)

    # Build graph
    G = nx.from_pandas_edgelist(tmpdf, 'from', 'to')
    carac = carac.set_index('ID')
    carac = carac[~carac.index.duplicated(keep='last')]
    carac = carac.reindex(G.nodes())

    carac['depth'] = pd.Categorical(carac['depth'])

    # Thus, we cannot give directly the 'myvalue' column to netowrkX, we need to arrange the order!
    plt.figure(figsize=(18, 9))
    pos = nx.spring_layout(G)
    nx.draw(G, with_labels=True,
            font_family=font_name,
            node_size=size,
            font_size=12,
            font_color='w',
            node_shape='o',
            linewidths=12.,
            node_color=carac['depth'].cat.codes,
            width=1.2,
            font_weight='bold',
            style='dashed',
            alpha=0.95,
            cmap=plt.cm.Set1)
    plt.show()

if __name__ == "__main__":
    # change file name
    contents1 = "코로나19"
    contents2 = "총선투표선거"

    if os.path.isfile('../matrix/'+contents1+'_count_tdm.pkl') and os.path.isfile('../matrix/'+contents1+'_raw.csv'):
        corpus_df1 = pd.read_csv('../matrix/'+contents1+'_raw.csv')
        df1 = pd.read_pickle('../matrix/'+contents1+'_count_tdm.pkl')
    else:
        print("Cannot find corpus file or matrix")

    if os.path.isfile('../matrix/'+contents2+'_count_tdm.pkl') and os.path.isfile('../matrix/'+contents2+'_raw.csv'):
        corpus_df2 = pd.read_csv('../matrix/'+contents2+'_raw.csv')
        df2 = pd.read_pickle('../matrix/'+contents2+'_count_tdm.pkl')
    else:
        print("Cannot find corpus file or matrix")

    result_df = competive_network(corpus_df1, corpus_df2, df1, df2, word_num = 20)
    result_df.to_csv("../results/tmp_compnetwork.csv", index = False)
    viz_compnetwork(result_df)
    print(result_df)