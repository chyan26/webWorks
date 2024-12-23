import undetected_chromedriver as uc
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

# Setting up options for undetected chromedriver
options = Options()
options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.140 Safari/537.3')
options.add_argument('--disable-extensions')  # Disable extensions to make it more like a normal user session

options.add_argument('--no-sandbox')  # Helps bypass certain security features
options.add_argument('--disable-dev-shm-usage')  # Prevents issues on Linux-based systems

# Use undetected_chromedriver to bypass bot protection
driver = uc.Chrome(options=options)

# Example URL (replace with your URL)
url = 'https://www.bravelog.tw/athlete/1189/003001'

try:
    # Open the URL
    driver.get(url)

    # Wait for the page to load fully (you can adjust the wait time as needed)
    time.sleep(10)  # Give it time to bypass the challenge (may need to increase)

    # After bypassing the Cloudflare page, extract content from the page
    page_content = driver.page_source
    print(page_content)  # Example: print the page source

    # If successful, proceed with scraping further content or interactions
    # driver.find_element(By.CLASS_NAME, 'your_class_name').click()  # Example of interacting with page

finally:
    # Make sure to close the browser session
    driver.quit()



