""" Benjamin Buss
    October 18th 2021
    Zion Permit Scraper
"""


def build_list(master_list, day_list, perm_type, months, canyon, typeid):
    temp = day_list[0].split('\n')
    dom = temp[0]  # Day of month
    value = temp[1]  # Permit value
    date = months + ", " + dom
    cur_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    temp_list = [date, value, perm_type, canyon, cur_time, typeid]

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
        months = [months[x] for x in (0, 8)]

        #  Last minute permits available
        full_day = driver.find_elements(By.XPATH, '//td[@class="znpwpcalendarfull"]')
        full_days = [full_day[0].text]

        build_list(master, full_days, "full", months[0], item, typeid)
        #  Next day available permits
        open_day = driver.find_elements(By.XPATH, '//td[@class="znpwpcalendaravailable"]')
        open_days = [open_day[0].text]

        temp = open_days[0].split('\n')
        dom = temp[0]  # Day of month
        if dom == '1':
            build_list(master, open_days, "open", months[1], item, typeid)
        else:  # Not first day of month
            build_list(master, open_days, "open", months[0], item, typeid)


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

master = []
TripType = ['1', '3', '4']

for type_id in TripType:
    driver = webdriver.Chrome(executable_path='/usr/bin/chromedriver', options=chrome_options)
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
    columns=["permit_date", "permit_count", "permit_type", "permit_area", "scraped_datestamp", "area_id"],
    )

filename = "raw_data/"+datetime.now().strftime("%Y-%m-%d")+".csv"

with io.StringIO() as csv_buffer:
    canyon_df.to_csv(csv_buffer, index=False)

    response = s3_client.put_object(
        Bucket='zionpermit', Key=filename, Body=csv_buffer.getvalue()
    )
