# Job Market and Employee Engagement Dashboard

## Overview

This project is intended to help all the HR departments around Canada with their alaysis on their people, and giving predictions on how likely they are to leave the company based on their personal and professional particulars and the landscape of current job market.

- **Data Science Pipeline:**
1. Data Collection: There are 3 different datasets collected for our project.
	- JobPosts: Latest job posts scraped from the four major job search platforms (Indeed, LinkedIn, Workopolis, Glassdoor)
	- AverageSalary: Average Salary information for respective job titles in Canada is scraped from Talent.
	- Employees: IBM HR Analytics Employee Attrition & Performance dataset Obtained from Kaggle.

	:loudspeaker: **Note:** Emplyees Dataset can be replaced by the company's own employee dataset that is looking to adapt this solution.

2. Data Pre-processing and Integration: While there are no data preprocessing requried for AverageSalary and Employees, we need to pre-process job posts collected in different forms and integrate all the job posts.
	- pre-processing of different datasets: Remove duplicate job posts within respective datasets. Assigning unique jobpost_id to those records whose ids are not available.
	- Jaccard Similarity: Apply Jaccard Similarity to detect and remove similar (possibly the same) job posts collected from different platforms.


3. Data Cleaning and Standardization: In order to facilitate easier data handilng and EDA (which will be conducted later in the pipeline), perform data cleaning and standardize values.
	- standardizaiton of values: e.g. Expected salary, location, remote


4. Data Storage: We are using MongoDB to store all the data we have collected for our anlaysis.
    - We have four collections on our MongoDB database:
		- AverageSalary: occupation, salary, date_added
		- Employees: Age, Attrition, BusinessTravel, DailyRate, Department, DistanceFromHome, Education, EducationField, EmployeeCount, EmployeeNumber, EnvironmentSatisfaction, Gender, HourlyRate, JobInvolvement, JobLevel, JobRole, JobSatisfaction, MaritalStatus, MonthlyIncome, MonthlyRate, NumCompaniesWorked, Over18, OverTime, PercentSalaryHike, PerformanceRating, RelationshipSatisfaction, StandardHours, StockOptionLevel, TotalWorkingYears, TrainingTimesLastYear, WorkLifeBalance, YearsAtCompany, YearsInCurrentRole, YearsSinceLastPromotion, YearsWithCurrManager
		- JobPosts: id, job_title, job_type, job_exp, company, industries, location, source, search_kw, expected_salary, post_date, job_function, remote, job_summary, description
		- Jobskills: text, job_title, prediction_prob, predicted_skill (1 for very likely, 0 for unlikely)


5. Data Analysis: We are performing a wide range of data analysis to derive meaninful insights from the available data.
	- Skillsets Extraction: Using NLP, we are extracting sought-after skillsets for different job titles.
	- Training of machine learning model: Using the avialble datasets, implement a machine learning model that will predict probabilities of a particular employee leaving the company.
	- EDA: Identify interesting patterns and trend in the current job market.


6. Data Visualization: Using the simple web front-end interface, we will be displaying all the intersting facts and predicitons.
	- Machine learning prediction: How likely is a particular employee to leave the company based on important factors (e.g. current salary, job satisfaction)
	- Visualization of EDA



## 1. Data Collection

### start-webscraping.sh
	- Objective: This shell script is intended to be used to trigger the following web-scraping python programs at one go for each job title. Job Posts for a job title will be collected successively after another.
		- webscrape_jobpost_indeed.py (Job Post web-scraping for Indeed)
		- workopolis_jobs.py (Job Post web-scraping for Workopolis)
		- glassdoor_scrape.py (Job Post web-scraping for Glassdoor)
		- webcrawling_linkedin.py (Job Post web-scraping for LinedIn)

:loudspeaker: **Caveat:** There are limits to the number of HTTP requests that can be made to some of the platforms daily. Although this includes a full list of job titles that were scraped for our data collection, it should NOT be used in practice.

### start-webscraping-one.sh
	- Objective: This shell script shall be used to trigger the four web-scraping scripts for one job title. It is recommended that web-scraping for each job title is performed with a reasonable interval (e.g. one run per day).
usage:
`./start-webscraping-one.sh`

### webscrape_jobpost_indeed.py & workopolis_jobs.py
    - Objective: This Python script is intended to scrape all the job posts and their relevant information (including job descriptions) from Indeed for a specific search condition comprising job title and location.
    - technologies used: BeautifulSoup
    - Inputs: job title, location
    - output: parquet file converted from the resulting pandas DataFrame

Usage: 
`python3 webscrape_jobpost_indeed.py "<JOB_TITLE>" "<LOCATION>"`
`python3 workopolis_jobs.py "<JOB_TITLE>" "<LOCATION>"`


