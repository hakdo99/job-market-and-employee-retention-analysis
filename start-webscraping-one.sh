#!/usr/bin/bash

# Pre-requisite
# pip install pyarrow
# pip install fastparquet
# 

echo "Web Scraping gets started."

location="Canada"
jobtile="Recruiter"

echo "**************************** starting web scraping for $jobtile ****************************"
python3 workopolis_jobs.py "$jobtile" "$location" &
python3 webcrawling_linkedin.py "$jobtile" "$location" 15 &
python3 webscrape_jobpost_indeed.py "$jobtile" "$location" &
python3 glassdoor_scraping.py "$jobtile" "$location" &
wait
echo "**************************** Web scraping completed for $jobtile ****************************"

echo "Web Scraping is completed."
