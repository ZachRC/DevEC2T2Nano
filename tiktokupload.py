import asyncio
from playwright.async_api import async_playwright
import json
import time
import os
import random
import sys
import boto3
from botocore.exceptions import NoCredentialsError
from dotenv import load_dotenv
from io import BytesIO

def print_flush(message):
    print(message, flush=True)

def random_sleep(min_time=1, max_time=5):
    time.sleep(random.uniform(min_time, max_time))

async def load_cookies(context, file_path):
    with open(file_path, 'r') as f:
        cookies = json.load(f)
    
    for cookie in cookies:
        if 'sameSite' in cookie:
            if cookie['sameSite'] not in ['Strict', 'Lax', 'None']:
                cookie['sameSite'] = 'Lax'
        else:
            cookie['sameSite'] = 'Lax'
        
        # Remove problematic fields
        cookie.pop('hostOnly', None)
        cookie.pop('session', None)
        cookie.pop('storeId', None)
        cookie.pop('id', None)
        
        # Ensure expirationDate is in the correct format
        if 'expirationDate' in cookie:
            cookie['expires'] = int(cookie['expirationDate'])
            del cookie['expirationDate']
    
    try:
        await context.add_cookies(cookies)
    except Exception as e:
        print_flush(f"Error adding cookies: {str(e)}")
        print_flush(f"Problematic cookies: {json.dumps(cookies, indent=2)}")

async def random_action(page):
    actions = [
        lambda: page.evaluate("window.scrollTo(0, document.body.scrollHeight * Math.random())"),
        lambda: page.evaluate(f"window.scrollBy(0, {random.randint(-500, 500)})"),
        lambda: page.keyboard.press("PageDown"),
        lambda: page.keyboard.press("PageUp"),
        lambda: page.hover("div[data-e2e='recommend-list-item-container']"),
    ]
    try:
        await random.choice(actions)()
        print_flush(f"Performed random action")
    except Exception as e:
        print_flush(f"Failed to perform random action: {str(e)}")

async def interact_with_video(page):
    try:
        videos = await page.query_selector_all("div[data-e2e='recommend-list-item-container']")
        if videos:
            video = random.choice(videos)
            await video.click()
            print_flush("Clicked on a video")
            await random_sleep(3, 10)
            
            actions = [
                lambda: page.click("[data-e2e='like-icon']"),
                lambda: page.click("[data-e2e='comment-icon']"),
                lambda: page.click("[data-e2e='share-icon']"),
                lambda: page.evaluate("window.scrollTo(0, document.body.scrollHeight * Math.random())"),
            ]
            
            for _ in range(random.randint(1, 3)):
                try:
                    await random.choice(actions)()
                    print_flush("Performed action on video")
                    await random_sleep(1, 5)
                except:
                    pass
            
            await page.go_back()
            print_flush("Returned to the main page")
    except Exception as e:
        print_flush(f"Failed to interact with video: {str(e)}")

async def explore_feed(page):
    for _ in range(random.randint(5, 15)):
        try:
            await random_action(page)
            await asyncio.sleep(random.uniform(1, 5))
            if random.random() < 0.3:
                await interact_with_video(page)
            await asyncio.sleep(random.uniform(2, 8))
        except Exception as e:
            print_flush(f"Error during explore_feed: {str(e)}")
            continue

async def search_and_explore(page):
    search_terms = ["funny", "cats", "dance", "food", "travel", "music", "fashion", "sports"]
    search_term = random.choice(search_terms)
    print_flush(f"Searching for: {search_term}")
    try:
        search_input = await page.wait_for_selector("input[data-e2e='search-user-input']", timeout=5000)
        if search_input:
            await search_input.fill(search_term)
            await search_input.press("Enter")
            await asyncio.sleep(random.uniform(3, 7))
            await explore_feed(page)
        else:
            print_flush("Search input not found")
    except Exception as e:
        print_flush(f"Error during search_and_explore: {str(e)}")

async def login_with_cookies():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
        )
        page = await context.new_page()

        try:
            print_flush("Navigating to TikTok...")
            await page.goto("https://www.tiktok.com/", wait_until="networkidle")
            
            print_flush("Loading cookies...")
            cookie_files = [f for f in os.listdir('./cookies') if f.endswith('.json')]
            random_cookie_file = random.choice(cookie_files)
            print_flush(f"Selected cookie file: {random_cookie_file}")
            await load_cookies(context, f'./cookies/{random_cookie_file}')
            
            print_flush("Refreshing the page...")
            await page.reload(wait_until="networkidle")
            
            print_flush("Checking login status...")
            login_button = await page.query_selector('button[data-e2e="top-login-button"]')
            if login_button:
                print_flush("Login unsuccessful. Trying to log in manually...")
                await manual_login(page)
            else:
                print_flush("Logged in successfully")
            
            # Explore the feed
            print_flush("Starting to explore feed...")
            await explore_feed(page)
            
            # Perform a search and explore results
            print_flush("Starting search and explore...")
            await search_and_explore(page)
            
            # Navigate to the upload page and take a screenshot
            print_flush("Navigating to the upload page...")
            await page.goto("https://www.tiktok.com/tiktokstudio/upload", wait_until="networkidle")
            await take_screenshot_and_upload(page, "upload_page.png")
            print_flush("Screenshot of upload page taken and uploaded to S3")
            
        except Exception as e:
            print_flush(f"An error occurred: {str(e)}")
            
            # Take a screenshot even if an error occurred
            await take_screenshot_and_upload(page, "error_page.png")
            print_flush("Error screenshot uploaded to S3 as error_page.png")
        
        finally:
            print_flush("Closing the browser...")
            await browser.close()

async def manual_login(page):
    # Implement manual login logic here if needed
    pass

async def take_screenshot_and_upload(page, filename):
    screenshot = await page.screenshot()
    upload_to_s3(screenshot, filename)

def upload_to_s3(image_data, filename):
    s3_client = boto3.client('s3')
    try:
        s3_client.upload_fileobj(
            BytesIO(image_data),
            os.getenv('S3_BUCKET_NAME'),
            filename
        )
        print_flush(f"Successfully uploaded {filename} to S3")
    except NoCredentialsError:
        print_flush("Credentials not available for S3 upload")
    except Exception as e:
        print_flush(f"Error uploading to S3: {str(e)}")

if __name__ == "__main__":
    load_dotenv()
    asyncio.run(login_with_cookies())