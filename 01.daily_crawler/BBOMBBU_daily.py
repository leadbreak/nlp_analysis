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
import re

# chromedriver 자동 설치
import chromedriver_autoinstaller

from selenium.webdriver.common.action_chains import ActionChains


# In[ ]:


# 작업 시간과 고유 dir 등 생성
n = time.localtime()
s = '%04d-%02d-%02d' % (n.tm_year, n.tm_mon, n.tm_mday)
s_time = time.time( )

a = datetime.now()-timedelta(days=1)
a = a.strftime('%Y.%m.%d')
b = datetime.now()-timedelta(days=1)
b = b.strftime('%Y.%m.%d')
print(b, a)


# In[ ]:


print("=" *80)
print("         뽐뿌 크롤러입니다.")
print("=" *80)

f_dir = os.path.expanduser('~') + f'\\Desktop\\daily\\{b.replace(".","-")}\\' # 운영체제 상관없이 바탕화면 'crawler-bot' 폴더에 작업

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

fc_name=f_dir+'\\'+f'bbombbu.csv'


# In[ ]:


# 크롤링 데이터가 들어갈 리스트 생성
domain2 = []    # 크롤링 도메인
title2 = []     # 게시물 제목
user2 = []      # 게시물 작성자
url2 = []       # 게시물 url
date2 = []      # 게시물 작성 시간
text2 = []      # 게시물 내용
com_user2 = []  # 댓글 user
com_text2 = []  # 댓글 user_id & text


# In[ ]:


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


# In[ ]:


# 1. 뽐뿌 크롤링
query_url= ('http://www.ppomppu.co.kr/zboard/zboard.php?id=issue')

driver.get(query_url)
driver.implicitly_wait(5)


# In[ ]:


domain1 = "뽐뿌"
print("==========",domain1,"크롤링 진행 중 ==========")

page_num = 1
while_code = 0

while True :
    
    if while_code == 1 :
        break

    target_url = f'http://www.ppomppu.co.kr/zboard/zboard.php?id=issue&page={page_num}'
    driver.get(target_url)
    print("\n")
    print(f'현재 페이지 {page_num}')
    time.sleep(2)
    
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    item_box = soup.find_all('tr')

    for item in item_box :
        try :
            item['class'][0]
            # 공지 외 타겟 게시물 분류
            if len(item['class'][0]) == 5 :
                
                for td in item :
                    try :
                        td['title']
                        date1 = "20" + td['title'][:8]                        
                    except :
                        pass
                
                print("date :", date1)
                
                if date1 > a :
                    print("scout1", date1, ">", a)
                    pass
                
                elif date1 >= b :
                    
                    
                    print(f"scout2 {date1} >= {b}")
                    url1 = f"http://www.ppomppu.co.kr/zboard/{item.find_all('td',class_='list_vspace')[2].find('a')['href']}"
                    print("url :", url1)
                    driver.get(url1)
                    time.sleep(1)
                    
                    html = driver.page_source
                    soup = BeautifulSoup(html, 'html.parser')
                
                    
#                     print(soup.find(name='font', attrs={'class':'view_title2'}))
                          
                    title1 = soup.find(name='font', attrs={'class':'view_title2'}).text.strip()
                    
                    if len(title2) > 0 and title1 == title2[-1] :
                        print("중복 게시물")
                        pass
                    else :

                        print("title :", title1)
                        
                        try :
                            user1 = soup.find(name='font', attrs={'class':'view_name'}).text.strip()
                        except :
                            user1 = soup.find(name='span', title=True).find('a').find('img')['alt']
                        print("user_name :", user1)

                        try :
                            text1 = soup.find(name='td', attrs={'class':'board-contents'}).text.replace("&nbsp;","").replace("\n", "").strip()
                        except :
                            print("내용 없음. 제목으로 대체")
                            text1 = title1
                            
                        print("user_text :", text1)

                        user_list = []
                        com_list = []

                        com_box = soup.find(name='div', attrs={'id':'quote'}).find_all('div', attrs={'class':'comment_line'})

                        for div in com_box :           

                            user_name = div.find('b').text
                            com_text = div.find(name='div', attrs={'id':re.compile('^commentContent')}).text.strip()

                            full_text = f'작성자 : {user_name} :: {com_text}'
                            user_list.append(user_name)
                            com_list.append(full_text)


                        # print("댓글 작성자 :", user_list)
                        # print("댓글 전체 :", com_list)
                        
                        domain2.append(domain1)
                        url2.append(url1)
                        date2.append(date1)
                        title2.append(title1)
                        user2.append(user1)
                        text2.append(text1)
                        com_user2.append(user_list)
                        com_text2.append(com_list) 

                        print("\n")          
                          
                          
                          
                else :
                    print(f"scout3 {date1} < {b}")
                    while_code=1
                    break
                    
                


        except :
            pass
    page_num += 1


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


df


# In[ ]:




