""" Benjamin Buss
    October 28th 2021
    Zion Permit Scraper
    Scrapes the number of available permits for various Zion backcountry activities.
    Uploads to AWS S3 bucket
"""


def build_list(master_list, day_list,  months, canyon, typeid):
    temp = day_list[0].split('\n')
    dom = temp[0]  # Day of month
    value = temp[1]  # Permit value
    date = months + ", " + dom
    temp_time = datetime.now()-timedelta(hours=7)
    cur_time = temp_time.strftime("%Y-%m-%d %H:%M:%S")
    temp_list = [date, value, canyon, cur_time, typeid]

    master_list.append(temp_list)


def scrape_trip(typeid):
    #  Select list of all area names
    area = driver.find_elements(By.XPATH, '//*[@id="ResourceID"]')
    templist = []
    for c in range(len(area)):
        templist.append(area[c].text)
    templist = templist[0].splitlines()
    templist = templist[1:]

    for item in templist:
        #  Select drop down and a area(canyon areas, climbing areas, camping areas).
        drop = Select(driver.find_element(By.ID, 'ResourceID'))
        drop.select_by_visible_text(item)

        #  Get months
        month = driver.find_elements(By.XPATH, '//*[@class="znpwpcaltable"]/tbody/tr/th')
        months = []
        for p in range(len(month)):
            months.append(month[p].text)
        months = months[0]

        #  Last minute permits available
        full_day = driver.find_elements(By.XPATH, '//td[@class="znpwpcalendarfull"]')
        full_days = [full_day[0].text]

        build_list(master, full_days, months, item, typeid)


import io
import os
import boto3
import pandas as pd
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

chrome_options = Options()
chrome_options.add_argument("--headless")

master = []
TripType = ['1', '3', '4']

for type_id in TripType:
    driver = webdriver.Chrome(executable_path='/usr/local/share/chromedriver', options=chrome_options)
    base_url = 'https://zionpermits.nps.gov/wilderness.cfm?TripTypeID='
    url = base_url + type_id

    driver.get(url)
    scrape_trip(type_id)
    driver.quit()


# ----- EXPORT DATA --------------------------
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
    )

canyon_df = pd.DataFrame(
    data=master,
    columns=["permit_date", "permit_count", "permit_area", "scraped_datestamp", "area_id"],
    )

temp_time = datetime.now()-timedelta(hours=7)
filename = "data/"+temp_time.strftime("%Y-%m-%d")+".csv"

with io.StringIO() as csv_buffer:
    canyon_df.to_csv(csv_buffer, index=False)

    response = s3_client.put_object(
        Bucket='zionpermit', Key=filename, Body=csv_buffer.getvalue()
    )
