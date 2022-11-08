"""
MongoDB 에서 data import 과정
사용자가 n개의 채널 옵션을 입력 -> 채널 리스트 생성
리스트 돌면서 collection에서 특정 task에 해당하는 Table 을 가져와 pandas dataframe 형태로 변환
n개의 dataframe을 리스트에 넣어서 리스트를 최종적으로 return

user : ddive
db address : "ec2-13-125-237-255.ap-northeast-2.compute.amazonaws.com/"
password : ddive0318!
port : 27017
db : crawler_db
"""

import pandas as pd
from pymongo import MongoClient

username = "ddive"
password = "ddive0318!"
host = "ec2-13-125-237-255.ap-northeast-2.compute.amazonaws.com/"
port = "27017"
db = "crawler_db"

address= 'mongodb://'+ username + ':' + password +'@'+ host
#task_list= [('playstore','6496993e-7950-472b-a247-522715952ba5'),('playstore','6496993e-7950-472b-a247-522715952ba5')] # channel, task-id tuple을 담고 있는 리스트

def get_task_list(contents_name, isfile = True): # (collection key, task_id) 의 리스트를 return
    task_list = []
    if isfile:
        with open('../Task_list/' + str(contents_name) + '_task_id_list.txt', encoding='cp949') as f:
            lines = f.readlines()
            for line in lines:
                line = line.replace('\n', '')
                tmplist = line.split(',')
                tmptuple = (tmplist[0], tmplist[1])

                task_list.append(tmptuple)
        return task_list

    else: #직접 channel, task id를 입력
        print(contents_name)
        task_list = [tuple(str(input("insert channel,task-id : ")).split(','))]
        print(task_list)
        return task_list

def request_db(task_list):
    dataframe_list = []
    client  = MongoClient('mongodb://%s:%s@ec2-13-125-237-255.ap-northeast-2.compute.amazonaws.com:27017' % (username, password))
    db = client.cralwer_db
    collection_dict = {'playstore': db.media_playstore, 'appstore': db.media_appstore, 'twitter': db.media_twitter,
                       'naver': db.media_naver, 'instagram':db.media_instagram, 'googlemaps': db.media_goolgemaps}

    for col in task_list:

        if col[0] == 'appstore' or col[0] == 'naver':
            columns = ['date', 'user_name', 'content', 'title','user_score']
            collection = collection_dict[col[0]]
            id = col[1]
            data = pd.DataFrame(list(collection.find({'task_id':id})))
            df = data.loc[:,columns]
            df['user_text'] = df['title'] + " " + df['content']
            df = df.loc[df['date'] != 'NOT_FOUND', ['date', 'user_name', 'user_text','user_score']]
            df['date'] = pd.to_datetime(df['date'])
            df['date'] = df['date'].astype('datetime64[ns]')
            dataframe_list.append(df)

        elif col[0] == 'twitter' or col[0] == 'instagram':
            columns = ['date', 'user_name', 'user_text']
            collection = collection_dict[col[0]]
            id = col[1]
            data = pd.DataFrame(list(collection.find({'task_id': id})))
            df = data.loc[:, columns]
            wordlist = ["네이버 뉴스", "토스", "smartconsumer", "배팅","렌탈", " 뉴스", "[뉴스]", "할인", "이벤트"] #word list for spam posting
            df = df.loc[df['user_text'].apply(lambda x: 1 if any(s in x for s in wordlist) else 0) == 0]
            dataframe_list.append(df)

        else:
            columns = ['date', 'user_name', 'user_text', 'user_score']
            collection = collection_dict[col[0]]
            id = col[1]
            data = pd.DataFrame(list(collection.find({'task_id': id})))
            df = data.loc[:, columns]
            dataframe_list.append(df)
    return dataframe_list

def merging_df(df_list):
    tmpdf = df_list[0]
    for df in df_list[1:]:
        tmpdf = tmpdf.append(df)
    tmpdf = tmpdf.reset_index(drop=True)
    return tmpdf

def import_data(task_list): #한 개의 콘텐츠에 관련된 여러 channel의 data frame 들을 합쳐서 하나의 table 로 return
    df_list = request_db(task_list)
    return merging_df(df_list)

def request_db_channel(task_list):
    dataframe_list = []

    client = MongoClient(
        'mongodb://%s:%s@ec2-13-125-237-255.ap-northeast-2.compute.amazonaws.com:27017' % (username, password))
    db = client.cralwer_db
    collection_dict = {'playstore': db.media_playstore, 'appstore': db.media_appstore, 'twitter': db.media_twitter,
                       'naver': db.media_naver, 'instagram':db.media_instagram, 'googlemaps': db.media_goolgemaps}

    for col in task_list:
        if col[0] == 'appstore' or col[0] == 'naver':
            columns = ['date', 'user_name', 'content', 'title']
            collection = collection_dict[col[0]]
            id = col[1]
            data = pd.DataFrame(list(collection.find({'task_id': id})))
            df = data.loc[:, columns]
            df['user_text'] = df['title'] + " " + df['content']
            df = df.loc[:, ['date', 'user_name', 'user_text']]
            df['channel'] = col[0]
            dataframe_list.append(df)

        elif col[0]=='twitter' or col[0] == 'instagram':
            columns = ['date', 'user_name', 'user_text']
            collection = collection_dict[col[0]]
            id = col[1]
            data = pd.DataFrame(list(collection.find({'task_id': id})))
            df = data.loc[:, columns]
            wordlist = ["네이버 뉴스", "토스", "smartconsumer", "배팅", "렌탈", " 뉴스", "[뉴스]", "할인",
                        "이벤트"]  # word list for spam posting
            df = df.loc[df['user_text'].apply(lambda x: 1 if any(s in x for s in wordlist) else 0) == 0]
            df['channel'] = col[0]
            dataframe_list.append(df)

        else:
            columns = ['date', 'user_name', 'user_text']
            collection = collection_dict[col[0]]
            id = col[1]
            data = pd.DataFrame(list(collection.find({'task_id': id})))
            df = data.loc[:, columns]
            df['channel'] = col[0]
            dataframe_list.append(df)

    return dataframe_list

def import_channel_data(task_list):
    df_list = request_db_channel(task_list)
    return merging_df(df_list)

if __name__ == "__main__":
    task_list = get_task_list('에이클린')
    #task_list = get_task_list('test', isfile=False)
    dataframe = import_data(task_list)
    dataframe.to_csv("../raw_data/"+str(input("save file name : "))+'.csv', index = False)
    print(dataframe.columns, dataframe.shape)
    print(dataframe.head(10))