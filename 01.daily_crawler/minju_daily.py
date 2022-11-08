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

# chromedriver 자동 설치
import chromedriver_autoinstaller

from selenium.webdriver.common.action_chains import ActionChains


# In[2]:


# 작업 시간과 고유 dir 등 생성
n = time.localtime()
s = '%04d-%02d-%02d' % (n.tm_year, n.tm_mon, n.tm_mday)
s_time = time.time( )

from_day = 1 # 7일 전부터
to_day = 1 # 1일 전부터

a = datetime.now()-timedelta(days=to_day)
a = a.strftime('%Y-%m-%d')
b = datetime.now()-timedelta(days=from_day)
b = b.strftime('%Y-%m-%d')
print(b, a)


# In[3]:


print("=" *80)
print("         민주당 권리당원게시판 크롤러입니다.")
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

fc_name=f_dir+'\\'+f'minju.csv'


# In[5]:


# 크롤링 데이터가 들어갈 리스트 생성
domain2 = []    # 크롤링 도메인
keyword2 = []   # 크롤링 키워드
title2 = []     # 게시물 제목
user2 = []      # 게시물 작성자
url2 = []       # 게시물 url
date2 = []      # 게시물 작성 시간
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


# 1. 권리당원 게시판 접속
query_url= ('https://theminjoo.kr/membership/login')

driver.get(query_url)
driver.implicitly_wait(5)


# In[8]:


# login

minju_id = 'gorviano'
minju_pw = 'soop*dive20'

# id 입력
driver.find_element_by_id('login_id').click()
for i in minju_id :
    time.sleep(0.1)
    driver.find_element_by_id('login_id').send_keys(i)

# pw 입력
driver.find_element_by_id('login_pw').click()
for i in minju_pw :
    time.sleep(0.1)
    driver.find_element_by_id('login_pw').send_keys(i)
    
driver.find_element_by_id('login_pw').send_keys(Keys.ENTER)
time.sleep(2)


# In[9]:


# 권리당원 게시판 이동
query_url= ('https://theminjoo.kr/board/lists/rmboard?page=1')

driver.get(query_url)
time.sleep(2)


# In[10]:


domain1 = "권리당원게시판"


# In[11]:


# 1차 크롤링 

page_num = 1
while_code = 0

while True :
    
    if while_code == 1 :
        break
    
    html = driver.page_source
    soup = BeautifulSoup(html, 'lxml')
    item_box = soup.find('ul', id='boardPostList').find_all('li', class_=False)
    
    for item in item_box :
        date1 = item.find('td', class_='date').text.replace("작성일:","")
        
        
        if "초" in date1 or "분" in date1 or "시간" in date1 :
            date1 = a
        elif "1일전" in date1 :
            tmp_date = datetime.now()-timedelta(days=to_day+1)
            tmp_date = tmp_date.strftime("%Y-%m-%d")
            date1 = tmp_date
        elif "2일전" in date1 :
            tmp_date = datetime.now()-timedelta(days=to_day+2)
            tmp_date = tmp_date.strftime("%Y-%m-%d")
            date1 = tmp_date
        else :
            date1 = "20" + date1
            
        print(date1)
        
        if date1 > a :
            pass
        
        elif date1 >= b : 

            title1 = item.find('div', class_='subject clearfix').find('a', href=True).text
            
            name1 = item.find('a', href=True).text
            url1 = "https://theminjoo.kr" + item.find('div', class_='subject clearfix').find('a', href=True)['href']
            
            print(title1)
            print(name1)
            print(url1)
            print("\n")
            
            domain2.append(domain1)
            title2.append(title1)
            date2.append(date1)
            user2.append(name1)
            url2.append(url1)
            
        
        else :
            while_code = 1
            break
            
    page_num += 1
    driver.get(f"https://theminjoo.kr/board/lists/rmboard?page={page_num}")
    time.sleep(random.randint(1,2))


# In[12]:


def scroll_down() :
    element = driver.find_element_by_tag_name('body')
    element.send_keys(Keys.END)
    element.send_keys(Keys.PAGE_DOWN)


# In[ ]:


# 2차 크롤링

for url in tqdm(url2) :
    driver.get(url)
    print(url)
    scroll_down()
    time.sleep(1)

    while True :

        try :
            scroll_down()
            driver.find_element_by_class_name("more_btn").click() 
        except :
            break
        
        time.sleep(1)

    html = driver.page_source
    soup = BeautifulSoup(html, 'lxml')
    
    try :

        text1 = soup.find('div', class_='bv_middle').text.strip()
        print(text1)

        com_box = soup.find('ul', id='boardCmtLists').find_all('li')

        com_user1 = []
        com_text1 = []
        for com in com_box :
            com_name = com.find('div', class_='mem_nick').text
            com_text = com.find('div', class_='reply_cnt').text

            if "님에 의해 삭제된 글입니다." in com_text :
                pass
            else :
                com_user1.append(com_name)
                com_text1.append(f"작성자 : {com_name} :: {com_text}")
    except :
        print("비밀글입니다.")
        text1 = "비밀글"
        com_user1 = []
        com_text1 = []     

    print(com_user1)
    print(com_text1)
    text2.append(text1)
    com_user2.append(com_user1)
    com_text2.append(com_text1)


# In[ ]:


df = pd.DataFrame()

df['domain'] = pd.Series(domain2)
# df['keyword'] = pd.Series(keyword2)
df['title'] = pd.Series(title2)
df['user_name'] = pd.Series(user2)
df['url'] = pd.Series(url2)
df['date'] = pd.Series(date2)
df['user_text'] = pd.Series(text2)
df['com_user'] = pd.Series(com_user2)
df['com_text'] = pd.Series(com_text2)

df


# In[ ]:


# for i in range(len(df)) :
#     if len(df['title'][i]) > len(df['user_text'][i]) * 0.9 :
#         df['user_text'][i] = df['title'][i]


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

