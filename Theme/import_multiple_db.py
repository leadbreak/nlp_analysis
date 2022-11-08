'''
DB에서 데이터 호출시 여러 개의 경쟁 콘텐츠에 대해 각각 task id를 리스트로 받아서
특정 콘텐츠에 해당하는 task id list를 받음. 리스트 안에는 channel, task_id 가 튜플로 포함됨
콘텐츠 단위로 Data frame merging 진행
'''

from Theme import import_db

def merging_channel_df(contents_name): #한 개의 콘텐츠에 해당하는 여러 Channel의 dataframe 을 리스트에 넣음
    task_list = []

    with open('../Task_list/'+ str(contents_name) +'_task_id_list.txt', encoding='cp949') as f:
        lines = f.readlines()
        for line in lines:
            line = line.replace('\n', '')
            tmplist = line.split(',')
            tmptuple = (tmplist[0], tmplist[1])
            task_list.append(tmptuple)
    df_list = import_db.request_db(task_list)
    return df_list


def get_df_list(contents_list): #리스트에 있는 한개의 contents에 해당하는 여러 dataframe을 하나로 합침. 이를 콘텐츠별로 진행해서 콘텐츠별 통합 dataframe을 담고 있는 list return
    contents_df_list = []

    for contents_name in contents_list:
        tmpdf_list = merging_channel_df(contents_name)
        tmpdf = tmpdf_list[0]
        for df in tmpdf_list[1:]:
            tmpdf = tmpdf.append(df)
        contents_df_list.append(tmpdf)

    return contents_df_list


if __name__ == "__main__":
    contents_list = ['브라운더스트', '소녀전선', '랑그릿사', '붕괴', '파이널블레이드', '데일리판타지']
    contents_df_list = get_df_list(contents_list)

    for df in contents_df_list:
        print(df.shape)
        df.to_csv(str(input("save text file : ")+'.csv'), index = False)