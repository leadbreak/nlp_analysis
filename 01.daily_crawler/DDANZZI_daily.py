#!/usr/bin/env python
# coding: utf-8

# In[1]:


# 필요한 모듈과 라이브러리를 로딩
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import pandas as pd
import time, os, math, random, sys, datetime
from datetime import date, timedelta, datetime
import pyautogui
from tqdm import tqdm
import _thread

# chromedriver 자동 설치
import chromedriver_autoinstaller

from selenium.webdriver.common.action_chains import ActionChains


# In[2]:


# 작업 시간과 고유 dir 등 생성
n = time.localtime()
s = '%04d-%02d-%02d' % (n.tm_year, n.tm_mon, n.tm_mday)
s_time = time.time( )


a = datetime.now()-timedelta(days=1)
a = a.strftime('%Y-%m-%d')
b = datetime.now()-timedelta(days=1)
b = b.strftime('%Y-%m-%d')
print(b, a)


# In[3]:


print("=" *80)
print("         OPINION 크롤러입니다.")
print("=" *80)

f_dir = os.path.expanduser('~') + f'\\Desktop\\daily\\{b}\\' # 운영체제 상관없이 바탕화면 'crawler-bot' 폴더에 작업

print("=" *80)
print("데이터 크롤링을 시작합니다.")
print("=" *80)


# In[4]:


# 저장될 파일 경로와 이름을 지정
# 파일을 저장할 폴더 위치를 만들고, 중복일 경우 해당 폴더를 삭제하고 새로 생성합니다.
try : 
    os.makedirs(f_dir)
except : pass
else : 
    os.chdir(f_dir)

fc_name=f_dir+'\\'+f'ddanzi.csv'


# In[5]:


# 크롤링 데이터가 들어갈 리스트 생성
domain2 = []    # 크롤링 도메인
keyword2 = []   # 크롤링 키워드
title2 = []     # 게시물 제목
user2 = []      # 게시물 작성자
url2 = []       # 게시물 url
time2 = []      # 게시물 작성 시간
view_cnt2 = []  # 게시물 뷰 카운트
like_cnt2 = []  # 추천/공감 카운트
text2 = []      # 게시물 내용
com_cnt2 = []   # 댓글 수
com_user2 = []  # 작성자 본인을 제외한 댓글 유저
com_text2 = []  # 댓글 user_id & text


# In[6]:


# chromedriver-autoinstaller 이용

chromedriver_autoinstaller.install(cwd=True)

# HEADLESS MODE
options = webdriver.ChromeOptions()
# options.add_argument('headless')
options.add_argument('window-size=1920x1080') 
# options.add_argument("--disable-gpu")
options.add_experimental_option('excludeSwitches', ['enable-logging'])
options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36")
args = ["hide_console", ]

# 알림창 끄기
options.add_experimental_option("prefs", {"profile.default_content_setting_values.notifications": 1})

# 웹사이트 접속 후 해당 메뉴로 이동
driver = webdriver.Chrome(options=options,service_args=args)
driver.maximize_window()


# In[7]:


# 1. 딴지 크롤링
query_url= ('https://www.ddanzi.com/free')

driver.get(query_url)
driver.implicitly_wait(5)


# In[8]:


domain1 = "딴지"
print("==========",domain1,"크롤링 진행 중 ==========")


# In[9]:

tmp_id = "ddive1041"
tmp_pw = "q1w2e3r4!@"

def login() :    

    driver.find_element_by_link_text('로그인').click()
    time.sleep(1)
    # id 입력
    driver.find_element_by_xpath('//*[@id="uid"]').click()
    for i in tmp_id :
        time.sleep(0.1)
        driver.find_element_by_xpath('//*[@id="uid"]').send_keys(i)

    # pw 입력    
    driver.find_element_by_xpath('//*[@id="upw"]').click()
    for j in tmp_pw :
        time.sleep(0.1)
        driver.find_element_by_xpath('//*[@id="upw"]').send_keys(j)

    driver.find_element_by_xpath('//*[@id="regularsubmit"]/td/button').click()
    time.sleep(1)


# In[10]:


login()


page_num = 19
while_code = 0
driver.get(f"https://www.ddanzi.com/index.php?mid=free&page={page_num}")
while True :
    if while_code == 1 :
        print("\n\n")
        print("===== 1차 게시물 수집 작업 완료...")
        print("===== 2차 게시물 내용 수집으로 넘어갑니다.")
        print("\n\n")
        break
    

        
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    item_box = soup.find_all(name='tbody')[-1].find_all('tr')              
        
    
    post_num = 0
    
    for item in item_box :
        
        try : # 공지글만 class가 있음, 공지글 제외
            item['class']
            post_num += 1
            cut_post_num = post_num
        except :
            post_num += 1
            page_num += 1

            # 크롤링 시작
            post_time = item.find(name='td', attrs={'class':'time'}).text        


            # 시간만 표시되는 오늘 게시물이거나, 올해 게시물만 크롤링
            if post_time > a or (datetime.now().strftime('%Y-%m-%d') != a and ":" in post_time):
                time_code=0
            elif datetime.now().strftime('%Y-%m-%d') == a and ":" in post_time :
                time_code = 1 
            elif post_time <= a and post_time >= b  :
                time_code = 1
            else : # 시간 영역이 맞지 않는 경우 time_code=2 로 변경
                time_code = 2
            
            print("time_scout:",post_time, time_code)
            if time_code == 1 :

                # print("크롤링 도메인 : ",domain1)

                title1 = item.find(name='td', attrs={'class':'title'}).find('a').text.strip()
                user1 = item.find(name='td', attrs={'class':'author txtleft'}).text.strip()
                url1 = item.find(name='td', attrs={'class':'title'}).find('a')['href']
                time1 = item.find(name='td', attrs={'class':'time'}).text
                view_cnt1 = item.find(name='td', attrs={'class':'readNum'}).text
                like_cnt1 = item.find(name='td', attrs={'class':'voteNum'}).text.strip()
                
                try :
                    com_cnt1 = item.find(name='td', attrs={'class':'title'}).find(name='span', attrs={'class':'talk'}).text.replace("[","").replace("]","").strip()
                except :
                    com_cnt1 = 0

                # print("게시물 제목 :", title1)
                # print("작성자 :", user1)
                # print("게시물 url :", url1)
                # print("업로드 시간 :", time1)
                # print("조회수 :", view_cnt1)
                # print("추천수 :", like_cnt1)
                # print("댓글수 :", com_cnt1)
                # print("\n")

                domain2.append(domain1)
#                 keyword2.append(keyword)
                title2.append(title1)
                user2.append(user1)
                url2.append(url1)
                time2.append(time1)
                view_cnt2.append(view_cnt1)
                like_cnt2.append(like_cnt1)
                com_cnt2.append(com_cnt1)    


            elif time_code == 2 :
                while_code = 1
                break
                

    
    if post_num == cut_post_num : # 게시물이 나오지 않고 공지만 있는 경우 : 계속 검색으로 우회
        print("=====   계속 검색을 시도합니다.   =====")
        driver.find_element_by_link_text("계속 검색").click()
        driver.implicitly_wait(3)
        time.sleep(2)
        page_num = 1
        
    else :
        print("=====   다음 페이지로 넘어갑니다.   =====")
        try :
            
            cur_url = driver.current_url        
            cur_page = int(cur_url.split("&page=")[1])
            print("scout 03 :", cur_url)
            next_page = cur_page + 1
            next_url = cur_url.split("&page=")[0] + "&page=" + str(next_page)
            print("scout 04 :", cur_url.split("&page="))
            print("scout 05 :", next_url)
            driver.get(next_url)
            driver.implicitly_wait(3)
            time.sleep(3)
            
        except :
            try :                
                print("scout 01:", driver.current_url )
                driver.find_element_by_link_text("2").click()
                driver.implicitly_wait(3)
                time.sleep(2)
                print("scout 02:", driver.current_url )
            except : # 페이지가 하나밖에 표시되지 않은 경우 - 계속 검색으로 우회
                print("=====   계속 검색을 시도합니다.   =====")
                driver.find_element_by_link_text("계속 검색").click()
                driver.implicitly_wait(3)
                time.sleep(2)
                page_num = 1
                
                


