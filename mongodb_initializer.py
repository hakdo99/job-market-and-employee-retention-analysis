#*************************************
# Created by: Kukpyo (Andrew) Han  - kha107@sfu.ca
# Created on: March 10, 2022
# Last Updated on: April 8, 2022
# Objective: This python code is intended clear all the documents from available MongoDB collections.
#*************************************

from mongodb_connector import connect_to_collection

confirmation = input("Are you sure you want to initialize all the MongoDB collections? (Y/n) ")

if str(confirmation).lower() == "y":

    avg_sal_collect = connect_to_collection("AverageSalary")
    avg_sal_collect.delete_many({})

    employees_collect = connect_to_collection("Employees")
    employees_collect.delete_many({})

    job_post_collect = connect_to_collection("JobPosts")
    job_post_collect.delete_many({})

    job_skills_collect = connect_to_collection("JobSkills")
    job_skills_collect.delete_many({})

elif str(confirmation).lower() == "n":
    print("Program terminated without initializing MongoDB")
else:
    print("Invalid Input. Program terminated")