### webscrape_salary_talent.py
    - Objective: This Python script is intended to periodically scrape average salary infomraiton for the pre-defined set of job titles from Talent and directly insert into MongoDB. (Salary info more than one month old will get replaced with the new salary figure.)
    - technologies used: BeautifulSoup, MongoClient
    - Inputs: None (A list of job titles for which annual salaries are scraped is maintained within the code)
    - output: None (Data inserted as a document into "AverageSalary" collection)
Usage: 
`python3 webscrape_salary_talent.py`

### glassdoor_scrape.py
    - Objective: This Python script is intended to scrape all the job posts and their relevant information (including job descriptions) from Glassdoor for a specific search condition comprising job title and location.
    - technologies used: Selenium, urllib
    - Inputs: job title, location
    - output: parquet file converted from the resulting pandas DataFrame (currently csv, will change to parquet later)
Usage: 
`python3 glassdoor_scrape.py "<JOB_TITLE>" "<LOCATION>"`

### webcrawling_linkedin.py
	- Objective: This Python script is intended to scrape all the job posts and their relevant information (including job descriptions) from Linkedin for a specific search condition comprising job title and location and the 
    - technologies used: LinkedIn API, BeautifulSoup and urllib
    - Inputs: job title, location and period for last n days (optional parameter - default 7 days)
    - Outputs: parquet file converted from the resulting pandas DataFrame
	- Note: without salary information as it is not available
Usage: 
`python3 webcrawling_linkedin.py "Production Technician" "Canada" 50`   # last 50 days

### webcrawling_linkedin_salary.py
	- Objective: This is the web scrapping for LinkedIn Salary Information (not job post specific)
	- salary range, average salary and post date will be obtained after the scrapping
	- technologies used: Selenium with Chrome, urllib
	- Inputs: job title, location
	- Outputs: base_salary, salary_range and post_date plus job title, location in parquet file

### converting_csv_to_parquet.py
	- Objective: this is for converting csv files (previously crawled) to parquet files
	- This program will read all csv files in a directory and convert all files in the directory to parquet files - output files will also be in the same directory
usage: 
`python3 converting_csv_to_parquet.py <folder_name>`

### web_scrapping_linkedin_script.sh
	- Objective: this is the web scrapping script specically for linkedin for job skill extraction model development
usage:
`./web_scrapping_linkedin_script.sh`



## 2. Data Pre-processing and Integration

### start-dataprocessing.sh
	- Objective: This shell script is intended to execute data processing scripts successively in the order they need to be executed.
		- Sequence #1: jobpost_integrator.py
		- Sequence #2: jobpost_cleaner.py
		- Sequence #3: jobpost_to_mongodb.py
		- Sequence #4: job_skill_model/job_skill_extraction_model_prediction.py
		- Sequence #5: jobskills_to_mongodb.py
usage:
`./start-dataprocessing.sh`

### jobpost_integrator.py
    - Objective: This python code is intended to consolidate all the job posts obtained from the 4 platforms, remove duplicate job records using Jaccard Similarity (based on job title / company / location), and output a single parquet file.
    - technologies used: Pandas, Numpy
	- Input files (before processing): parquet files located under "/preprocessing_parquet"
	- Input files (after processing): parquet files located under "/preprocessing_parquet/archive"
	- Output files : parquet files located under "/integrated_parquet"

### Pre-processing and postprocessing done in Job Skill extraction
	- Pre-processing and postprocessing have been done on job descriptions across job posts so that
	Pre-processing
	1. Handling contracted form of phrase
	2. Converting to lowercase
	3. Replacing symbols and puntuations
	4. Removing new lines
	5. Handling and/or
	6. Handling & (amp)
	
	Post-processing, includes
	1. stripping front and back spaces and puntuations
	2. handling of words "a" "an" "this" "the" etc at the front or back of phrase
	3. handling of "."


## 3. Data Cleaning and Standardization

The main task in order to obtain trends and visualization was to standardize data for both JobPosts and Employee data collection. 

### jobpost_cleaner.py
    - Objective: This python code is intended to read the integrated parquet files generated by "jobpost_integrator.py" and apply data cleaning/transformations before they can get pushed to MongoDB.
    - technologies used: Pandas, Numpy
	- Input files (before processing): parquet files located under "/integrated_parquet"
	- Input files (after processing): parquet files located under "/integrated_parquet/archive"
	- Output files : parquet files located under "/postprocessing_parquet"

### JobRole_EDA.ipynb 
In JobRole_EDA.ipynb location is seggregated based on province. 
The salary expectation was given for half of the total dataset there created a new column to get the average salary for each jobrole from the average data collection. 
Found distibution of jobs based on location and salary. 
The dataset while fetching the jobs from four different platforms included some job which were irrelevant to the search_kw (search keyword). Inorder to remove those jaccard similarity and sequence matcher where used. In addition NLTK was also implemented which given considerable results to match job titles for some of the search keywords. 

### IBM_Employee_Dataset.ipynb
In JobRole_EDA.ipynb found distrubtion based on each category. 
Monthly rate, monthlyincome and hourly rate where standardized to get yearly payout 
Found outliers to eliminate bias, if any. 
Found correlation in the dataset and difference between salary average to gauge the data flow. 


