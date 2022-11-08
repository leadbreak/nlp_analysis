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
print("         twitter 자유게시판 크롤러입니다.")
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

fc_name=f_dir+'\\'+f'twitter.csv'


# In[5]:


# 크롤링 데이터가 들어갈 리스트 생성
domain2 = []    # 크롤링 도메인
keyword2 = []   # 크롤링 키워드
user2 = []      # 게시물 작성자
url2 = []       # 게시물 url
time2 = []      # 게시물 작성 시간
text2 = []      # 게시물 내용


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


domain1 = "twitter"
print("==========",domain1,"크롤링 진행 중 ==========")


# In[8]:


def scroll_down() :
    element = driver.find_element_by_tag_name('body')
    element.send_keys(Keys.END)
    element.send_keys(Keys.PAGE_DOWN)
    element.send_keys(Keys.PAGE_DOWN)
    element.send_keys(Keys.PAGE_UP)
    element.send_keys(Keys.PAGE_DOWN)
    element.send_keys(Keys.PAGE_UP)
    element.send_keys(Keys.PAGE_UP)
    element.send_keys(Keys.PAGE_DOWN)
    element.send_keys(Keys.PAGE_UP)
    element.send_keys(Keys.PAGE_UP)
    time.sleep(random.randint(2,3))
    element.send_keys(Keys.PAGE_DOWN)
    element.send_keys(Keys.PAGE_DOWN)
    element.send_keys(Keys.PAGE_DOWN)
    time.sleep(random.randint(1,3) + random.randint(0,1) + random.randint(0,1) + random.randint(0,1))


# In[ ]:

# keyword_list = ["정세균"]
keyword_list = ['이낙연', '이재명', '정세균', '이광재']

for keyword in keyword_list :
    driver.get(f'https://twitter.com/search?q={keyword}&src=typed_query&f=live')
    time.sleep(3)

    while_code = 0

    while True :

        if while_code == 1 :
            break

        html = driver.page_source
        soup = BeautifulSoup(html, 'lxml')
        box = soup.find_all('div', attrs={'style':re.compile('position: absolute; width: 100%;')})
        for div in box :
            
            try :
                date = div.find_all('time', datetime = True)[0]['datetime'][:10]
            except :
                date = date
                print("exception :", div.find_all('time', datetime = True))
            
            if date < a :
                while_code = 1
                
            if while_code == 1 :
                break
                
            target = div.find_all('span', text=True)
            text = ""
            cnt = 0

            context = ""
            before = "?"
            for line in target :


                target_line = line.text.strip().replace("\n"," ").replace("이 스레드 보기","")
                if len(target_line) > 0 :

                    text += target_line
            #         print(cnt, target_line)

                    if cnt == 0 :
                        print("글쓴이 :", target_line)
                        user2.append(target_line)
                    elif target_line[0] == "@" :
                        print("아이디 :", target_line)
                    elif before == "·" :
                        if target_line not in context and len(target_line) > 1:
                            context += target_line

                    if target_line == "·" :
                        before = target_line
                    else :
                        pass

                    cnt += 1

            print("날짜 :", date)
            print("본문 :", context)
            print("원문 :", text)
            print("\n")

            domain2.append(domain1)
            keyword2.append(keyword)
            time2.append(date)
            text2.append(context)




        scroll_down()
        
    print(f"keyword를 변경합니다.")


# In[ ]:


df = pd.DataFrame()

df['domain'] = pd.Series(domain2)
df['keyword'] = pd.Series(keyword2)
df['date'] = pd.Series(time2)
df['user_text'] = pd.Series(text2)

df


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

