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


a = datetime.now()-timedelta(days=1)
a = a.strftime('%Y.%m.%d')
b = datetime.now()-timedelta(days=7)
b = b.strftime('%Y.%m.%d')
print(b, a)


# In[3]:


print("=" *80)
print("         YOUTUBER 크롤러입니다.")
print("=" *80)

f_dir = os.path.expanduser('~') + f'\\Desktop\\weekly\\{b}-{a}\\' # 운영체제 상관없이 바탕화면 'crawler-bot' 폴더에 작업

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

fc_name=f_dir+'\\'+f'youtube.csv'


# In[5]:


# 크롤링 데이터가 들어갈 리스트 생성
domain2 = []    # 크롤링 도메인
title2 = []     # 게시물 제목
user2 = []      # 게시물 작성자
date2 = []     # 게시물 작성 시간
view2 = []     # 게시물 뷰 카운트

url2 = []      # 게시물 url
like2 = []     # 좋아요 - 싫어요
writer2 = []   # 댓글 작성자
com2 = []      # 댓글




# chromedriver-autoinstaller 이용
chromedriver_autoinstaller.install(cwd=True)

# HEADLESS MODE
options = webdriver.ChromeOptions()
# options.add_argument('headless')
options.add_argument('window-size=660,1080') 
# options.add_argument("--disable-gpu")
options.add_experimental_option('excludeSwitches', ['enable-logging'])
options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36")
args = ["hide_console", ]

# 알림창 끄기
options.add_experimental_option("prefs", {"profile.default_content_setting_values.notifications": 1})

# 웹사이트 접속 후 해당 메뉴로 이동
driver = webdriver.Chrome(options=options,service_args=args)
# driver.maximize_window()



domain1 = "youtube"


# In[8]:


url_list = [
    'https://www.youtube.com/c/%EB%94%B4%EC%A7%80%EB%B0%A9%EC%86%A1%EA%B5%AD/videos',
    'https://www.youtube.com/channel/UCu1FzjrHosuKGvgIx8oBi8w/videos',
    'https://www.youtube.com/c/%EC%9D%B4%EB%8F%99%ED%98%95TV/videos',
    'https://www.youtube.com/c/kimyongminTV/videos',
    'https://www.youtube.com/c/%EC%98%B3%EC%9D%80%EC%86%8C%EB%A6%AC/videos',
    'https://www.youtube.com/c/%EC%95%8C%EB%A6%AC%EB%AF%B8%ED%99%A9%ED%9D%AC%EB%91%90/videos',
    'https://www.youtube.com/channel/UCIMv9bOOGWGIfg6wPcRLItQ/videos'
]

# url2 = url_list


# In[9]:


# 각 유튜브 페이지로 이동
for url in tqdm(url_list) :

    driver.get(url)
    time.sleep(random.randint(3,4))
    
    element = driver.find_element_by_tag_name('body')
    element.send_keys(Keys.END)
    element.send_keys(Keys.PAGE_DOWN)
    element.send_keys(Keys.PAGE_DOWN)
    element.send_keys(Keys.PAGE_UP)
    time.sleep(random.randint(2,4))
    element.send_keys(Keys.PAGE_DOWN)
    element.send_keys(Keys.PAGE_DOWN)
    element.send_keys(Keys.PAGE_UP)
    element.send_keys(Keys.PAGE_DOWN)
    element.send_keys(Keys.PAGE_DOWN)
    time.sleep(random.randint(2,4))

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')    
    
    video_box = soup.find_all('ytd-grid-video-renderer')
    
    for video in video_box :
        video_url = f"https://www.youtube.com{video.find(name='a', attrs={'id':'thumbnail'})['href']}"
        
        driver.get(video_url)
        time.sleep(random.randint(3,4))
        
        element = driver.find_element_by_tag_name('body')
        element.send_keys(Keys.END)
        element.send_keys(Keys.PAGE_DOWN)
        element.send_keys(Keys.PAGE_DOWN)
        element.send_keys(Keys.PAGE_UP)
        element.send_keys(Keys.PAGE_DOWN)
        time.sleep(random.randint(2,4))
        element.send_keys(Keys.PAGE_DOWN)
  
            
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser') 
        
        try :
            date1 = soup.find(name='div',attrs={'id':'info-text'}).find(name='div', attrs={'id':'date'}).find('yt-formatted-string').text.replace("최초 공개: ","").replace(" ","").replace("실시간스트리밍시작일:","").replace("이전실시간스트리밍:","")
        except :
            print(soup.find(name='div',attrs={'id':'info-text'}).find(name='div', attrs={'id':'date'}))
            date1 = soup.find(name='div', attrs={'id':'date'}).find('yt-formatted-string').text
            
        if "시간전" in date1 or "스트리밍시작" in date1:
            date1 = datetime.now().strftime('%Y.%m.%d').strip()
        else :
            date1 = date1[:-1].strip()
        
        if len(date1) != 10 :
