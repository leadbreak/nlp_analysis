#!/usr/bin/env python
# coding: utf-8

# In[ ]:

keyword_list = ['이낙연', '이재명', '정세균', '이광재']
start_day = 7 # 시작일은 7일 전
end_day = 1 # 끝일은 하루 전

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

# chromedriver 자동 설치
import chromedriver_autoinstaller

from selenium.webdriver.common.action_chains import ActionChains


# 작업 시간과 고유 dir 등 생성
n = time.localtime()
s = '%04d-%02d-%02d' % (n.tm_year, n.tm_mon, n.tm_mday)
s_time = time.time( )


a = datetime.now()-timedelta(days=start_day)
a = a.strftime('%Y.%m.%d')
b = datetime.now()-timedelta(days=end_day)
b = b.strftime('%Y.%m.%d')
print(a, b)


# In[3]:


print("=" *80)
print("         Naver & DAUM NEWS 크롤러입니다.")
print("=" *80)

f_dir = os.path.expanduser('~') + f'\\Desktop\\weekly\\{a}-{b}\\' # 운영체제 상관없이 바탕화면 'weekly' 폴더에 작업

print("=" *80)
print("다음뉴스 크롤링을 시작합니다.")
print("=" *80)


# In[4]:


# 저장될 파일 경로와 이름을 지정
# 파일을 저장할 폴더 위치를 만들고, 중복일 경우 해당 폴더를 삭제하고 새로 생성합니다.
try : 
    os.makedirs(f_dir)
except : pass
else : 
    os.chdir(f_dir)

# fc_name=f_dir+'\\'+f'.csv'


# In[5]:


# 크롤링 데이터가 들어갈 리스트 생성
domain2 = []    # 크롤링 도메인
keyword2 = []   # 크롤링 키워드
title2 = []     # 게시물 제목
user2 = []      # 게시물 작성자
date2 = []      # 게시물 작성 시간


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


def date_range(start, end):
    start = datetime.strptime(start, "%Y.%m.%d")
    end = datetime.strptime(end, "%Y.%m.%d")
    dates = [date.strftime("%Y.%m.%d") for date in pd.date_range(start, periods=(end-start).days+1)]
    return dates
    
dates = date_range(a, b)
print(dates)


# 1. 다음 뉴스 이동


for keyword in keyword_list :
    print("keyword:", keyword)

    for date in dates :
        
        page_num = 1

        while True :

            query_url= (f'https://search.daum.net/search?&at=more&cluster=n&dc=STC&ed={str(date.replace(".",""))}235959&https_on=on&p={page_num}&period=u&pg=1&q={keyword}&r=1&rc=1&sd={str(date.replace(".",""))}000000&sort=recency&w=news')
            driver.get(query_url)
            driver.implicitly_wait(5)

            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')        
            try :
                item_box = soup.find(name='ul', attrs={'id':'newsResultUL'}).find_all('li')  

                if len(title2) > 0 :            
                    if title2[-len(item_box)] == item_box[0].find(name='div', attrs={'class':'wrap_cont'}).find(name='div',attrs={'class':'wrap_tit mg_tit'}).text :
                        print(f"현재 페이지 {page_num+1}, 현재 키워드 : {keyword} 크롤링을 종료합니다.")
                        break

                for item in item_box :

                    if item.find(name='div', attrs={'class':'wrap_cont'}) :                

                        domain1 = "DaumNews"
                        keyword1 = keyword

                        news = item.find(name='div', attrs={'class':'wrap_cont'})

        #                 print(news)
        #                 break

                        user1 = news.find(name='span', attrs={'class':'f_nb date'}).text.split(" | ")[1]
                        date1 = date
                        # date1 = news.find(name='span', attrs={'class':'f_nb date'}).text.split(" | ")[0]

                        title1 = item.find(name='div',attrs={'class':'wrap_tit mg_tit'}).text
                        
#                         url1 = 

                        print(f'keyword : {keyword1}')
                        print(f'user : {user1}')
                        print(f'date : {date1}')
                        print(f'title : {title1}')

                        print("\n")

                        domain2.append(domain1)
                        keyword2.append(keyword1)
                        date2.append(date1)
                        title2.append(title1)
                        user2.append(user1)



                page_num += 1
            except :
                break


### Naver News


# 작업 시간과 고유 dir 등 생성
n = time.localtime()
s = '%04d-%02d-%02d' % (n.tm_year, n.tm_mon, n.tm_mday)
s_time = time.time( )


a = datetime.now()-timedelta(days=end_day)
a = a.strftime('%Y.%m.%d')
b = datetime.now()-timedelta(days=start_day)
b = b.strftime('%Y.%m.%d')
print(b, a)


# In[3]:

print("=" *80)

f_dir = os.path.expanduser('~') + f'\\Desktop\\weekly\\{b}-{a}\\' # 운영체제 상관없이 바탕화면 'weekly' 폴더에 작업

print("=" *80)
print("네이버뉴스 크롤링을 시작합니다.")
print("=" *80)


# In[4]:


# 저장될 파일 경로와 이름을 지정
# 파일을 저장할 폴더 위치를 만들고, 중복일 경우 해당 폴더를 삭제하고 새로 생성합니다.
try : 
    os.makedirs(f_dir)
except : pass
else : 
    os.chdir(f_dir)

fc_name=f_dir+'\\'+f'news.csv'



# 1. 네이버 이동

dates = date_range(b, a)

for keyword in keyword_list :
    print("keyword:", keyword)

    for date in dates :

        page_num = 0


        while True :

            query_url= (f'https://search.naver.com/search.naver?where=news&sm=tab_pge&query={keyword}&sort=1&photo=0&field=0&pd=3&ds={date}&de={date}&mynews=0&office_type=0&office_section_code=0&news_office_checked=&nso=so:dd,p:from{b}to{a},a:all&start={page_num}1')
            driver.get(query_url)
            driver.implicitly_wait(5) 
            

            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')        
            item_box = soup.find_all(name='li', attrs={'class':'bx'})
            
            if len(item_box) == 6 :
                print(f"현재 페이지 {page_num+1}, 현재 키워드 : {keyword} 크롤링을 종료합니다.")
                break

            for item in item_box :
                
                if item.find(name='div', attrs={'class':'news_area'}) :
                    

                    domain1 = "NaverNews"
                    keyword1 = keyword

                    news = item.find(name='div', attrs={'class':'news_area'})
                    
    #                 print(news)
    #                 break
    
                    user1 = news.find(name='div', attrs={'class':'news_info'}).find(name='a', attrs={'class':'info press'}).text

                    date1 = date                    
                    # try : 
                    #     date1 = news.find(name='div', attrs={'class':'news_info'}).find_all(name='span', attrs={'class':'info'})[-1].text
                    # except :
                    #     date1 = news.find(name='div', attrs={'class':'news_info'}).find(name='span', attrs={'class':'info'}).text
                    title1 = item.find(name='a',attrs={'class':'news_tit'})['title']

                    print(f'user : {user1}')
                    print(f'date : {date1}')
                    print(f'title : {title1}')

                    print("\n")

                    domain2.append(domain1)
                    keyword2.append(keyword1)
                    date2.append(date1)
                    title2.append(title1)
                    user2.append(user1)
                
                
                    
            page_num += 1


# In[8]:


df = pd.DataFrame()

df['domain'] = pd.Series(domain2)
df['keyword'] = pd.Series(keyword2)
df['user_text'] = pd.Series(title2)
df['channel'] = pd.Series(user2)
df['date'] = pd.Series(date2)

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
