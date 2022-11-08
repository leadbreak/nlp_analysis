#!/usr/bin/env python
# coding: utf-8

# In[ ]:


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

# chromedriver 자동 설치
import chromedriver_autoinstaller

from selenium.webdriver.common.action_chains import ActionChains


# In[ ]:


# 작업 시간과 고유 dir 등 생성
n = time.localtime()
s = '%04d-%02d-%02d' % (n.tm_year, n.tm_mon, n.tm_mday)
s_time = time.time( )

a = datetime.now()-timedelta(days=1)
a = a.strftime('%Y-%m-%d')
b = datetime.now()-timedelta(days=1)
b = b.strftime('%Y-%m-%d')
print(a, b)


# In[ ]:


print("=" *80)
print("         OPINION 크롤러입니다.")
print("=" *80)

f_dir = os.path.expanduser('~') + f'\\Desktop\\daily\\{b}\\' # 운영체제 상관없이 바탕화면 'crawler-bot' 폴더에 작업

print("=" *80)
print("데이터 크롤링을 시작합니다.")
print("=" *80)


# In[ ]:


# 저장될 파일 경로와 이름을 지정
# 파일을 저장할 폴더 위치를 만들고, 중복일 경우 해당 폴더를 삭제하고 새로 생성합니다.
try : 
    os.makedirs(f_dir)
except : pass
else : 
    os.chdir(f_dir)

fc_name=f_dir+'\\'+f'clien.csv'


# In[ ]:


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
com_user2 = []  # 댓글 user
com_text2 = []  # 댓글 user_id & text


# In[ ]:


# chromedriver-autoinstaller 이용
chromedriver_autoinstaller.install(cwd=True)

# HEADLESS MODE
options = webdriver.ChromeOptions()
options.add_argument('headless')
options.add_argument('window-size=1920x1080') 
options.add_argument("--disable-gpu")
options.add_experimental_option('excludeSwitches', ['enable-logging'])
options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36")
args = ["hide_console", ]

# 알림창 끄기
options.add_experimental_option("prefs", {"profile.default_content_setting_values.notifications": 1})

# 웹사이트 접속 후 해당 메뉴로 이동
driver = webdriver.Chrome(options=options,service_args=args)
driver.maximize_window()


# In[ ]:


# 1. 클리앙 크롤링
query_url= ('https://www.clien.net/service/board/park')

driver.get(query_url)
driver.implicitly_wait(5)

domain1 = "클리앙"
print("==========",domain1,"크롤링 진행 중 ==========")

print("로그인을 진행합니다.")

tmp_id = "ddive1041"
tmp_pw = "q1w2e3r4!@"

# id 입력
driver.find_element_by_xpath('//*[@id="loginForm"]/input[2]').click()
for i in tmp_id :
    time.sleep(0.1)
    driver.find_element_by_xpath('//*[@id="loginForm"]/input[2]').send_keys(i)
    
# pw 입력    
driver.find_element_by_xpath('//*[@id="loginForm"]/input[3]').click()
for j in tmp_pw :
    time.sleep(0.1)
    driver.find_element_by_xpath('//*[@id="loginForm"]/input[3]').send_keys(j)
    
driver.find_element_by_xpath('//*[@id="loginForm"]/div[1]/button').click()
time.sleep(3)

html = driver.page_source
soup = BeautifulSoup(html, 'html.parser')
item_box = soup.find(name='div', attrs={'class':'list_content'})
# item_box

page_num = 0        # 현재 페이지 넘버
while_code = 0

