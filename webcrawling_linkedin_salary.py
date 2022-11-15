#*************************************
# Created by: Rovenna Chu (ytc17@sfu.ca)
# Purpose: this is the web scrapping for LinkedIn Salary Information (not job post specific)
#  - salary range, average salary and post date will be obtained after the scrapping
#*************************************

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup as bs
import re as re
import time
import pandas as pd

import traceback
import sys

PATH = '/usr/bin/chromedriver'
BASE_URL = 'https://www.linkedin.com/salary/'

DESTINATION_FOLDER = "preprocessing_parquet"

def search_job_salary(
    url=BASE_URL,
    keywords=None,
    location_name=None):
    
    job_base_salary = ""
    job_salary_range = ""
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get(BASE_URL)
    
    with open("salary__front_page.html", "w") as file:
        file.write(str(driver.page_source))
            
    
    try:
        wait = WebDriverWait(driver, 3)
        
        wait.until(EC.presence_of_element_located((By.XPATH, "//input[@class='typeahead-keyword']")))
        
        #enter job title
        keywords_field = driver.find_element_by_xpath("//input[@class='typeahead-keyword']")
        
        print(keywords_field)
        
        keywords_field.send_keys(keywords)
        
        #enter location
        location_field = driver.find_element_by_xpath("//input[@class='typeahead-location']")
       
        location_field.send_keys(location_name)
        
        #press search button
        search_btn = driver.find_element_by_xpath("//div[@class='search-button-container']/button")
        
        # save current page url
        current_url = driver.current_url
        
        #search
        search_page = search_btn.click()
        
        
        wait = WebDriverWait(driver, 10)
        
        wait.until(EC.url_changes(current_url))
        
        # print new URL
        new_url = driver.current_url
        print(new_url)
        
        #locate search results
        job_salary_container = driver.find_element_by_xpath("//section[@class='search-results-container']//div[@class='searchTopCard__lowerContentWrapper ']")
        
        job_base_salary = job_salary_container.find_element_by_xpath("//span[@class='searchTopCard__baseCompensation']").text
        job_salary_range = job_salary_container.find_element_by_xpath("//span[@class='searchTopCard__rangeNumber']").text
        
            
        with open("salary_page.html", "w") as file:
            file.write(str(search_page))
            
        print("Finish crawling and saving")
        
    except Exception:
        print(traceback.format_exc())
        #time.sleep(3)
    finally:
        driver.quit()
    
    #enter job title
    #keywords_field = driver.find_element_by_xpath("//*[@id='ember1466']/div/input")
    #keywords_field = driver.find_element_by_xpath("//input[@class='typeahead-keyword']")
    #keywords_field.send_keys(keywords)
    
    #enter location
    #location_field = driver.find_element_by_xpath("//*[@id='ember1470']/div/input")
    #location_field = driver.find_element_by_xpath("//input[@class='typeahead-location']")
    #location_field.send_keys(location_name)
    
    #press search button
    #search_btn = driver.find_element_by_xpath("//*[@id='ember1463']/div/div/div[2]/button")
    #search_btn = driver.find_element_by_xpath("//div[@class='search-button-container']/button")
    
    
    #locate search results
    #job_salary_container = driver.find_element_by_xpath("//section[@class='search-results-container']//div[@class='searchTopCard__lowerContentWrapper ']")

    
    return job_base_salary, job_salary_range

if __name__ == '__main__':
    job_title = "data scientist"
    location = "Canada"
    
    if len(sys.argv) == 3:
        job_title = sys.argv[1]
        location = sys.argv[2]

    job_base_salary, job_salary_range = search_job_salary(url=BASE_URL, keywords=job_title, location_name=location)
    
    
    print("Job title: {}".format(job_title))
    print("Location: {}".format(location))
    print("Base Salary: {}".format(job_base_salary))
    print("Salary Range: {}".format(job_salary_range))
    
    from datetime import date

    today = date.today()

    # YYYY/mm/dd
    current_date = today.strftime("%Y-%m-%d")
    
    df = pd.Dataframe()
    df['base_salary'] = job_base_salary
    df['salary_range'] = job_salary_range
    df['post_date'] = current_date
    
    df.to_parquet(DESTINATION_FOLDER + "/" + "LinkedIn_{}_{}_{}.csv".format(keywords, location, pd.datetime.now().strftime("%Y-%m-%d %H%M%S")))