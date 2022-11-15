#*************************************
# Created by: Rovenna Chu (ytc17@sfu.ca)
# Purpose: this is the schema of job market data for web scrapping functions across the 4 job platforms - LinkedIn, Indeed, Workoplis and Glassdoor
#*************************************

columns = [ "id",
			"job_title",
			"job_type", #A list of job types (full-time, contract, part-time, temporary, internship, volunteer and "other", respectively)
			"job_exp", #experience: A list of experience levels, one or many of "1", "2", "3", "4", "5" and "6" (internship, entry level, associate, mid-senior level, director and executive, respectively)
			"company", 
			"industries", #A list of industry  (str)
			"location",
			"source",       # sourced from : "Indeed", "Linkedin", "Workpolis", "Glassdoor" 
			"search_kw",
			"expected_salary",	#salary range: CA$54,000 - CA$115,000
			"post_date",
            "job_function",
            "remote",         #"remote" if job_workRemoteAllowed else ""
            "job_summary",
			"description"
			]