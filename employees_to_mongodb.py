# *************************************
# Created by: Kukpyo (Andrew) Han  - kha107@sfu.ca
# Created on: March 25, 2022
# Last Updated on: April 1, 2022
# Objective: This python code is intended to load employees information from IBM dataset
#            and directly push them to MongoDB "Employees" collection.
# *************************************

from mongodb_connector import connect_to_collection
import pandas as pd


def dict_constructor(age, attrition, business_travel, daily_rate, department, distance_from_home, education,
                     education_field, employee_count, employee_number, environment_satisfaction, gender,
                     hourly_rate, job_involvement, job_level, job_role, job_satisfaction, marital_status,
                     monthly_income, monthly_rate, num_companies_worked, over_eighteen, over_time,
                     percent_salary_hike, performance_rating, relationship_satisfaction, standard_hours,
                     stock_option_level, total_working_years, training_times_last_year, work_life_balance,
                     yrs_at_company, yrs_in_role, yrs_since_prom, yrs_with_cur_mgr):
    output_dict = {
        'Age': age,
        'Attrition': attrition,
        'BusinessTravel': business_travel,
        'DailyRate': daily_rate,
        'Department': department,
        'DistanceFromHome': distance_from_home,
        'Education': education,
        'EducationField': education_field,
        'EmployeeCount': employee_count,
        'EmployeeNumber': employee_number,
        'EnvironmentSatisfaction': environment_satisfaction,
        'Gender': gender,
        'HourlyRate': hourly_rate,
        'JobInvolvement': job_involvement,
        'JobLevel': job_level,
        'JobRole': job_role,
        'JobSatisfaction': job_satisfaction,
        'MaritalStatus': marital_status,
        'MonthlyIncome': monthly_income,
        'MonthlyRate': monthly_rate,
        'NumCompaniesWorked': num_companies_worked,
        'Over18': over_eighteen,
        'OverTime': over_time,
        'PercentSalaryHike': percent_salary_hike,
        'PerformanceRating': performance_rating,
        'RelationshipSatisfaction': relationship_satisfaction,
        'StandardHours': standard_hours,
        'StockOptionLevel': stock_option_level,
        'TotalWorkingYears': total_working_years,
        'TrainingTimesLastYear': training_times_last_year,
        'WorkLifeBalance': work_life_balance,
        'YearsAtCompany': yrs_at_company,
        'YearsInCurrentRole': yrs_in_role,
        'YearsSinceLastPromotion': yrs_since_prom,
        'YearsWithCurrManager': yrs_with_cur_mgr
    }

    return output_dict


if __name__ == "__main__":

    employees_df = pd.read_csv("sample_file/WA_Fn-UseC_-HR-Employee-Attrition.csv")

    print('============================== Construct a dictionary for batch insert ===================================')
    # docs_to_insert will hold all the records to be inserted into "JobPosts" collection
    docs_to_insert = []

    for idx_row, row in employees_df.iterrows():
        employees_dict = dict_constructor(row['Age'], row['Attrition'], row['BusinessTravel'], row['DailyRate'],
                                          row['Department'], row['DistanceFromHome'], row['Education'],
                                          row['EducationField'], row['EmployeeCount'], row['EmployeeNumber'],
                                          row['EnvironmentSatisfaction'], row['Gender'], row['HourlyRate'],
                                          row['JobInvolvement'], row['JobLevel'], row['JobRole'],
                                          row['JobSatisfaction'],
                                          row['MaritalStatus'], row['MonthlyIncome'], row['MonthlyRate'],
                                          row['NumCompaniesWorked'], row['Over18'], row['OverTime'],
                                          row['PercentSalaryHike'], row['PerformanceRating'],
                                          row['RelationshipSatisfaction'], row['StandardHours'],
                                          row['StockOptionLevel'],
                                          row['TotalWorkingYears'], row['TrainingTimesLastYear'],
                                          row['WorkLifeBalance'],
                                          row['YearsAtCompany'], row['YearsInCurrentRole'],
                                          row['YearsSinceLastPromotion'], row['YearsWithCurrManager']
                                          )
        docs_to_insert.append(employees_dict)
    print('============================== Construct a dictionary for batch insert (completed) ==================='
          '================')

    print('============================== Connecting to MongoDB ===================================')
    # Connect to MongoDB and obtain "Employees" collection
    employees_collect = connect_to_collection("Employees")
    print('============================== Connecting to MongoDB (completed) ===================================')

    print('============================== Inserting into MongoDB ===================================')
    result = employees_collect.insert_many(docs_to_insert)
    print("Number of documents added: ", len(result.inserted_ids))
    print("New documents added: ", result.inserted_ids)
    print('============================== Inserting into MongoDB (completed) ===================================')
