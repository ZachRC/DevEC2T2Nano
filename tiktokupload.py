import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import json
import time
import os
import random

def load_cookies(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

def login_with_cookies():
    options = uc.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--headless")
    options.binary_location = os.environ.get("CHROME_BIN")
    
    print("Starting the browser...")
    driver = uc.Chrome(
        options=options,
        driver_executable_path=os.environ.get("CHROMEDRIVER_PATH")
    )
    
    try:
        print("Navigating to TikTok...")
        driver.get("https://www.tiktok.com/")
        
        print("Loading cookies...")
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
        
        print("Refreshing the page...")
        driver.refresh()
        
        print("Waiting for the page to load...")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        print("Logged in successfully")
        
        scroll_count = 0
        while scroll_count < 10:
            # Scroll down
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            print(f"Scrolling down the page (scroll {scroll_count + 1})")
            time.sleep(random.uniform(2, 4))
            scroll_count += 1
            
            # Try to find and interact with random elements
            try:
                clickable_elements = driver.find_elements(By.CSS_SELECTOR, "button, a, div[role='button']")
                if clickable_elements:
                    element = random.choice(clickable_elements)
                    element_text = element.text.strip() if element.text.strip() else "Unnamed element"
                    print(f"Clicking on: {element_text}")
                    element.click()
                    time.sleep(random.uniform(2, 4))
                    
                    # Go back to the main page
                    driver.back()
                    print("Returned to the previous page")
                    time.sleep(random.uniform(1, 3))
                else:
                    print("No clickable elements found on this page")
            except Exception as e:
                print(f"Error interacting with element: {str(e)}")
            
            # Simulate random actions
            if random.random() < 0.3:  # 30% chance to perform an action
                random_action = random.choice(["like", "comment", "follow", "share"])
                print(f"Simulating {random_action} action")
                time.sleep(random.uniform(1, 3))
        
        print("Finished scrolling and interacting. Exiting...")
    
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    
    finally:
        print("Closing the browser...")
        driver.quit()

if __name__ == "__main__":
    login_with_cookies()