#             print("기존 1 :", date1)
            date1 = date1[:5] +"0" + date1[5:]
        if len(date1) != 10 :
#             print("기존 2 :", date1)
            date1 = date1[:8] +"0" + date1[8:]      
        
        print("date :", date1)
        
        if date1 > a :
            pass
            print("\n")
            print("해당 게시물을 건너뜁니다.")
            print(video_url)
            print(a, "<",date1)     
            
        elif date1 >= b :
            print("\n")
            print("해당 게시물 댓글을 크롤링합니다.")
            print(video_url)
            print(b, "<=",date1)
            
            domain2.append(domain1)
            url2.append(video_url)

            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            
            title1 = soup.find(name='h1', attrs={'class':'title style-scope ytd-video-primary-info-renderer'}).text.strip()
            # print('title : ', title1)
            title2.append(title1)
            
            user1 = soup.find(name='div', attrs={'id':'text-container'}).text.strip()
            # print("채널명 :", user1)
            user2.append(user1)
            
            date2.append(date1)

            black_box = soup.find_all(name='yt-formatted-string', attrs={'id':'text', 'class':'style-scope ytd-toggle-button-renderer style-text'})
                        
            for box in black_box :
                try :        
                    text = box['aria-label']
                    if "좋아요 " in text :
                        like1 = text.replace('좋아요 ', '').replace(',','').replace('개','').strip()
                    elif "싫어요 " in text :
                        dislike1 = text.replace('싫어요 ', '').replace(',','').replace('개','').strip()
                        break
                except :
                    pass

            if like1 == "없음" :
                like1 = 0
            if dislike1 == "없음" :
                dislike1 = 0

            net_like = int(like1) - int(dislike1)
            # print('net_like :', net_like)
            like2.append(net_like)

            element = driver.find_element_by_tag_name('body')
            element.send_keys(Keys.END)
            element.send_keys(Keys.PAGE_DOWN)
            element.send_keys(Keys.PAGE_DOWN)
            element.send_keys(Keys.PAGE_UP)
            time.sleep(random.randint(2,4))
            element.send_keys(Keys.PAGE_DOWN)
            html = driver.page_source

            old_box = len(html)

            while True:
                
                element.send_keys(Keys.PAGE_UP)
                element.send_keys(Keys.PAGE_DOWN)
                element.send_keys(Keys.PAGE_DOWN)
                element.send_keys(Keys.PAGE_DOWN)
                time.sleep(3)
                element.send_keys(Keys.PAGE_UP)
                element.send_keys(Keys.PAGE_DOWN)
                element.send_keys(Keys.PAGE_DOWN)
                element.send_keys(Keys.PAGE_DOWN)
                time.sleep(3)
                element.send_keys(Keys.PAGE_UP)
                element.send_keys(Keys.PAGE_DOWN)
                element.send_keys(Keys.PAGE_DOWN)
                time.sleep(3)

                html = driver.page_source
                
                new_box = len(html)

        #         print(new_box, old_box)

                if new_box == old_box:
                    break
                else :