# In[16]:


def crawling02() :
    global batch_cnt, while_code, driver, url2

    print(f"======   키워드 게시물 총 {len(url2)}개입니다.   =====")
    print(f"=====   총 {math.ceil(len(url2) / 10)} 개의 batch로 나눠 진행합니다.   ======")

    while True :
        print(f"현재 {batch_cnt+1}번째 batch 진행 중...")
        driver.refresh()

        try :
            login()
        except :
            pass

        time.sleep(1)

        url_list = [x for x in url2[batch_cnt*10:batch_cnt*10+10]] # 10개씩 끊기

        batch_user2 = []
        batch_text2 = []
        batch_com_text2 = []

        for url in tqdm(url_list) :
            print("url :", url)

            com_cnt = 0

            while True :

                com_cnt += 1

                post_code = 0

                try :

                    driver.get(url)
                    time.sleep(random.randint(2,3))

                    html = driver.page_source
                    soup = BeautifulSoup(html, 'html.parser')

                    text1 = soup.find(name='div', attrs={'class':'read_content'}).text.strip().replace("\n", "")
                    com_user_list = soup.find(name='div', attrs={'id':'cmt_list'}).find_all(name='div', attrs={'class':'fbItem_left'})
                    com_text_list = soup.find(name='div', attrs={'id':'cmt_list'}).find_all(name='div', attrs={'class':'fbItem_right'})
                    tmp_list = []
                    user_list = []

                    for k in range(len(com_user_list)) :

                        string = "작성자 : " + com_user_list[k].text.strip().replace("\n","").replace("\t", "") + " :: " + com_text_list[k].text.strip().replace("\n","").replace("\t", "")
                        com_list.append(string)
                        user_list.append(com_user_list[k].find(name='h4',attrs={'class':'author'}).text.strip().replace("\n","").replace("\t", "").replace("본문 글쓴이",""))

                    for k in range(len(com_user_list)) :
                #         print(com_user_list[k].text.strip().replace("\n",""),com_text_list[k].text.strip().replace("\n",""))
                        string = com_user_list[k].text.strip().replace("\n","").replace("\t", "") + " : " + com_text_list[k].text.strip().replace("\n","").replace("\t", "")
                        tmp_list.append(string)
                    com_text1 = tmp_list


                    # print("본문 :", text1)
                    # print("댓글 유저 :", user_list)
                    # print("댓글 :", com_text1)
                    # print("\n")

                    batch_text2.append(text1)
                    batch_user2.append(user_list)
                    batch_com_text2.append(com_text1)

                    post_code = 1

                    break

                except : # 글이 삭제된 경우

                    except_cnt = 0

                    while except_cnt <= 2 :
                        except_code = 0

                        try :
                            except_cnt += 1

                            driver.refresh()
                            driver.get(url)
                            time.sleep(1)

                            html = driver.page_source
                            soup = BeautifulSoup(html, 'html.parser')

                            text1 = soup.find(name='div', attrs={'class':'read_content'}).text.strip().replace("\n", "")
                            com_user_list = soup.find(name='div', attrs={'id':'cmt_list'}).find_all(name='div', attrs={'class':'fbItem_left'})
                            com_text_list = soup.find(name='div', attrs={'id':'cmt_list'}).find_all(name='div', attrs={'class':'fbItem_right'})
                            user_list = []
                            com_list = []
    #                         tmp_list = []

                            for k in range(len(com_user_list)) :

                                string = "작성자 : " + com_user_list[k].text.strip().replace("\n","").replace("\t", "").replace("본문 글쓴이","") + " :: " + com_text_list[k].text.strip().replace("\n","").replace("\t", "")
                                com_list.append(string)
                                user_list.append(com_user_list[k].find(name='h4',attrs={'class':'author'}).text.strip().replace("\n","").replace("\t", "").replace("본문 글쓴이",""))

    #                         for k in range(len(com_user_list)) :
    #                     #         print(com_user_list[k].text.strip().replace("\n",""),com_text_list[k].text.strip().replace("\n",""))
    #                             string = com_user_list[k].text.strip().replace("\n","").replace("\t", "") + " : " + com_text_list[k].text.strip().replace("\n","").replace("\t", "")
    #                             tmp_list.append(string)
                            com_text1 = com_list


                            # print("본문 :", text1)
                            # print("댓글 유저 :", user_list)
                            # print("댓글 :", com_list)
                            # print("\n")

                            batch_text2.append(text1)
                            batch_user2.append(user_list)
                            batch_com_text2.append(com_list)

                            except_code = 1

                            break

                        except :
                            pass

                if except_code == 0 :
                    driver.refresh()

                    try :
                        login()
                    except :
                        pass

                    print("삭제된 게시물 입니다.")

                    try :                    
                        # print("본문 :", text1)
                        # print("댓글 유저:", user_list)
                        # print("댓글 :", com_text1)
                        print("\n")                
                    except :
                        pass

                    text1 = "삭제된 게시물"
                    user_list = [""]
                    com_text1 = "삭제된 게시물"


                    # print("본문 :", text1)
                    # print("댓글 유저:", user_list)
                    # print("댓글 :", com_text1)
                    # print("\n")

                    batch_text2.append(text1)
                    batch_user2.append(user_list)
                    batch_com_text2.append(com_text1)

                    break

        for i in range(len(batch_text2)) :
            text2.append(batch_text2[i])
            com_text2.append(batch_com_text2[i])
            com_user2.append(batch_user2[i])

        if batch_cnt*10+10 >= len(url2) :
            while_code = 1
            break

        batch_cnt += 1

    print("모든 크롤링 작업을 완료하였습니다.")


                

