#연관 단어 시각화 Test file
import numpy as np
import pandas as pd
import time, os
from Theme.extract_rawtext import easy_extraction

#시각화 packages
import networkx as nx
from wordcloud import WordCloud
from PIL import Image
import matplotlib.pyplot as plt
from matplotlib import font_manager, rc

font_name = font_manager.FontProperties(fname="C:\\Windows\\Fonts\\malgun.ttf").get_name() # 시각화시 한글 설정
rc('font', family=font_name)

def importing_df(cnt_tdm, first_dep = 10):
    cnt_keyword = cnt_tdm.sum(axis=0).sort_values(ascending = False)
    result_df = pd.DataFrame(cnt_keyword[:first_dep].reset_index())
    result_df.columns = ['keyword', 'cnt']
    return result_df

def first_lev_cloud(cnt_tdm, word, num_word):
    result_df = importing_df(cnt_tdm, num_word)
    center_node = []
    for i in range(len(result_df['keyword'])):
        center_node.append(word)  # 중심에 있을 contents 이름
        # network 관계를 구성할 table 지정
    network_df = pd.DataFrame({'from': center_node, 'to': result_df['keyword']})
    network_df['depth'] = 1
    network_df = network_df.append({'from': word, 'to': word, 'depth': 0}, ignore_index=True)
    network_df = network_df.sort_values(by='depth')

    node_size = [12000]  # initial node size
    firstdep_word = network_df.loc[network_df['depth'] == 1, 'to'].values
    total_val = cnt_tdm.loc[:, firstdep_word].sum(axis=0).sum()

    for i, word in enumerate(network_df.loc[network_df['depth'] == 1, 'to'].values):
        # node_size.append(8500)
        if i == 0:
            node_size.append(node_size[0] - 1000)
        else:
            cnt_val = cnt_tdm.loc[:, word].sum(axis=0) / total_val
            pre_val = cnt_tdm.loc[:, firstdep_word[i - 1]].sum(axis=0) / total_val
            size_val = node_size[-1] - ((((cnt_val - pre_val) / pre_val) * 120) ** 2)  # size value
            if size_val <= 3500:
                node_size.append(3500)
            else:
                node_size.append(size_val)
    network_df['value'] = node_size

    cloud_mask = np.array(Image.open("./cloud.png"))
    print(cloud_mask)
    print(cloud_mask.shape)
    wordcloud = WordCloud(
        width=800,
        height=800,
        font_path="C:\\Windows\\Fonts\\malgun.ttf",
        mask=cloud_mask,
        background_color="white"
    )

    keywords = {}
    for i in range(network_df.shape[0]):
        keywords[network_df.loc[i, 'to']] = network_df.loc[i, 'value']

    wordcloud = wordcloud.generate_from_frequencies(keywords)
    plt.figure(figsize=(10, 10))
    plt.imshow(wordcloud.recolor(colormap=plt.cm.gnuplot), interpolation="bilinear")
    plt.axis("off")
    plt.show()

def first_lev_network(cnt_tdm, word, num_word):
    result_df = importing_df(cnt_tdm, num_word)
    center_node = []
    for i in range(len(result_df['keyword'])):
        center_node.append(word)  # 중심에 있을 contents 이름

    # network 관계를 구성할 table 지정
    network_df = pd.DataFrame({'from': center_node, 'to': result_df['keyword']})
    network_df['depth'] = 1
    network_df = network_df.append({'from': word, 'to': word, 'depth': 0}, ignore_index=True)
    network_df = network_df.sort_values(by='depth')

    node_size = [12000]  # initial node size
    firstdep_word = network_df.loc[network_df['depth'] == 1, 'to'].values
    total_val = cnt_tdm.loc[:, firstdep_word].sum(axis=0).sum()

    for i, word in enumerate(network_df.loc[network_df['depth'] == 1, 'to'].values):
        # node_size.append(8500)
        if i == 0:
            node_size.append(node_size[0] - 1000)
        else:
            cnt_val = cnt_tdm.loc[:, word].sum(axis=0) / total_val
            pre_val = cnt_tdm.loc[:, firstdep_word[i - 1]].sum(axis=0) / total_val
            size_val = node_size[-1] - ((((cnt_val - pre_val) / pre_val) * 150) ** 2)  # size value
            if size_val <= 2000:
                node_size.append(2000)
            else:
                node_size.append(size_val)

    carac = pd.DataFrame({'ID': network_df['to'], 'depth': list(network_df['depth'])})
    # Build graph
    G = nx.from_pandas_edgelist(network_df, 'from', 'to', 'depth')
    carac = carac.set_index('ID')
    carac['depth'] = pd.Categorical(carac['depth'])

    plt.figure(figsize=(15, 12))

    pos = nx.spring_layout(G, k=10., iterations = 10000, seed= 4)
    nx.draw(G, pos, with_labels=True, font_family=font_name,
                     font_size=13,
                     font_color='w',
                     node_shape='o',
                     node_size=node_size,
                     linewidths=3.,
                     width=1.,
                     font_weight='bold',
                     style='dashed',
                     alpha=1,
                     node_color=carac['depth'] ,
                     cmap=plt.cm.Set1
                     )
    plt.show()


