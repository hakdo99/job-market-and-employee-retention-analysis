from mongodb_connector import connect_to_collection
import pandas as pd
# import pyspark
# from pyspark.sql import SparkSession
# spark = SparkSession.builder.appName('sparkdf').getOrCreate()


jobskills_collect = connect_to_collection("JobSkills")
jobskills = pd.DataFrame(list(jobskills_collect.find()))
avgsal_collect = connect_to_collection("AverageSalary")
jobposts_collect = connect_to_collection("JobPosts")
df = pd.DataFrame(list(avgsal_collect.find()))
data_scientist_salary = df.loc[df['occupation'] == 'recruiter', 'salary'].item()
print(data_scientist_salary)
jobposts = pd.DataFrame(list(jobposts_collect.find()))
df_inner = pd.merge(jobskills, jobposts, on='job_title', how='inner')
job_matches = df_inner[df_inner['search_kw'] == "Recruiter"]
job_matches = job_matches.groupby(['text','prediction_prob'], as_index=False).first()
data = job_matches[job_matches['prediction_prob'] >= 0.5]
print(data.head())
#print(job_matches['prediction_prob'])
# top_skills = job_matches.nlargest(5, 'prediction_prob')[['text','prediction_prob']]
# print(top_skills['text'].values.tolist())
