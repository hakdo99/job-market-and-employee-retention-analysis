#!/usr/bin/bash

# Pre-requisite
# pip install pyarrow
# pip install fastparquet
# 

echo "Data processing gets started."

# 1. Consolidate all the job posts obtained from the 4 platforms
echo "**************************** starting the integration of job posts ****************************"
python3 jobpost_integrator.py
echo "**************************** the integration of job posts (comleted) ****************************"

# 2. Clean and standardize the data formats
echo "**************************** starting the standardization of job posts ****************************"
python3 jobpost_cleaner.py
echo "**************************** the standardization of job posts (comleted) ****************************"

# 3. Push the processed job posts to MongoDB
echo "**************************** starting the uploading of job posts to MongoDB ****************************"
python3 jobpost_to_mongodb.py
echo "**************************** the uploading of job posts to MongoDB (comleted) ****************************"

# 4. Extract jobskills for respective job titles scraped
echo "**************************** starting the extraction of job skills to job posts ****************************"
python3 job_skill_model/job_skill_extraction_model_prediction.py
echo "**************************** the extraction of job skills to job posts (comleted) ****************************"

# 5. Push the extracted job skills to MongoDB
echo "**************************** starting the uploading of job skills to MongoDB ****************************"
python3 jobskills_to_mongodb.py
echo "**************************** the uploading of job skills to MongoDB (comleted) ****************************"

echo "Data processing is completed."