while True :
    
    if while_code == 1:
        break

    target_page = f"https://www.clien.net/service/board/park?&od=T31&category=0&po={page_num}"
    driver.get(target_page)
    time.sleep(1)

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    item_box = soup.find(name='div', attrs={'class':'list_content'})

    for i in item_box :
        if len(i) > 1 :
            to_day = a + " 23:59:59"
            target_day = b
            
            # 게시글에 날짜가 지정되어 있으면 가져오고 에러로 가져오지 못하면 전 게시물 날짜 사용
            try :
                i.find(name='span', attrs={'class':'timestamp'}).text.strip()
                post_day = i.find(name='span', attrs={'class':'timestamp'}).text.strip()
            except :
                pass
            
            if  post_day > to_day :
                print(post_day, to_day)
                pass           
            
            elif post_day >= target_day :
                try :
                    print('href :',i.find(name='a', attrs={'class':'list_subject'})['href'] )


                    target_url = "https://www.clien.net"+i.find(name='a', attrs={'class':'list_subject'})['href']
                    print("target_url :", target_url)
                    driver.get(target_url)
                    time.sleep(1)
                    print("domain :", domain1)
    #                 print("keyword :", keyword)

                    post_html = driver.page_source
                    post_soup = BeautifulSoup(post_html, 'html.parser')
                    post_box = post_soup.find(name='div', attrs={'class':'content_view'})

                    # title
                    title1 = post_box.find(name='h3', attrs={'class':'post_subject'}).text.strip().split("\n")[0]     
                    print("title :", title1)

                    # user_id
                    try : # user_id 가 text형태인 경우
                        user1 = post_box.find(name='a', attrs={'class':'nickname'}).find('img')['alt']
                    except :
                        user1 = post_box.find(name='a', attrs={'class':'nickname'}).text.strip()            
                    print("user_id :", user1)

                    # time
                    time1 = post_box.find(name='div', attrs={'class':'post_author'}).find('span').text.strip()[:19]
                    print("작성 시간 :", time1)


                    # view
                    view_cnt1 = post_box.find(name='span', attrs={'class':'view_count'}).text.replace("\n", "").replace(",","")
                    print("조회수 :", view_cnt1)

                    # like
                    try :
                        like_cnt1 = post_box.find(name='div', attrs={'class':'post_title symph_row'}).find('div').text.strip()
                    except :
                        like_cnt1 = 0
                    print("공감/좋아요 수 :", like_cnt1)

                    # text
                    text1 = post_box.find(name='div', attrs={'post_article'}).text.strip().replace("\n","")
                    print('게시물 내용 :', text1) 

                    # com_cnt
                    try :                    
                        com_cnt1 = post_box.find(name='h3', attrs={'class':'post_subject'}).text.strip().split("\n")[-1]
                        com_cnt1 = int(com_cnt1)
                    except :
                        com_cnt1 = 0
                    print("댓글 수 :", com_cnt1)

                    # com_text
                    com_box = post_box.find(name='div', attrs={'class':'comment'})
                    com_list = []
                    user_list = []

                    for j in com_box :

                        if len(j) > 1 :  

                            try :
                                # comment_user_id
                                try : # user_id 가 text형태인 경우
                                    com_user = j.find(name='a', attrs={'class':'nickname'}).find('img')['alt']
                                except :
                                    com_user = j.find(name='a', attrs={'class':'nickname'}).text.strip()


                                com_text = j.find(name='div', attrs={'class':'comment_content'}).text.strip().replace("\n","")
                                com_list.append("작성자 : " + com_user + " :: " + com_text)
                                user_list.append(com_user)
                            except :
                                com_list.append("삭제된 댓글입니다.")

                    # print("게시물 작성자 :", user_list)
                    # print('게시물 댓글 :', com_list)
                    
                    domain2.append(domain1)
    #                 keyword2.append(keyword)
                    title2.append(title1)
                    user2.append(user1)
                    url2.append(target_url)
                    time2.append(time1)
                    view_cnt2.append(view_cnt1)
                    like_cnt2.append(like_cnt1)
                    text2.append(text1)
                    com_cnt2.append(com_cnt1)
                    com_user2.append(user_list)
                    com_text2.append(com_list)

                    print("\n")
                    
                except :
                    print('삭제된 게시물입니다.')
                    domain2.append(domain1)
    #                 keyword2.append(keyword)
                    title2.append('삭제된 게시물입니다.')
                    user2.append('삭제된 게시물입니다.')
                    url2.append('삭제된 게시물입니다.')
                    time2.append('삭제된 게시물입니다.')
                    view_cnt2.append(0)
                    like_cnt2.append(0)
                    text2.append('삭제된 게시물입니다.')
                    com_cnt2.append(0)
                    com_user2.append('삭제된 게시물입니다.')
                    com_text2.append('삭제된 게시물입니다.')


            else :
                print("크롤링을 완료했습니다.")
                while_code = 1
                break
        
    page_num += 1


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
df['com_text'] = pd.Series(com_text2)

df


# In[ ]:


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


# In[ ]:




