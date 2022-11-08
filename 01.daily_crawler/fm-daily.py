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
import requests, re

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
print(a, b)


# In[3]:


print("=" *80)
print("         FM 정치/시사 게시판 크롤러입니다.")
print("=" *80)

f_dir = os.path.expanduser('~') + f'\\Desktop\\daily\\{a}\\' # 운영체제 상관없이 바탕화면 'crawler-bot' 폴더에 작업

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

fc_name=f_dir+'\\'+f'fm.csv'


# In[5]:


# 크롤링 데이터가 들어갈 리스트 생성
domain2 = []    # 크롤링 도메인
title2 = []     # 게시물 제목
user2 = []      # 게시물 작성자
url2 = []       # 게시물 url
time2 = []      # 게시물 작성 시간
view_cnt2 = []  # 게시물 뷰 카운트
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


domain1 = "fm"
print("==========",domain1,"크롤링 진행 중 ==========")


# In[8]:


def drive_on() :
#     # chromedriver-autoinstaller 이용
#     chromedriver_autoinstaller.install(cwd=True)

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


# In[ ]:


page_num = 10
while_code = 0

while True :
    if while_code == 1 :
        print("1차 데이터 수집 완료")
        print("2차 데이터 수집으로 넘어갑니다.")
        break
    
    
    driver.get(f'https://www.fmkorea.com/index.php?mid=news&page={page_num}')
    time.sleep(2)
    html = driver.page_source
    soup = BeautifulSoup(html, 'lxml')
    post_box = soup.find('tbody').find_all('tr', class_=False)
    
    for post in post_box :
        
        post_url = "https://www.fmkorea.com/" + post.find("td", class_=re.compile('title')).find('a')['href']
        print("url :", post_url)
        
        try :

            driver.get(post_url)
            time.sleep(1)
            html2 = driver.page_source
            soup2 = BeautifulSoup(html2, 'lxml')
            # print(soup2.select('#bd_4180795_3604166605 > div.rd.rd_nav_style2.clear'))
            # print("aa:", soup2.find('span', class_='date m_no'))
            # print("bb:", soup2.find('span', class_='date m_no').text)
            post_date = soup2.find('span', class_='date m_no').text[:10].replace(".","-")
        except :

            post_date = post_date
                
        if post_date > b :
#             page_num += 1
            print(post_date, " > ", b)
            print("페이지를 넘깁니다.\n")
            break
            
        elif post_date >= a :
            if post_url not in url2 :                

                domain1 = domain1
                title1 = soup2.find('span', class_='np_18px_span').text
                user1 = soup2.find('a', class_=re.compile('nick member')).text
                url1 = post_url


                view1 = soup2.find_all(class_='side fr')[0].find('b').text
                try :
                    com_cnt1 = soup2.find(class_='ui_font bubble').find('b').text
                except :
                    com_cnt1 = 0

                text1 = soup2.find('article').text
                com_user1 = []
                com_text1 = []

                try :

                    com_box = soup2.find(class_='fdb_lst_ul').find_all('li')

                    for com in com_box :

                        com_user = com.find('a', class_=re.compile('member_')).text

                        try :
                            delete = com.find('a', class_='findParent').text
                            comment = com.find('div', class_=re.compile('comment_')).text
                            comment.replace(delete, "")
                        except :
                            comment = com.find('div', class_=re.compile('comment_')).text

                        com_user1.append(com_user)
                        com_text1.append(f"작성자 : {com_user} :: {comment}")
                except :
                    com_user1.append("")
                    com_text1.append("")                     

                print("게시일 :", post_date)
                print("제목 :", title1)
                print("작성자 :", user1)
                print("url :", url1)
                print("조회수 :", view1)
                print("게시물 내용 :", text1)
                print("댓글수 :", com_cnt1)
                print("댓글 작성자 :", com_user1)
                print("댓글 내용 :", com_text1)
                print("\n")

                domain2.append(domain1)
                title2.append(title1)
                time2.append(post_date)
                user2.append(user1)
                url2.append(url1)
                view_cnt2.append(view1)
                com_cnt2.append(com_cnt1)
                text2.append(text1)
                com_user2.append(com_user1)
                com_text2.append(com_text1)

                time.sleep(1)
        
            
        else :
            while_code = 1
            break

    page_num += 1
    driver.delete_all_cookies()


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
# df['like_cnt'] = pd.Series(like_cnt2)
df['user_text'] = pd.Series(text2)
df['com_cnt'] = pd.Series(com_cnt2)
df['com_user'] = pd.Series(com_user2)
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


# ## 