## 4. Data Storage

### mongodb_connector.py
    - Objective: This python code serves as a common custom library that will enable other codes to connect to "EmployeeRetentionDB" database with a single line of code.

### mongodb_initializer.py
    - Objective: This python code is intended clear all the documents from all the MongoDB collections available.

### jobpost_to_mongodb.py
    - Objective: This python code is intended to read the cleaned parquet files generated by "jobpost_cleaner.py" and push all the records to MongoDB.
	- Input files (before processing): parquet files located under "/postprocessing_parquet"
	- Input files (after processing): parquet files located under "/postprocessing_parquet/archive"
	- Output files : None

### jobskills_to_mongodb.py
    - Objective: This python code is intended to load parquet files containing predicted skills for respective job titles (which were generated by "job_skill_model/job_skill_extraction_model_prediction.py") and push all the records to MongoDB.
	- Input files (before processing): parquet files located under "/job_skill_model/job_skill_prediction"
	- Input files (after processing): parquet files located under "/job_skill_model/job_skill_prediction/archive"
	- Output files : None
**Note:** Jobskills collection will by default be initialized before it inserts a new set of records.

### employees_to_mongodb.py
    - Objective: This python code is intended to load employees information from IBM dataset and directly push them to MongoDB "Employees" collection.
	- Input file: IBM Emloyees dataset with attrition ("sample_file/WA_Fn-UseC_-HR-Employee-Attrition.csv")
	- Output files : None


## 5. Data Analysis

Model Built:

1. Extracting Job Skills from Different Job Postings

This main task is to built a Job Skill Extraction Model - all files contained in job_skill_model folder
### data_exploration_job_skills.ipynb
	- Objective: data exploration (EDA) and data pre-processing and preparation on job descriptions, including
		- Tokenization
		- Stop Words Removal
		- Lemmatization
### job_skill_extraction_model_training.ipynb
	- Objective: Training of the Job Skill Extraction Model with BERT Embedding
### job_skill_extraction_model_evaluation.ipynb
	- Objective: Evaluation of Job Skill Extraction Model with sample data
### job_skill_extraction_model_prediction.ipynb
	- Objective: Illustration of how the model will be used for skill extraction for other posts, developed not using full dataset
	
	- Equivalent files in py will be used for the real skill extraction on full job post dataset
		- job_skill_extraction_model_prediction.py: Main function to call for 
		- job_skill_extraction_data_processing.py: Library functions for data pre- and post- processing 
		- job_skill_extraction_model.py: Class functions for model built with feature conversion, BERT embedding and network architecture build
### job_skill_extraction_model_prediction.py
	- Objective: this is for extracting job skills from job posts crawled across all job market platforms (LinkedIn, Workoplis, Indeed and Glassdoor)
	- This program will read all job posts data from parquet and extract the job skills from each job posts
	- The resulting skills extracted will be attached to the original job posts / separate table containing only job title - skill pairs
	- Input files : parquet files located under "postprocessing_parquet/archive/"
	- Output files : parquet files located under "job_skill_model/job_skill_prediction"
usage:
`python3 job_skill_extraction_model_prediction.py model/job_skill_extraction_bert.h5`
	
where model/job_skill_extraction_bert.h5 is the trained job skill extraction model

### Others	
- [Folder] evaluation_data: sample data and output used for model evaluation
- [Folder] processing: processed / processing data for model built
- [Model] job_skill_extraction_bert.h5: trained network model with BERT embedding - not uploaded since it is over 1GB

## 6. Visualization (Front-end Development)

### 1. Web application for employee retention prediction
- technologies used: pythonanywhere with python backend rendering html templates with js and css using Flask
- web technologies used: html, boostrap and jQuery; Chart.js for plotting charts interactively

The web application consists of five parts:
a. About project ("/") - which contains introduction of our project and architecture
b. Predict - Enter Employee ("/employee_forecast") - which allows users to input employee information for getting immediate prediction of employee retention
c. Predict - Select Employee ("/select_employee_forecast") - which allows users to select from existing employee information for getting immediate prediction of employee retention
d. Our Analysis - ("/analysis") - which illustrates our detailed analysis of the employee dataset and job posts across 4 platforms
e. Our Models - ("/models") - which describe the list of models used in our employee retention and job market analysis and predictions

Backend python files:
1. index_page.py - main python program for rendering 5 webpages plus result page after enquiry
2. greeting.py - provides greeting in index page according to time (morning, afternoon, evening and night)
3. employee_retention_forecast.py - contains functions for employee retention prediction and job skills listings for similar jobs

### 2. Tableau visualization
Used JobRole and IBM Employee Dataset for visualization and comparison using Tableau. 
link: https://public.tableau.com/app/profile/rakhi6857/viz/JobRole_16493972035820/Sheet5
