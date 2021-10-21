""" Benjamin Buss
    October 18th 2021
    Zion Permit Scraper
"""


def build_list(master_list, day_list, perm_type, months, canyon):
    temp = day_list[0].split('\n')
    dom = temp[0]  # Day of month
    value = temp[1]  # Permit value
    date = months + ", " + dom
    cur_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    temp_list = [date, value, perm_type, canyon, cur_time]

    master_list.append(temp_list)


import io
import os
import boto3
import pandas as pd
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

chrome_options = Options()
chrome_options.add_argument("--headless")
driver = webdriver.Chrome(executable_path='/usr/local/bin/chromedriver', options=chrome_options)
driver.get('https://zionpermits.nps.gov/wilderness.cfm?TripTypeID=3')

#  Select list of all canyon names
canyons = driver.find_elements(By.XPATH, '//*[@id="ResourceID"]')
canyon_list = []
for c in range(len(canyons)):
    canyon_list.append(canyons[c].text)
canyon_list = canyon_list[0].splitlines()
canyon_list = canyon_list[1:]

master = []

for canyon in canyon_list:
    #  Select drop down and a canyon
    drop = Select(driver.find_element(By.ID, 'ResourceID'))
    drop.select_by_visible_text(canyon)

    #  Get months
    month = driver.find_elements(By.XPATH, '//*[@class="znpwpcaltable"]/tbody/tr/th')
    months = []
    for p in range(len(month)):
        months.append(month[p].text)
    months = [months[x] for x in (0, 8)]

    #  Last minute permits available
    full_day = driver.find_elements(By.XPATH, '//td[@class="znpwpcalendarfull"]')
    full_days = [full_day[0].text]

    build_list(master, full_days, "full", months[0], canyon)
    #  Next day available permits
    open_day = driver.find_elements(By.XPATH, '//td[@class="znpwpcalendaravailable"]')
    open_days = [open_day[0].text]

    temp = open_days[0].split('\n')
    dom = temp[0]  # Day of month
    if dom == '1':
        build_list(master, open_days, "open", months[1], canyon)
    else:  # Not first day of month
        build_list(master, open_days, "open", months[0], canyon)

driver.quit()

AWS_S3_BUCKET = os.getenv("AWS_S3_BUCKET")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
    )

canyon_df = pd.DataFrame(
    data=master,
    columns=["permit_date", "permit_count", "permit_type", "permit_canyon", "scraped_datestamp"],
    )

filename = "rawdata/"+datetime.now().strftime("%Y-%m-%d")+".csv"

with io.StringIO() as csv_buffer:
    canyon_df.to_csv(csv_buffer, index=False)

    response = s3_client.put_object(
        Bucket='zionpermit', Key=filename, Body=csv_buffer.getvalue()
    )
