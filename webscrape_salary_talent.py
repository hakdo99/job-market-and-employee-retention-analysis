#*************************************
# Created by: Kukpyo (Andrew) Han  - kha107@sfu.ca
# Created on: March 5, 2022
# Last Updated on: April 1, 2022
# Objective: This python code is intended to scrape average salary information from Talent.com
#            and directly push them to MongoDB "AverageSalary" collection.
# Input source: https://ca.talent.com
# Output destination :  MongoDB "AverageSalary" collection
#*************************************

from mongodb_connector import connect_to_collection
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import random
import requests
import time
import sys

chars_to_remove = '''$,'''

"""  Talent URL examples
https://ca.talent.com/salary?job=Data+Engineer
https://ca.talent.com/salary?job=Sales+Manager
"""

def get_url_talent(position):
    """Generate a url based on the input postition"""

    tokens = position.split(" ")
    tokens_size = len(tokens)

    # talent.com requires search keywords to be capitalized
    for i in range(tokens_size):
        tokens[i] = tokens[i].capitalize()

    search_string = "+".join(tokens)

    template = "https://ca.talent.com/salary?job={}"
    url = template.format(search_string)

    return url


def get_avg_salary(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    avg_annual_sal_str = soup.find('div', {"class": "c-card__stats-mainNumber timeBased"}).get("peryear")

    # remove dollar sign and separators from the salary string
    salary_str = ""
    for char in avg_annual_sal_str:
        if char not in chars_to_remove:
            salary_str = salary_str + char

    avg_annual_sal = int(salary_str)

    return avg_annual_sal


def add_salary(collection, occ, salary):
    document = {
        'occupation': occ,
        'salary': salary,
        'date_added': datetime.now()
    }

    return collection.insert_one(document)


def post_date_check(collection, occ):

    update_flag = False
    selected = collection.find({'occupation': occ})

    # CAVEAT: MongoDB cursor object will become empty once it is accessed by list()
    selected_list = list(selected)
    selected_cnt = len(selected_list)

    if selected_cnt > 1:
        sys.exit(f"More than one document is found for {occ} in AverageSalary collection. Please check.")
    elif selected_cnt == 1:
        last_update = selected_list[0]["date_added"]
        if last_update < datetime.now() - timedelta(days=30):
            # If the last update was done more than 30 days ago, replace the old document wit the latest salary info.
            del_result = collection.delete_many({'occupation': occ})
            print(f"Number of rows deleted for {occ}: ", del_result.deleted_count)
            update_flag = True
    # If the occupation does not exist, add to the collection.
    else:
        update_flag = True

    return update_flag


if __name__ == "__main__":

    # Connect to MongoDB and Obtain "average_salaries" collection
    avg_sal_doc = connect_to_collection("AverageSalary")

    # List down all the occupations for which salaries are gathered.
    occupation_list = ["Data Scientist", "Data Analyst", "Software Developer", "Senior Software Engineer",
                       "Front End Developer", "Senior Backend Engineer", "systems analyst", "IT Manager",
                       "Information Technology Director", "Database Administrator",
                       "Human Resources Manager", "Human Resources Supervisor", "Recruitment Consultant",
                       "Human Resources Coordinator",
                       "Recruiter", "Human Resources Director",
                       "Sales Manager", "Sales Representative", "Sales Executive",
                       "Research Scientist", "Senior Research Scientist", "Research Director",
                       "Manufacturing Technician", "Manufacturing Associate", "Manufacturing Manager",
                       "Manufacturing Director",
                       "Accountant", "Senior Accountant", "Accounting Manager",
                       "Laboratory Technician", "Patient Representative", "Research Manager",
                       "Healthcare Representative"
                       ]

    print("Number of job titles for which salaries will be obtained: ", len(occupation_list))

    for occupation in occupation_list:
        # Construct an URL for the required search
        url = get_url_talent(occupation)

        # Get an average salary for the selected job title
        avg_salary = get_avg_salary(url)

        replace_flag = post_date_check(avg_sal_doc, occupation.lower())

        if replace_flag:
            # When saving into MongoDB, turn the occupation string to lowercase.
            result = add_salary(avg_sal_doc, occupation.lower(), avg_salary)
            print("New document added: ", result.inserted_id)

        time.sleep(random.randint(7, 10))

    print("successfully updated MongoDB!!!!")
