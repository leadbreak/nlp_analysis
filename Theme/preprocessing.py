import pandas as pd
from Theme.import_db import *
from soynlp.normalizer import *
from soyspacing.countbase import CountSpace
import time, re, os

def preprocessing(corpus_df):
    start = time.time()
    # 원문 수정 단계
    corpus_df['user_text'] = corpus_df['user_text'].astype('str')
    corpus_df['user_text'] = corpus_df['user_text'].str.lower()
    corpus_df['user_text'] = corpus_df['user_text'].str.replace(r'[ㄱ-ㅎ]', ' ')
    #corpus_df['user_text'] = corpus_df['user_text'].str.replace(r"[(굿)+]","좋아요 ")
    corpus_df['user_text'] = corpus_df['user_text'].str.replace(r'[.]+', '.')
    corpus_df['user_text'] = corpus_df['user_text'].str.replace(r'[-=+,/<>\;:^$@*\"※~&%ㆍ!』\\‘|\(\)\[\]\<\>`\'…》◀▶●■★◆]', '')
    # corpus_df['user_text'] = corpus_df['user_text'].str.replace(r'[http://][a-z]+', '')
    # corpus_df['user_text'] = corpus_df['user_text'].str.replace(r'[www.][a-z]+', '')
    # corpus_df['user_text'] = corpus_df['user_text'].str.replace(r'[.]+[a-zA-Z0-9_]+', '')
    corpus_df = corpus_df.dropna(subset=['user_text']) # 특수문자가 제거되어 공백이 된 문서를 제거함
    print(corpus_df.shape)
    corpus_df['user_text'] = corpus_df['user_text'].apply(only_text) # 한글, 영어, 숫자에 해당하는 텍스트만 남김
    corpus_df['user_text'] = corpus_df['user_text'].apply(repeat_normalize) #반복되는 문자를 줄여줌 와하하하하하하하하하핫 -> 와하하핫
    corpus_df['user_text'] = corpus_df['user_text'].apply(emoticon_normalize) #반복되는 이모티콘을 줄여줌 ㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋ쿠ㅜㅜㅜㅜㅜㅜ -> ㅋ쿠ㅜ
    # 단어 수정
    # web상에서 쓰이는 용어나 자주 발생하는 오타를 포함해 품사 태깅 시 잘못된 단어 인식을 방지하기 위해 단어를 수정하는 단계
    word_replace_df = pd.read_csv('./wordreplace/word_replace_총선.txt', sep='\t')
    word_replace_df = word_replace_df.fillna(" ")
    beforelist = list(word_replace_df.before)
    afterlist = list(word_replace_df.after)

    for i in range(word_replace_df.shape[0]):
        corpus_df['user_text'] = corpus_df['user_text'].str.replace(beforelist[i], afterlist[i])

    # 띄어쓰기 교정 training (임시로 활용)
    # 전체 문서의 띄어쓰기 구간을 학습해 다시 띄어쓰기가 되어야할 부분을 수정하는 단계를 거침
    # 추후 띄어쓰기 교정을 할 수 있는 방법 모색 후 수정 가능
    model = CountSpace()
    model_fname = './wordreplace/space.model'
    if os.path.isfile(model_fname):
        print("loading saved model")
        model.load_model(model_fname, json_format=False)
    else:
        model.train('./wordreplace/2016-10-20_article_all_normed.txt')
        model.save_model(model_fname, json_format=False)

    verbose = False
    mc = 10  # min_count
    ft = 0.3  # force_abs_threshold
    nt = -.1  # nonspace_threshold
    st = 0.1  # space_threshold
    spc_doc = []

    for i in range(corpus_df.shape[0]):
        sent = corpus_df.loc[i, 'user_text']
        sent_corrected, tags = model.correct(
            sent,
            verbose=verbose,
            force_abs_threshold=ft,
            nonspace_threshold=nt,
            space_threshold=st,
            min_count=mc
        )
        spc_doc.append(sent_corrected)
    corpus_df['user_text'] = spc_doc
    # 단어 수정
    # web상에서 쓰이는 용어나 자주 발생하는 오타를 포함해 품사 태깅 시 잘못된 단어 인식을 방지하기 위해 단어를 수정하는 단계
    word_replace_df = pd.read_csv('./wordreplace/word_replace.txt', sep='\t')
    word_replace_df = word_replace_df.fillna(" ")
    beforelist = list(word_replace_df.before)
    afterlist = list(word_replace_df.after)

    for i in range(word_replace_df.shape[0]):
        corpus_df['user_text'] = corpus_df['user_text'].str.replace(beforelist[i], afterlist[i])

    corpus_df = corpus_df[corpus_df['user_text'].str.len() > 1]

    corpus_df.drop_duplicates(subset = 'user_text', inplace = True, keep='last')
    print("Text 원문 전처리 후 data shape : ", corpus_df.shape)
    print(time.time() - start, ' sec spent for preprocessing')
    return corpus_df

def include_words(corpus_df): #특정 단어들의 리스트를 받아서 해당 단어들이 본문에 포함된 문서만 filtering
    terms = str(input("포함시킬 단어 리스트  (AND 연산으로 filtering): "))
    base = r'^{}'
    expr = '(?=.*{})'
    p = base.format(''.join(expr.format(w) for w in terms))

    corpus_df = corpus_df.loc[corpus_df['user_text'].str.contains(p)]
    return corpus_df

def exclude_words(corpus_df): #특정 단어들의 리스트를 받아서 해당 단어들이 본문에 있는 문서들을 제외시킴
    wordlist = str(input("띄어쓰기 기준 필터 단어 리스트 : ")).split()  # word list for filtering spam_posting
    corpus_df = corpus_df.loc[corpus_df['user_text'].apply(lambda x: 1 if any(s in x for s in wordlist) else 0) == 0]
    return corpus_df


if __name__ == "__main__":
    # task_list = get_task_list('브라운더스트')
    # corpus_df = import_data(task_list)

    df1 = pd.read_csv('../raw_data/브라운더스트.csv')
    df1['game'] = '브라운더스트'
    contents_list = ['소녀전선', '붕괴', '파이널블레이드', '랑그릿사', '데일리판타지']

    for game in contents_list:
        new_game_df = pd.read_csv('../raw_data/'+game+'.csv')
        new_game_df['game'] = game
        df1 = df1.append(new_game_df)

    corpus_df = df1.reset_index(drop=True)

    print(corpus_df.shape)
    print(corpus_df['game'].value_counts())

    corpus_df = preprocessing(corpus_df)
    corpus_df.to_csv("./topic_modeling_game.csv", index = False)