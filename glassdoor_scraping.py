#!/usr/bin/env python
# coding: utf-8

# In[3]:


from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, ElementNotInteractableException, StaleElementReferenceException
from selenium import webdriver
import time
import sys
import pandas as pd
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from datetime import datetime, timedelta
import os
import re

# now = datetime.now()
# timestamp = now.strftime("%d/%m/%Y %H:%M:%S")


# In[4]:


# FOLDER = os.path.join(os.getcwd(), "preprocessing_parquet")
# # print(FOLDER)
# if not os.path.exists(FOLDER):
#     os.mkdir(FOLDER)


# In[5]:


import urllib
import requests
sample_endpoint = "https://www.glassdoor.com/findPopularLocationAjax.htm?" +                     f"term={urllib.parse.quote('Vancouver, BC')}&maxLocationsToReturn=10"
headers = {
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; rv:91.0) Gecko/20100101 Firefox/91.0'
}
response = requests.get(sample_endpoint, headers=headers)
response.json()


# In[6]:


def location_glassdoor_id(location: str):
    url_encoded_loc = urllib.parse.quote(location)
    endpoint = f"https://www.glassdoor.com/findPopularLocationAjax.htm?term={url_encoded_loc}&maxLocationsToReturn=10"
    headers = {
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; rv:91.0) Gecko/20100101 Firefox/91.0'
    }
    response = requests.get(endpoint, headers=headers)
    # Best guess location
    location = response.json()[0]
    location_name = location['longName']
    location_ID = location['locationId']
    location_type = location['locationType']
    
    return location_name, location_ID, location_type


# In[8]:


def get_post_date(input_str):
    today = datetime.today()
    if (input_str == "30d+"):
        days_to_stt = timedelta(days=40)
    if (input_str[-1] == "h"):
        days_to_stt = timedelta(days=0)
    else:
        res = re.findall('(\d+|[A-Za-z]+)', input_str)
        days_to_stt = timedelta(days=int(res[0]))
    post_date = today - days_to_stt
    return post_date.strftime("%Y-%m-%d")


# In[9]:


def get_jobs(keyword, location, verbose=False):
    
    '''Gathers jobs as a dataframe, scraped from Glassdoor'''
    
    #Initializing the webdriver
    options = webdriver.ChromeOptions()
    
    #Uncomment the line below if you'd like to scrape without a new Chrome window every time.
    #options.add_argument('headless')
    
    #Change the path to where chromedriver is in your home folder.
    driverpath = GeckoDriverManager().install()
    driver = webdriver.Firefox(executable_path=driverpath)
    driver.set_window_size(1120, 1000)
    
    name, loc_id, loc_type = location_glassdoor_id(location)
    url = 'https://www.glassdoor.ca/Job/index.htm'
    driver.get(url)
    time.sleep(5.5)
    driver.find_element(by = By.XPATH, value = '//input[@data-test="search-bar-keyword-input"]').send_keys(keyword)
    driver.find_element(by = By.XPATH, value = '//input[@data-test="search-bar-location-input"]').clear()
    driver.find_element(by = By.XPATH, value = '//input[@data-test="search-bar-location-input"]').send_keys(location)
    driver.find_element(by = By.XPATH, value = '//input[@data-test="search-bar-location-input"]').send_keys(Keys.RETURN)
    try:
        driver.find_element(by = By.XPATH, value = '//button[@data-test="search-bar-submit"]').click() 
        time.sleep(2.5)
    except ElementClickInterceptedException:
        print("Cannot find search bar")
        pass
    #url = f'https://www.glassdoor.com/Job/jobs.htm?sc.keyword="{keyword}"' +             f'&locT={loc_type}&locId={loc_id}' +             '&jobType=all&fromAge=-1&minSalary=0&includeNoSalaryJobs=true' +             '&radius=100&cityId=-1&minRating=0.0&industryId=-1&sgocId=-1&seniorityType=all' +             '&companyId=-1&employerSizes=0&applicationType=0&remoteWorkType=0'
    #url = f'https://www.glassdoor.com/Job/jobs.htm?sc.keyword="{keyword}"' +             f'&locT={loc_type}&locId={loc_id}' +             '&jobType=all&fromAge=-1&minSalary=0&lo_IP{page}.htm?includeNoSalaryJobs=true' +             '&radius=100&cityId=-1&minRating=0.0&industryId=-1&sgocId=-1&seniorityType=all' +             '&companyId=-1&employerSizes=0&applicationType=0&remoteWorkType=0'

    #url = 'https://www.glassdoor.com/Job/jobs.htm?sc.keyword="' + keyword + '"&locT=C&locId=1147401&locKeyword=San%20Francisco,%20CA&jobType=all&fromAge=-1&minSalary=0&includeNoSalaryJobs=true&radius=100&cityId=-1&minRating=0.0&industryId=-1&sgocId=-1&seniorityType=all&companyId=-1&employerSizes=0&applicationType=0&remoteWorkType=0'
    # url = 'https://www.glassdoor.com/Job/jobs.htm?sc.keyword="' + keyword + '"&locT=C&locId=1147401&locKeyword="' + location + '"&jobType=all&fromAge=-1&minSalary=0&includeNoSalaryJobs=true&radius=100&cityId=-1&minRating=0.0&industryId=-1&sgocId=-1&seniorityType=all&companyId=-1&employerSizes=0&applicationType=0&remoteWorkType=0'
    #driver.get(url)
    jobs = []
    source = "Glassdoor"
    job_type = ""
    job_exp = ""
    signup_found = False
    meta_url = None

    #while len(jobs) < num_jobs:  #If true, should be still looking for new jobs.

        # Change this number based on internet speed.
    time.sleep(5)

    try:
        driver.find_element(by = By.CLASS_NAME, value = "ModalStyle__xBtn___29PT9").click()  #clicking to the X.
    except NoSuchElementException:
        print("Cannot find modalstyle")
        pass
    
    index_footer = driver.find_element(by = By.XPATH, value = './/div[@class="paginationFooter"]').text.split(" ")
    num_pages = int(index_footer[-1])
    index = int(index_footer[1])
    print("Number of pages: " + str(num_pages))
    

    #Going through each job in this page, index STARTS AT 1!
    while (index <= num_pages):
        print("Current index: " + str(index))
        try:
            meta_url_element = driver.find_element(by = By.XPATH, value = '//meta[@property="og:url"]')
            meta_url = meta_url_element.get_attribute('content')
            
            job_buttons = driver.find_elements(by = By.XPATH, value = '//a[@class="jobLink"]')

            for job_button in job_buttons:
                print("Progress: " + str(len(jobs)))

                try:
                    driver.find_element(by = By.CLASS_NAME, value = "modal_closeIcon").click()  #clicking to the X.
                    print("found a pop-up, clicking X...")
                    time.sleep(2)
                except NoSuchElementException:
                    pass
                try:
                    job_button.click()  #You might 
                    time.sleep(1)
                except StaleElementReferenceException:
                    driver.refresh()
                    driver.implicitly_wait(2)
                    #job_button.click()
                    ActionChains(driver).double_click(job_button).perform()
                    #driver.implicitly_wait(10)
                    #ActionChains(driver).move_to_element(job_button).click(job_button).perform()

                collected_successfully = False

                while not collected_successfully:
                    try:
                        company_name = driver.find_element(by = By.XPATH, value = './/div[@class="css-xuk5ye e1tk4kwz5"]').text.splitlines()[0]
                        location = driver.find_element(by = By.XPATH, value = './/div[@class="css-56kyx5 e1tk4kwz1"]').text
                        job_title = driver.find_element(by = By.XPATH, value = './/div[@class="css-1j389vi e1tk4kwz2"]').text
                        job_description = driver.find_element(by = By.XPATH, value = './/div[@class="jobDescriptionContent desc"]').text                        
                        post_date = driver.find_element(by = By.XPATH, value = './/div[@class="d-flex align-items-end pl-std css-17n8uzw"]').text
                        post_date = get_post_date(post_date)
                        collected_successfully = True
                    except:
                        print("Cannot collect successfully")
                        time.sleep(0.5)


                try:
                    estimated_salary = driver.find_element(by = By.XPATH, value = './/div[@class="css-y2jiyn e2u4hf18"]').text
                except NoSuchElementException:
                    estimated_salary = None #You need to set a "not found value. It's important."

                #Printing for debugging
                if verbose:
                    print("Job Title: {}".format(job_title))
                    print("Salary Estimate: {}".format(estimated_salary))
                    #print("Job Description: {}".format(job_description[:500]))
                    print("Job Description: {}".format(job_description))
                    #print("Rating: {}".format(rating))
                    print("Company Name: {}".format(company_name))
                    print("Location: {}".format(location))

                #Going to the Company tab...

                try:
                    industry = driver.find_element(by = By.XPATH, value = './/span[@class="css-1pldt9b e1pvx6aw1" and text()="Industry"]//following-sibling::*').text                
                except NoSuchElementException:
                    industry = None


                if verbose:
                    # print("Headquarters: {}".format(headquarters))
                    # print("Size: {}".format(size))
                    # print("Founded: {}".format(founded))
                    # print("Type of Ownership: {}".format(type_of_ownership))
                    print("Industry: {}".format(industry))
                    # print("Sector: {}".format(sector))
                    # print("Revenue: {}".format(revenue))
                    # print("Competitors: {}".format(competitors))
                    print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")

                jobs.append({"job_title" : job_title,
                             "job_type" : job_type,
                             "job_type" : job_exp,
                             "company" : company_name,
                "industries" : industry,
                "location" : location,
                "description" : job_description,
                "source" : source,
                "search_kw" : keyword,
                "expected_salary" : estimated_salary,
                "post_date": post_date,           

                })

        except ElementNotInteractableException:
            if (index >= num_pages):
                print("Scraping done")
                break
            index = index + 1
            fix_url = "_IP{}.htm".format(index)
            new_url = meta_url.replace(".htm",fix_url)
            #print(new_url)
            driver.get(new_url)
            #print("switching")
            time.sleep(3.5)
        time.sleep(3.5)
            
#     timestamp = str(datetime.now().strftime("%Y%m%d_%H%M%S"))
#     filename = f"Glassdoor_{keyword}_{location}_{timestamp}.parquet"
#     filepath = os.path.join(FOLDER, filename)

#     return pd.DataFrame(jobs).to_parquet(filepath, compression='gzip')  #This line converts the dictionary object into a parquet file.
    return pd.DataFrame(jobs)

if __name__ == "__main__":

    # python webscrape_jobpost_indeed.py "data analyst" "Vancouver BC"
    position = sys.argv[1]
    location = sys.argv[2]
    
    df = get_jobs(position, location)

    timestamp = str(datetime.today().strftime("%Y%m%d%H"))
    FOLDER = os.path.join(os.getcwd(), "preprocessing_parquet")
    if not os.path.exists(FOLDER):
        os.mkdir(FOLDER)
    #FOLDER = "preprocessing_parquet/"
    filename = f"Glassdoor_{position}_{location}_{timestamp}.parquet"
    filepath = os.path.join(FOLDER, filename)

    df.to_parquet(filepath)