def related_keyword(matrix, word, min_df, related_threshold, second_dep):  # Matrix, 지정 단어, 최소 출현수, 결과 도출 단어 수
    # print('전체 matrix shape : ', matrix.shape)
    total_words_sum = matrix.sum(axis=0)
    min_words = total_words_sum[total_words_sum > min_df].index

    filtering_tdm = matrix.loc[matrix[word] >= 1, min_words]
    # print('filtered matrix shape : ', filtering_tdm.shape)

    filter_words_sum = filtering_tdm.sum(axis=0)

    score_df = (filter_words_sum/matrix.shape[0]) / (matrix.loc[:, min_words].sum(axis=0)/matrix.shape[0]) #simple propotion like conditional probability

    score_df = pd.DataFrame(score_df.reset_index())
    score_df.columns = ['word', 'score']
    score_df = score_df.sort_values(by='score', ascending=False)
    score_df['rank'] = range(score_df.shape[0])

    f_score_df = score_df.loc[score_df['score'] >= related_threshold, :]
    f_score_df = f_score_df.iloc[1:, :]
    f_score_df = f_score_df.iloc[:second_dep, :]

    return f_score_df


def networktable2(result_df, cnt_tdm, corpus_df, centerword, min_df, related_threshold, second_dep):
    center_node = []
    for i in range(len(result_df['keyword'])):
        center_node.append(centerword)  # 중심에 있을 contents 이름

    # network 관계를 구성할 table 지정
    network_df = pd.DataFrame({'from': center_node, 'to': result_df['keyword']})
    network_df['depth'] = 1
    network_df = network_df.append({'from': centerword, 'to': centerword, 'depth': 0}, ignore_index=True)
    network_df = network_df.sort_values(by='depth')

    # 만들어진 network 관계 dataframe에서 depth 를 추가하는 과정
    lev1_list = list(network_df.loc[network_df['depth'] == 1, 'to']) #level-1 node
    value_list = [cnt_tdm.shape[0]]
    for t in list(cnt_tdm.loc[:, lev1_list].sum(axis=0).values):
        value_list.append(t)
    network_df['val'] = value_list

    for depone_keyword in lev1_list:  # second level depth
        tmp_related_df = related_keyword(cnt_tdm, depone_keyword, min_df, related_threshold, second_dep)  # Matrix, 지정 단어, 최소 출현수, 결과 도출 단어 수
        for related_word in tmp_related_df['word']:
            network_df = network_df.append({'from': depone_keyword, 'to': related_word, 'depth': 2, 'val': tmp_related_df.loc[tmp_related_df['word']==related_word, 'rank'].values[0]}, ignore_index=True)

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

def draw_network(network_table, cnt_tdm, size_par = 8000):
    node_size = [12000]  # center node size (brand name)
    firstdep_word = network_table.loc[network_table['depth'] == 1, 'to'].values

    for i,word in enumerate(network_table.loc[network_table['depth'] == 1, 'to'].values):
        if i == 0:
            init_size = node_size[0] + 2000
            node_size.append(init_size)
        else:
            norm_val = (cnt_tdm.loc[:, word].sum(axis=0) - cnt_tdm.loc[:, firstdep_word].sum(axis=0).min()) / (cnt_tdm.loc[:, firstdep_word].sum(axis=0).max()- cnt_tdm.loc[:, firstdep_word].sum(axis=0).min())
            size_val = ((init_size - size_par)*norm_val) + size_par
            node_size.append(size_val)
    for i in range(len(network_table) - len(firstdep_word)):
        node_size.append(5000)


    tmp_network_df = network_table.drop_duplicates('to', keep='first')
    tmp_network_df.loc[:,'depth'] = pd.Categorical(tmp_network_df.loc[:,'depth'])
    # 2-depth network visualization

    carac = pd.DataFrame({'ID': network_table['to'], 'depth': list(network_table['depth'])})
    # Build graph
    G = nx.from_pandas_edgelist(network_table, 'from', 'to', 'depth')
    carac = carac.set_index('ID')
    carac['depth'] = pd.Categorical(carac['depth'])

    plt.figure(figsize=(16, 14))

    pos = nx.spring_layout(G, k=20., iterations = 20000, seed=11)
    nx.draw(G, pos, with_labels=True, font_family=font_name,
                     font_size=17,
                     font_color='w',
                     node_shape='o',
                     node_size=node_size,
                     linewidths=.5,
                     width=1.,
                     font_weight='bold',
                     style='dashed',
                     alpha=1,
                     node_color=tmp_network_df['depth'].cat.codes,
                     cmap=plt.cm.Set1
                     )
    plt.show()

def complexity_control(user_option = 'normal'):
    #v_simple, simple , normal , complex, v_complex 단계로 구성
    if user_option == 'normal':
        network_table = networktable2(result_df, cnt_tdm, center_node, min_df=10, related_threshold=.5, second_dep=5)
        draw_network(network_table, cnt_tdm, size_par=8000)
    elif user_option == 'simple':
        network_table = networktable2(result_df, cnt_tdm, center_node, min_df=10, related_threshold=.6, second_dep=4)
        draw_network(network_table, cnt_tdm, size_par=8000)
    elif user_option == 'v_simple':
        network_table = networktable2(result_df, cnt_tdm, center_node, min_df=10, related_threshold=.7, second_dep=3)
        draw_network(network_table, cnt_tdm, size_par=8000)
    elif user_option == 'complex':
        network_table = networktable2(result_df, cnt_tdm, center_node, min_df=10, related_threshold=.4, second_dep=6)
        draw_network(network_table, cnt_tdm, size_par=8000)
    elif user_option == 'v_complex':
        network_table = networktable2(result_df, cnt_tdm, center_node, min_df=10, related_threshold=.3, second_dep=7)
        draw_network(network_table, cnt_tdm, size_par=8000)


def complexity_control2(user_option = 5):
    #v_simple, simple , normal , complex, v_complex 단계로 구성
    if user_option == 1:
        network_table = networktable2(result_df, cnt_tdm, center_node, min_df=10, related_threshold=.5, second_dep=3)
        draw_network(network_table, cnt_tdm, size_par=8000)
    elif user_option == 2:
        network_table = networktable2(result_df, cnt_tdm, center_node, min_df=10, related_threshold=.45, second_dep=4)
        draw_network(network_table, cnt_tdm, size_par=8000)
    elif user_option == 3:
        network_table = networktable2(result_df, cnt_tdm, center_node, min_df=10, related_threshold=.4, second_dep=5)
        draw_network(network_table, cnt_tdm, size_par=8000)
    elif user_option == 4:
        network_table = networktable2(result_df, cnt_tdm, center_node, min_df=10, related_threshold=.35, second_dep=6)
        draw_network(network_table, cnt_tdm, size_par=8000)
    elif user_option == 5:
        network_table = networktable2(result_df, cnt_tdm, center_node, min_df=10, related_threshold=.3, second_dep=7)
        draw_network(network_table, cnt_tdm, size_par=8000)


if __name__ == "__main__":
    center_node = "경제위기"
    corpus_df = pd.read_csv('../matrix/'+str(center_node)+'_raw.csv')
    cnt_tdm = pd.read_pickle('../matrix/'+str(center_node)+'_count_tdm.pkl')
    #first_lev_cloud(cnt_tdm, center_node, 20)
    #first_lev_network(cnt_tdm, center_node, 30)
    first_lev_words = 10
    result_df = importing_df(cnt_tdm, first_dep = first_lev_words)

    network_table = networktable2(result_df, cnt_tdm, corpus_df, center_node,  min_df=10, related_threshold=.5, second_dep = 5)
    network_table.to_csv("../results/"+center_node+"_network.csv", index = False)
    draw_network(network_table, cnt_tdm, size_par = 8000)