#                     print("스크롤을 내립니다.")
                    pass

                old_box = new_box
            
            time.sleep(3)
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')

            comment_box = soup.find_all(name='div', attrs={'id':'contents'})[-1].find_all(name='ytd-comment-thread-renderer', attrs={'class':'style-scope ytd-item-section-renderer'})
            writers = []
            comments = []
            for comment in comment_box :       

                try :
                    writer1 = comment.find(name='a', attrs={'id':'author-text'}).text.strip()
                    com1 = comment.find(name='yt-formatted-string', attrs={'id':'content-text'}).text.strip()
                    writers.append(writer1)
                    comments.append(com1)
                except :
                    print("\n예외상황 :")
                    print(comment.text.strip().replace("\n", ""))

            # print("댓글 작성자 :", writers)
            # print(f"댓글 내용 :", comments)
            # print("\n")

            writer2.append(writers)
            com2.append(comments)                 
            
            
        else :
            print("타겟 게시물이 아님")
            print(video_url)
            print(b, ">", date1)
            break
    
df = pd.DataFrame()

df['domain'] = pd.Series(domain2)
df['title'] = pd.Series(title2)
df['channel'] = pd.Series(user2)
df['date'] = pd.Series(date2)
df['url'] = pd.Series(url2)
df['like'] = pd.Series(like2)
df['commentor'] = pd.Series(writer2)
df['comment'] = pd.Series(com2)

# csv 형태로 저장하기
df.to_csv(fc_name,encoding="utf-8-sig",index=False)

while True :
    
    re_list = []
    url_list = []

    for i in range(len(df)) :
        if len(df['commentor'][i]) < 1 :
            re_list.append(i)
            url_list.append(df['url'][i])
    
    if len(re_list) < 1 :
        break

    re_writer2 = []
    re_com2 = []

    for url in tqdm(url_list) :

        driver.get(url)

        time.sleep(random.randint(3,4))

        element = driver.find_element_by_tag_name('body')
        element.send_keys(Keys.END)
        element.send_keys(Keys.PAGE_DOWN)
        element.send_keys(Keys.PAGE_DOWN)
        element.send_keys(Keys.PAGE_UP)
        element.send_keys(Keys.PAGE_DOWN)
        time.sleep(random.randint(2,4))
        element.send_keys(Keys.PAGE_DOWN)


        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')       

        element = driver.find_element_by_tag_name('body')
        element.send_keys(Keys.END)
        element.send_keys(Keys.PAGE_DOWN)
        element.send_keys(Keys.PAGE_DOWN)
        element.send_keys(Keys.PAGE_UP)
        time.sleep(random.randint(2,4))
        element.send_keys(Keys.PAGE_DOWN)
        html = driver.page_source

        old_box = len(html)

        while True:

            element.send_keys(Keys.PAGE_UP)
            element.send_keys(Keys.PAGE_DOWN)
            element.send_keys(Keys.PAGE_DOWN)
            element.send_keys(Keys.PAGE_DOWN)
            time.sleep(3)
            element.send_keys(Keys.PAGE_UP)
            element.send_keys(Keys.PAGE_DOWN)
            element.send_keys(Keys.PAGE_DOWN)
            element.send_keys(Keys.PAGE_DOWN)
            time.sleep(3)
            element.send_keys(Keys.PAGE_UP)
            element.send_keys(Keys.PAGE_DOWN)
            element.send_keys(Keys.PAGE_DOWN)
            time.sleep(3)

            html = driver.page_source

            new_box = len(html)

            if new_box == old_box:
                break
            else :
    #                     print("스크롤을 내립니다.")
                pass

            old_box = new_box

        time.sleep(3)
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        comment_box = soup.find_all(name='div', attrs={'id':'contents'})[-1].find_all(name='ytd-comment-thread-renderer', attrs={'class':'style-scope ytd-item-section-renderer'})
        writers = []
        comments = []
        for comment in comment_box :       

            try :
                writer1 = comment.find(name='a', attrs={'id':'author-text'}).text.strip()
                com1 = comment.find(name='yt-formatted-string', attrs={'id':'content-text'}).text.strip()
                writers.append(writer1)
                comments.append(com1)
            except :
                print("\n예외상황 :")
                print(comment.text.strip().replace("\n", ""))

        # print("댓글 작성자 :", writers)
        # print(f"댓글 내용 :", comments)
        # print("\n")

        re_writer2.append(writers)
        re_com2.append(comments)                 

    for j in range(len(re_list)) :
        df['commentor'][re_list[j]] = re_writer2[j]
        df['comment'][re_list[j]] = re_com2[j]

    df
    
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