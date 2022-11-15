#*************************************
# Created by: Kukpyo (Andrew) Han  - kha107@sfu.ca
# Created on: February 20, 2022
# Last Updated on: March 23, 2022
# Objective: This python code is intended to scrape job posts from ca.indeed.com (based on search keyword and location)
#            and output a parquet file.
# Input source: https://ca.indeed.com
# Output files : located under "/preprocessing_parquet"
#*************************************

## pip install pyarrow fastparquet

from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import random
import csv
import requests
import pandas as pd
import time
import sys


# define punctuation
punctuations = '''!()-[]{};:'"\,<>./?@#$%^&*_~'''
# Special characters to be removed when extracting annual salaries
chars_to_remove = '''$,'''

words_to_remove_loc = ["Temporarily", "Remote", "in"]


"""  Indeed URL examples
https://ca.indeed.com/jobs?q=data%20analyst&l=Canada
https://ca.indeed.com/jobs?q=data%20analyst&l=Vancouver%2C%20BC
"""

def get_url_indeed(position, location):
    """Generate a url based on the input postition and location"""
    template = "https://ca.indeed.com/jobs?q={}&l={}"
    url = template.format(position, location)
    return url



def get_post_date(input_str):
    today = datetime.today()

    if input_str in ("Today", "Just posted"):
        post_date = today

    else:
        tokens = input_str.split(" ")
        num_day_idx = -1

        for i in range(len(tokens)):
            if tokens[i] == "days":
                num_day_idx = i - 1

        if tokens[num_day_idx].isnumeric():
            days_to_stt = timedelta(days=int(tokens[num_day_idx]))
        else:
            days_to_stt = timedelta(days=50)

        post_date = today - days_to_stt

    return post_date.strftime("%Y-%m-%d")


def get_jobspecifics(url):

    print(url)
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    job_sticky_section = soup.find('div', 'jobsearch-DesktopStickyContainer')

    if job_sticky_section:

        ## Get Job title from sticky section.
        job_infohead_sub = job_sticky_section.find("div",
                                                   {"class": "jobsearch-JobInfoHeader-title-container"})
        job_title_sticky = job_infohead_sub.find("h1").text.strip()

        ## Get Job location and arrangement from sticky section.
        job_compinfo_sub = job_sticky_section.find("div",
                                                   {"class": "icl-u-xs-mt--xs icl-u-textColor--secondary jobsearch-JobInfo"
                                                             "Header-subtitle jobsearch-DesktopStickyContainer-subtitle"})
        compinfo_div_sections = job_compinfo_sub.findChildren("div", recursive=False)

        index_counter = 0
        company_name = job_location = job_arrangement = ''
        for section in compinfo_div_sections:
            if index_counter == 0:
                company_name = section.text.strip()
            elif index_counter == 1:
                job_location = section.text.strip()
            else:
                job_arrangement = section.text.strip()
            index_counter += 1


        ## Get job type from sticky section.
        job_salary_jobtype_info = job_sticky_section.find("div", {"id": "salaryInfoAndJobType"})
        try:
            jobtype_div_sections = job_salary_jobtype_info.findChildren("span")
            div_count = len(jobtype_div_sections)
            # grab job type info from the last div section
            job_type = jobtype_div_sections[div_count-1].text.strip()
        except AttributeError:
            print(f"Attribute Error occured while extracting the job type: "
                  f"{url}")
            job_type = ""

        # remove the leading dash if present
        if job_type.startswith("-"):
            job_type = job_type[1:].strip()

        # In rare cases, job type is not present while a salary is available.
        # If the extracted string is found to be a salary, leave the job type empty.
        if job_type.startswith("$"):
            job_type = ""

    # If response.text is not in a plain HTML format:
    else:
        print(f"Tag ('div', 'jobsearch-DesktopStickyContainer') does not exist : "
              f"{url}")
        job_title_sticky = ""
        company_name = ""
        job_location = ""
        job_arrangement = ""
        job_type = ""

    ## Lastly, get the job desc info
    job_desc_section = soup.find('div', 'jobsearch-jobDescriptionText')

    if job_desc_section:
        try:
            # In order to avoid duplicate fetching of the same text, we will only extract texts from <p> and <li> tags.
            children = job_desc_section.findChildren(['p', 'li'])

            text_list = []
            separator = " "
            for child in children:
                text_list.append(child.text.strip())
            job_description = separator.join(text_list)
        except AttributeError:
            try:
                job_description = job_desc_section.text
            except AttributeError:
                job_description = ""
                print(url)

    # If response.text is not in a plain HTML format:
    else:
        print(f"Tag ('div', 'jobsearch-jobDescriptionText') does not exist : "
              f"{url}")
        job_description = ""

    return company_name, job_location, job_arrangement, job_type, job_description