# In[ ]:


batch_cnt = 0
# batch_cnt += 1
# login()
while_code = 0
while True :
    if while_code == 1 :
        break
        
    try :
        crawling02()
    except :
        # _thread.exit()
        element = driver.find_element_by_tag_name('body')
        element.send_keys(Keys.F5)
        print("timeout 감지 - 새로고침합니다.")

    if while_code != 1 :
    
        driver.delete_all_cookies()
        driver.refresh()
        time.sleep(2)
        login()


# In[ ]:


print("Let's Test")


# In[ ]:


df = pd.DataFrame()

df['domain'] = pd.Series(domain2)
# df['keyword'] = pd.Series(keyword2)
df['title'] = pd.Series(title2)
df['user_name'] = pd.Series(user2)
df['url'] = pd.Series(url2)
df['date'] = pd.Series(time2)
df['view_cnt'] = pd.Series(view_cnt2)
df['like_cnt'] = pd.Series(like_cnt2)
df['user_text'] = pd.Series(text2)
df['com_cnt'] = pd.Series(com_cnt2)
df['com_user'] = pd.Series(com_user2)
df['com_text'] = pd.Series(com_text2)

for i in range(len(df)) :
    if len(df['user_text'][i]) < 5 :
        df['user_text'][i] = df['title'][i]


# In[ ]:


# csv 형태로 저장하기
df.to_csv(fc_name,encoding="utf-8-sig",index=False)

e_time = time.time( )
t_time = e_time - s_time

print("\n")
print("=" *80)
print("1.총 소요시간은 %s 초 입니다 " %round(t_time,1))
print("2.파일 저장 완료: csv 파일명 : %s " %fc_name)

driver.quit()
sys.exit("프로그램을 종료합니다.")

