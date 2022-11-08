
import time, pyautogui, pyperclip


def click_every_5s() :
    # time.sleep(50)
    print("정체 페이지 모니터링을 시작합니다.")
    
    while True :
        #1
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
            pyautogui.click(1846,214)

            if url1 == url2 :
                print("정체 페이지 발생 - 새로고침합니다.")
                print("url1 :", url1)
                print("url2 :", url2)
                pyautogui.click(x=110, y=75)
                time.sleep(10)
                pyautogui.click(1846,214)
        except :
            time.sleep(10)
        time.sleep(1)
        
        # #2
        # try :
                
        #     pyperclip.copy("") # pyperclip 초기화
        #     pyautogui.click(205,605)
        #     pyautogui.hotkey('ctrl', 'c')
        #     url1 = pyperclip.paste()
        #     # pyautogui.click(1780,405)
        #     pyautogui.click(876,388)

        #     time.sleep(10)

        #     pyperclip.copy("") # pyperclip 초기화
        #     pyautogui.click(205,605)
        #     pyautogui.hotkey('ctrl', 'c')
        #     url2 = pyperclip.paste()
        #     pyautogui.click(876,388)

        #     if len(url1) > 0 and url1 == url2 :
        #         print("정체 페이지 발생 - 새로고침합니다.")
        #         print("url1 :", url1)
        #         print("url2 :", url2)
        #         pyautogui.click(x=112, y=588)
        #         time.sleep(10)
                # pyautogui.click(1846,214)
        # except :
        #     time.sleep(10)
        # time.sleep(1)
        #3
        try :
                
            pyperclip.copy("") # pyperclip 초기화
            pyautogui.click(1173,73)
            pyautogui.hotkey('ctrl', 'c')
            url1 = pyperclip.paste()
            pyautogui.click(1846,214)
            # pyautogui.moveTo(1524,240)

            time.sleep(10)

            pyperclip.copy("") # pyperclip 초기화
            pyautogui.click(1173,73)
            pyautogui.hotkey('ctrl', 'c')
            url2 = pyperclip.paste()
            pyautogui.click(1865,722)
            # pyautogui.click(1524,240)

            if len(url1) > 0 and url1 == url2 :
                print("정체 페이지 발생 - 새로고침합니다.")
                print("url1 :", url1)
                print("url2 :", url2)
                pyautogui.click(x=1074, y=75)
                time.sleep(10)
                pyautogui.click(1865,722)
               
        except :
            time.sleep(10)
        time.sleep(1)
        
        #4
        try :
                
            pyperclip.copy("") # pyperclip 초기화
            pyautogui.click(1173,591)
            pyautogui.hotkey('ctrl', 'c')
            url1 = pyperclip.paste()
            # pyautogui.click(1780,405)
            pyautogui.click(1865,722)

            time.sleep(10)

            pyperclip.copy("") # pyperclip 초기화
            pyautogui.click(1173,591)
            pyautogui.hotkey('ctrl', 'c')
            url2 = pyperclip.paste()
            pyautogui.click(876,388)
            # pyautogui.click(1601,750)

            if len(url1) > 0 and url1 == url2 :
                print("정체 페이지 발생 - 새로고침합니다.")
                print("url1 :", url1)
                print("url2 :", url2)
                pyautogui.click(x=1074, y=591)
                time.sleep(10)
                pyautogui.click(876,388)
        except :
            time.sleep(10)
        
        time.sleep(1)
            

if __name__=="__main__" :
    click_every_5s()