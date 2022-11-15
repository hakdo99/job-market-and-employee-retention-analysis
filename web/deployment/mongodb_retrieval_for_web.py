from unicodedata import ucd_3_2_0
from mongodb_connector import connect_to_collection
import pandas as pd
avgsal_collect = connect_to_collection("AverageSalary")
jobskills_collect = connect_to_collection("JobSkills")
jobposts_collect = connect_to_collection("JobPosts")
avgsal_df = pd.DataFrame(list(avgsal_collect.find()))
jobskills = pd.DataFrame(list(jobskills_collect.find()))
jobposts = pd.DataFrame(list(jobposts_collect.find()))
skills_join = pd.merge(jobskills, jobposts, on='job_title', how='inner')

def get_agv_sal(job_title):
    if (job_title == "Human Resources"):
        return avgsal_df.loc[avgsal_df['occupation'] == 'recruiter', 'salary'].item()
    else:
        return avgsal_df.loc[avgsal_df['occupation'] == job_title.lower(), 'salary'].item()

def get_top_skills(job_title):
    if (job_title == "Human Resources"):
        job_matches = skills_join[skills_join['search_kw'] == "Recruiter"]
    else:
        job_matches = skills_join[skills_join['search_kw'] == job_title]
    unique_text_prob = job_matches[job_matches['prediction_prob'] >= 0.5].groupby(['text','prediction_prob'], as_index=False).first()
    if (unique_text_prob.shape[0] >= 5):
        top_skills = unique_text_prob.nlargest(5, 'prediction_prob')[['text','prediction_prob']]
    else:
        top_skills = unique_text_prob[['text','prediction_prob']]
    return top_skills['text'].values.tolist()