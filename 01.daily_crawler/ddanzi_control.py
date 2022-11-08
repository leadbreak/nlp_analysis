
import time, pyautogui, pyperclip


def click_every_5s() :
    time.sleep(10)
    print("정체 페이지 모니터링을 시작합니다.")
    
    while True :
        try :
                
            pyperclip.copy("") # pyperclip 초기화
            pyautogui.click(214,78)
            pyautogui.hotkey('ctrl', 'c')
            url1 = pyperclip.paste()
            # pyautogui.click(1780,405)
            pyautogui.click(876,388)

            time.sleep(10)

            pyperclip.copy("") # pyperclip 초기화
            pyautogui.click(214,78)
            pyautogui.hotkey('ctrl', 'c')
            url2 = pyperclip.paste()
            # pyautogui.click(1780,405)
            pyautogui.click(876,388)

            if url1 == url2 :
                print("정체 페이지 발생 - 새로고침합니다.")
                print("url1 :", url1)
                print("url2 :", url2)
                pyautogui.click(x=110, y=75)
                time.sleep(10)
        except :
            time.sleep(10)
            

if __name__=="__main__" :
    click_every_5s()