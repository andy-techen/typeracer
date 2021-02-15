import os
import time
from datetime import datetime
import pandas as pd
from dotenv import load_dotenv
from selenium import webdriver

load_dotenv()
url = 'https://play.typeracer.com/'
driver_path = os.getenv("DRIVER_PATH")
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument(os.getenv("USER_AGENT"))

driver = webdriver.Chrome(driver_path)
driver.get(url)
time.sleep(5)

# Logging in
try:
    driver.find_element_by_link_text("Sign In").click()
    driver.find_element_by_name("username").send_keys(os.getenv("RACERNAME"))
    driver.find_element_by_name("password").send_keys(os.getenv("PASSWORD"))
    driver.find_element_by_xpath("//button[text()='Sign In']").click()
    print("Successfully Signed In!")
    time.sleep(1)
except Exception as e:
    print(e)

# Switching to classic mode
driver.find_element_by_xpath("//a[@title='choose a theme']").click()
time.sleep(3)
driver.find_element_by_xpath("//b[text()='Classic']").click()
time.sleep(5)

# Scraping first page
driver.find_elements_by_xpath("//div[text()='My Scores']")[0].click()
time.sleep(1)
scores = driver.find_elements_by_xpath("//*[@class='StatsTable']")[1].get_attribute("innerHTML")
scores_list = pd.read_html(scores, header=0)
races = scores_list[0].iloc[0, 0]
pages = races // 20
print(f"Fetching Page #1 (20/{races})")

# Scraping all following pages
for page in range(pages):
    driver.find_element_by_link_text("older").click()
    page_races = (page + 2) * 20
    if page_races > races:
        print(f"Fetching Page #{pages+1} ({races}/{races})") # last page
    else:
        print(f"Fetching Page #{page+2} ({page_races}/{races})")
    time.sleep(3.5) # 20 requests per minute limit
    scores = driver.find_elements_by_xpath("//*[@class='StatsTable']")[1].get_attribute("innerHTML")
    scores_list.append(pd.read_html(scores, header=0)[0])

scores_table = pd.concat(scores_list)
fetch_date = str(datetime.now().date())
scores_table.loc[scores_table['when'].str.contains("ago"), 'when'] = fetch_date
scores_table['speed'] = scores_table['speed'].str.replace('wpm', '')

# Saving to csv
scores_table.to_csv(f"{fetch_date}.csv", index=False)
print("Finished Fetching!")
