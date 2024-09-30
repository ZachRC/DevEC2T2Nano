import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException, ElementNotInteractableException
from selenium.webdriver.common.keys import Keys
import json
import time
import os
import random
import sys

def load_cookies(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

def print_flush(message):
    print(message, flush=True)

def random_sleep(min_time=1, max_time=5):
    time.sleep(random.uniform(min_time, max_time))

def random_scroll(driver):
    scroll_amount = random.randint(300, 1000)
    driver.execute_script(f"window.scrollBy(0, {scroll_amount});")

def random_action(driver):
    actions = [
        lambda: driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.HOME),
        lambda: driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END),
        lambda: random_scroll(driver),
        lambda: driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_DOWN),
        lambda: driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_UP),
    ]
    random.choice(actions)()
    print_flush(f"Performed random action: {actions.index(random.choice(actions))}")

def interact_with_video(driver):
    try:
        video = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "div[data-e2e='recommend-list-item-container']"))
        )
        video.click()
        print_flush("Clicked on a video")
        random_sleep(3, 10)
        
        actions = [
            lambda: driver.find_element(By.CSS_SELECTOR, "[data-e2e='like-icon']").click(),
            lambda: driver.find_element(By.CSS_SELECTOR, "[data-e2e='comment-icon']").click(),
            lambda: driver.find_element(By.CSS_SELECTOR, "[data-e2e='share-icon']").click(),
        ]
        
        for _ in range(random.randint(1, 3)):
            try:
                random.choice(actions)()
                print_flush(f"Performed action on video: {actions.index(random.choice(actions))}")
                random_sleep()
            except:
                pass
        
        driver.back()
        print_flush("Returned to the main page")
    except:
        print_flush("Failed to interact with video")

def login_with_cookies():
    options = uc.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--headless")
    options.binary_location = os.environ.get("CHROME_BIN")
    
    print_flush("Starting the browser...")
    driver = uc.Chrome(options=options, driver_executable_path=os.environ.get("CHROMEDRIVER_PATH"))
    
    try:
        print_flush("Navigating to TikTok...")
        driver.get("https://www.tiktok.com/")
        
        print_flush("Loading cookies...")
        cookies = load_cookies('/app/cookies/1.json')
        for cookie in cookies:
            if 'sameSite' in cookie:
                if cookie['sameSite'] == 'unspecified':
                    cookie['sameSite'] = 'Lax'
                elif cookie['sameSite'] == 'no_restriction':
                    cookie['sameSite'] = 'None'
                else:
                    cookie['sameSite'] = cookie['sameSite'].capitalize()
            driver.add_cookie(cookie)
        
        print_flush("Refreshing the page...")
        driver.refresh()
        
        print_flush("Waiting for the page to load...")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        
        print_flush("Logged in successfully")
        
        for i in range(random.randint(20, 30)):
            print_flush(f"Iteration {i+1}")
            random_action(driver)
            random_sleep()
            
            if random.random() < 0.3:
                interact_with_video(driver)
            
            if random.random() < 0.1:
                search_term = random.choice(["funny", "cats", "dance", "food", "travel"])
                search_box = driver.find_element(By.CSS_SELECTOR, "input[data-e2e='search-user-input']")
                search_box.clear()
                search_box.send_keys(search_term)
                search_box.send_keys(Keys.RETURN)
                print_flush(f"Searched for: {search_term}")
                random_sleep(3, 7)
        
        print_flush("Finished scrolling and interacting. Exiting...")
    
    except Exception as e:
        print_flush(f"An error occurred: {str(e)}")
    
    finally:
        print_flush("Closing the browser...")
        driver.quit()

if __name__ == "__main__":
    login_with_cookies()