def get_record(container):
    """Extract job data from a single record"""

    # 1. Extract the job title
    span_count = len(container.h2.find_all("span"))
    job_title = ""
    for i in range(span_count):
        if container.h2.find_all("span")[i].get('title'):
            job_title = container.h2.find_all("span")[i].get('title').strip()
            break

    # 2. Extract the company_name/job_location/job_summary
    company_name = container.find("span", {"class": "companyName"}).text.strip()
    job_location = container.find("div", {"class": "companyLocation"}).text.strip()
    job_summary = container.find("div", {"class": "job-snippet"}).text.strip().replace("\n", " ")

    # 2-1. If the job location is multiple, extract the first location only.
    if "+" in job_location:
        location_temp = job_location.split("+")
        job_location = location_temp[0]
    # 2-2. Handle special cases where "Remote" is present in location field.
    if job_location == "Remote":
        job_location = "Canada"
    else:
        for word in words_to_remove_loc:
            job_location = job_location.replace(word, "")
        job_location = job_location.strip()

    ## To be enable for debugging
    print(f"{job_title} /// {company_name}")

    # 3. Extract the post date
    try:
        date_span_tag = container.find("span", {"class": "date"})
        date_span_tag.find("span", {"class": "visually-hidden"}).clear()
        posted = date_span_tag.text.strip()
    except AttributeError:
        print(f"Attribute Error occured while extracting the post data: "
              f"{job_title} /// {company_name}")
        posted = "Today"

    post_date = get_post_date(posted)
    today = datetime.today().strftime("%Y-%m-%d")

    # 4. Extract the salary info
    try:
        salary = container.find("div", {"class": "salary-snippet"}).text.strip()
    except AttributeError:
        salary = ""

    # Put a pause to avoid bombarding the web server
    time.sleep(round(random.uniform(3.5, 10), 2))
    desc_url = "https://ca.indeed.com" + container.get('href')
    company_name_stk, job_location_stk, job_arrangement, job_type, job_desc = get_jobspecifics(desc_url)

    record = (job_title, job_type, company_name, job_location, salary, post_date, job_arrangement,\
              job_summary, job_desc)

    return record


def add_addiontal_fields(df, position):

    # JobID/JobExperience are not available on Indeed. Therefore, leaving it empty.
    df['id'] = ''
    df['job_exp'] = ''
    df['industries'] = ''
    df['job_function'] = ''

    df['source'] = 'Indeed'
    df['search_kw'] = position

    return df



def get_result(url, position):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    #slider_containers = soup.find_all('div', 'slider_container')
    job_cards = soup.find('div', 'mosaic-provider-jobcards')
    atag_containers = job_cards.findChildren("a", recursive=False)

    # Extract all the job posts from the first page
    records = []
    for container in atag_containers:
        record = get_record(container)
        records.append(record)

    # Loop over all the result pages
    while True:
        try:
            url = "https://ca.indeed.com" + soup.find("a", {"aria-label": "Next"}).get('href')
        except AttributeError:
            break

        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        #slider_containers = soup.find_all('div', 'slider_container')
        job_cards = soup.find('div', 'mosaic-provider-jobcards')
        atag_containers = job_cards.findChildren("a", recursive=False)

        for container in atag_containers:
            record = get_record(container)
            records.append(record)

        # Put a pause to avoid bombarding the web server
        time.sleep(random.randint(7, 10))

        print("Data Fetch Completed : " + url)

    df = pd.DataFrame(records, columns= \
        ['job_title', 'job_type', 'company', 'location', 'expected_salary', 'post_date',\
         'remote', 'job_summary', 'description'])

    output_df = add_addiontal_fields(df, position)

    # Rearrange fields for consistency with data obtained from other data sources
    output_df = output_df[['id', 'job_title', 'job_type', 'job_exp', 'company', 'industries', 'location',\
                           'source', 'search_kw', 'expected_salary', 'post_date', 'job_function', 'remote',\
                           'job_summary', 'description']]

    return output_df


if __name__ == "__main__":

    # python3 webscrape_jobpost_indeed.py "data analyst" "Vancouver BC"
    position = sys.argv[1]
    location = sys.argv[2]

    url = get_url_indeed(position, location)
    df = get_result(url, position)

    timestamp = datetime.today().strftime("%Y%m%d%H")
    FOLDER = "preprocessing_parquet/"

    #df.to_csv(position + "_" + location + "_" + timestamp + ".csv", index=False)
    df.to_parquet(FOLDER + "Indeed_" + position + "_" + location + "_" + timestamp + ".parquet")
    #df.to_parquet(FOLDER + position + "_" + location + "_" + timestamp + "parquet.gzip", compression='gzip')

