#!/usr/bin/bash

# Pre-requisite
# pip install pyarrow
# pip install fastparquet
# 

echo "Web Scraping gets started."

location="Canada"
jobtile1="Sales Executive"

echo "**************************** starting web scraping for $jobtile1 ****************************"
python3 workopolis_jobs.py "$jobtile1" "$location" &
python3 webcrawling_linkedin.py "$jobtile1" "$location" 15 &
python3 webscrape_jobpost_indeed.py "$jobtile1" "$location" &
python3 glassdoor_scraping.py "$jobtile1" "$location" &
wait
echo "**************************** Web scraping completed for $jobtile1 ****************************"

jobtile2="Research Scientist"

echo "**************************** starting web scraping for $jobtile2 ****************************"
python3 workopolis_jobs.py "$jobtile2" "$location" &
python3 webcrawling_linkedin.py "$jobtile2" "$location" 15 &
python3 webscrape_jobpost_indeed.py "$jobtile2" "$location" &
python3 glassdoor_scraping.py "$jobtile2" "$location" &
wait
echo "**************************** Web scraping completed for $jobtile2 ****************************"

jobtile3="Laboratory Technician"

echo "**************************** starting web scraping for $jobtile3 ****************************"
python3 workopolis_jobs.py "$jobtile3" "$location" &
python3 webcrawling_linkedin.py "$jobtile3" "$location" 15 &
python3 webscrape_jobpost_indeed.py "$jobtile3" "$location" &
python3 glassdoor_scraping.py "$jobtile3" "$location" &
wait
echo "**************************** Web scraping completed for $jobtile3 ****************************"

jobtile4="Manufacturing Director"

echo "**************************** starting web scraping for $jobtile4 ****************************"
python3 workopolis_jobs.py "$jobtile4" "$location" &
python3 webcrawling_linkedin.py "$jobtile4" "$location" 15 &
python3 webscrape_jobpost_indeed.py "$jobtile4" "$location" &
python3 glassdoor_scraping.py "$jobtile4" "$location" &
wait
echo "**************************** Web scraping completed for $jobtile4 ****************************"

jobtile5="Healthcare Representative"

echo "**************************** starting web scraping for $jobtile5 ****************************"
python3 workopolis_jobs.py "$jobtile5" "$location" &
python3 webcrawling_linkedin.py "$jobtile5" "$location" 15 &
python3 webscrape_jobpost_indeed.py "$jobtile5" "$location" &
python3 glassdoor_scraping.py "$jobtile5" "$location" &
wait
echo "**************************** Web scraping completed for $jobtile5 ****************************"

jobtile6="Sales Manager"

echo "**************************** starting web scraping for $jobtile6 ****************************"
python3 workopolis_jobs.py "$jobtile6" "$location" &
python3 webcrawling_linkedin.py "$jobtile6" "$location" 15 &
python3 webscrape_jobpost_indeed.py "$jobtile6" "$location" &
python3 glassdoor_scraping.py "$jobtile6" "$location" &
wait
echo "**************************** Web scraping completed for $jobtile6 ****************************"

jobtile7="Sales Representative"

echo "**************************** starting web scraping for $jobtile7 ****************************"
python3 workopolis_jobs.py "$jobtile7" "$location" &
python3 webcrawling_linkedin.py "$jobtile7" "$location" 15 &
python3 webscrape_jobpost_indeed.py "$jobtile7" "$location" &
python3 glassdoor_scraping.py "$jobtile7" "$location" &
wait
echo "**************************** Web scraping completed for $jobtile7 ****************************"

jobtile8="Research Director"

echo "**************************** starting web scraping for $jobtile8 ****************************"
python3 workopolis_jobs.py "$jobtile8" "$location" &
python3 webcrawling_linkedin.py "$jobtile8" "$location" 15 &
python3 webscrape_jobpost_indeed.py "$jobtile8" "$location" &
python3 glassdoor_scraping.py "$jobtile8" "$location" &
wait
echo "**************************** Web scraping completed for $jobtile8 ****************************"

jobtile9="Research Manager"

echo "**************************** starting web scraping for $jobtile9 ****************************"
python3 workopolis_jobs.py "$jobtile9" "$location" &
python3 webcrawling_linkedin.py "$jobtile9" "$location" 15 &
python3 webscrape_jobpost_indeed.py "$jobtile9" "$location" &
python3 glassdoor_scraping.py "$jobtile9" "$location" &
wait
echo "**************************** Web scraping completed for $jobtile9 ****************************"

jobtile10="Human Resources Manager"

echo "**************************** starting web scraping for $jobtile10 ****************************"
python3 workopolis_jobs.py "$jobtile10" "$location" &
python3 webcrawling_linkedin.py "$jobtile10" "$location" 15 &
python3 webscrape_jobpost_indeed.py "$jobtile10" "$location" &
python3 glassdoor_scraping.py "$jobtile10" "$location" &
wait
echo "**************************** Web scraping completed for $jobtile10 ****************************"

jobtile11="Human Resources Coordinator"

echo "**************************** starting web scraping for $jobtile11 ****************************"
python3 workopolis_jobs.py "$jobtile11" "$location" &
python3 webcrawling_linkedin.py "$jobtile11" "$location" 15 &
python3 webscrape_jobpost_indeed.py "$jobtile11" "$location" &
python3 glassdoor_scraping.py "$jobtile11" "$location" &
wait
echo "**************************** Web scraping completed for $jobtile11 ****************************"

jobtile12="Recruiter"

echo "**************************** starting web scraping for $jobtile12 ****************************"
python3 workopolis_jobs.py "$jobtile12" "$location" &
python3 webcrawling_linkedin.py "$jobtile12" "$location" 15 &
python3 webscrape_jobpost_indeed.py "$jobtile12" "$location" &
python3 glassdoor_scraping.py "$jobtile12" "$location" &
wait
echo "**************************** Web scraping completed for $jobtile12 ****************************"


echo "Web Scraping is completed."