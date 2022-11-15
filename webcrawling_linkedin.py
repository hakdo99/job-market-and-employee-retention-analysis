#*************************************
# Created by: Rovenna Chu (ytc17@sfu.ca)
# Purpose: this is the web crawler for LinkedIn (Job Posting Platform)
#  - without salary information as it is not available
#  - usage: python3 webcrawling_linkedin.py "Production Technician" "Canada" 50 #last 50 days
#*************************************

import json
import random
import requests
import string
import time
from time import sleep
from urllib.parse import quote, urlencode
from bs4 import BeautifulSoup


import logging
import sys


from schema import columns
import pandas as pd

logger = logging.getLogger("log.txt")


MAX_POST_COUNT = 100  # max seems to be 100 posts per page
MAX_UPDATE_COUNT = 100  # max seems to be 100
MAX_SEARCH_COUNT = 49  # max seems to be 49, and min seems to be 2
MAX_REPEATED_REQUESTS = (
    200  # VERY conservative max requests count to avoid rate-limit
)
LINKEDIN_BASE_URL = "https://www.linkedin.com"
API_BASE_URL = f"{LINKEDIN_BASE_URL}/voyager/api"
DESTINATION_FOLDER = "preprocessing_parquet"
 
def auth(credentials):
    '''
    Run the Authentication.
    If the access token exists, it will use it to skip browser auth.
    If not, it will open the browser for you to authenticate.
    You will have to manually paste the redirect URI in the prompt.
    '''
    creds = read_creds(credentials)
    print(creds)
    client_id, client_secret = creds['client_id'], creds['client_secret']
    redirect_uri = creds['redirect_uri']
    api_url = 'https://www.linkedin.com/oauth/v2' 
         
    if 'access_token' not in creds.keys(): 
        args = client_id,client_secret,redirect_uri
        auth_code = authorize(api_url,*args)
        access_token = refresh_token(auth_code,*args)
        creds.update({'access_token':access_token})
        save_token(credentials,creds)
    else: 
        access_token = creds['access_token']
    return access_token
 
def headers(access_token):
    '''
    Make the headers to attach to the API call.
    '''
    headers = {
    'Authorization': f'Bearer {access_token}',
    'cache-control': 'no-cache',
    'X-Restli-Protocol-Version': '2.0.0'
    }
    return headers
 
def read_creds(filename):
    '''
    Store API credentials in a safe place.
    If you use Git, make sure to add the file to .gitignore
    '''
    with open(filename) as f:
        credentials = json.load(f)
    return credentials
 
def save_token(filename,data):
    '''
    Write token to credentials file.
    '''
    data = json.dumps(data, indent = 4) 
    with open(filename, 'w') as f: 
        f.write(data)
 
def create_CSRF_token():
    '''
    This function generate a random string of letters.
    It is not required by the Linkedin API to use a CSRF token.
    However, it is recommended to protect against cross-site request forgery
    For more info on CSRF https://en.wikipedia.org/wiki/Cross-site_request_forgery
    '''
    letters = string.ascii_lowercase
    token = ''.join(random.choice(letters) for i in range(20))
    return token
 
def open_url(url):
    '''
    Function to Open URL.
    Used to open the authorization link
    '''
    import webbrowser
    print(url)
    webbrowser.open(url)
 
def parse_redirect_uri(redirect_response):
    '''
    Parse redirect response into components.
    Extract the authorized token from the redirect uri.
    '''
    from urllib.parse import urlparse, parse_qs
 
    url = urlparse(redirect_response)
    url = parse_qs(url.query)
    return url['code'][0]
 
def authorize(api_url,client_id,client_secret,redirect_uri):
    # Request authentication URL
    csrf_token = create_CSRF_token()
    params = {
        'response_type': 'code',
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'state': csrf_token,
        'scope': 'r_liteprofile,r_emailaddress,w_member_social'
        }
 
    response = requests.get(f'{api_url}/authorization',params=params)
 
    print(f'''
    The Browser will open to ask you to authorize the credentials.\n
    Since we have not setted up a server, you will get the error:\n
    This site can’t be reached. localhost refused to connect.\n
    This is normal.\n
    You need to copy the URL where you are being redirected to.\n
    ''')
 
    open_url(response.url)
 
    # Get the authorization verifier code from the callback url
    redirect_response = input('Paste the full redirect URL here:')
    auth_code = parse_redirect_uri(redirect_response)
    return auth_code
 
def refresh_token(auth_code,client_id,client_secret,redirect_uri):
    '''
    Exchange a Refresh Token for a New Access Token.
    '''
    access_token_url = 'https://www.linkedin.com/oauth/v2/accessToken'
 
    data = {
        'grant_type': 'authorization_code',
        'code': auth_code,
        'redirect_uri': redirect_uri,
        'client_id': client_id,
        'client_secret': client_secret
        }
 
    response = requests.post(access_token_url, data=data, timeout=30)
    response = response.json()
    print(response)
    access_token = response['access_token']
    return access_token
    
def user_info(headers):
    '''
    Get user information from Linkedin
    '''
    response = requests.get('https://api.linkedin.com/v2/me', headers = headers)
    user_info = response.json()
    return user_info

def get_job_details(session, urn_id):
    '''
    Get user information from Linkedin
    '''
    
    #url of the data source
    
    url = "https://www.linkedin.com/jobs/view/"+urn_id
    
    print('Job Detail URL to be extracted: '+url)
    
    sleep(random.randint(2, 7))
    response = requests.get(url)
    html_soup = BeautifulSoup(response.text, 'html.parser')
    
    #with open("job_page.html", "w") as file:
    #    file.write(str(html_soup))
        
    print("Finish crawling and saving")
    print()
    
    info_containers = html_soup.find_all('li', class_ = "description__job-criteria-item")
    
    job_type = ""
    industry = ""
    job_details = ""
    job_exp = ""
    job_function = ""
    job_details = ""
    company_name = ""
    
    for e in info_containers:
        if "Seniority level" in e.h3.get_text():
            job_exp = e.span.text.strip()
        elif "Employment type" in e.h3.get_text():
            job_type = e.span.text.strip()
        elif "Job function" in e.h3.get_text():
            job_function = e.span.text.strip()
        elif "Industries" in e.h3.get_text():
            industry = e.span.text.strip()
        else:
            pass
    
    job_details_container = html_soup.find("div", class_ = "show-more-less-html__markup--clamp-after-5")

    
    if job_details_container is not None:
        import re
        tag = re.compile('<.*?>')
        job_details = re.sub(tag, "\n", str(job_details_container))
        
    company_name_container = html_soup.find('a', class_ = "sub-nav-cta__optional-url")
    
    if company_name_container is not None:
        company_name = company_name_container.text
    
    return job_type, industry, job_details, job_exp, job_function, company_name


# extract job posts using linkedin api voyager
def search_jobs_all(
    session=None,
    keywords=None,
    companies=None,
    experience=None,
    job_type=None,
    job_title=None,
    industries=None,
    location_name=None,
    remote=False,
    listed_at=7 * 24 * 60 * 60,
    distance=None,
    limit=-1,
    offset=0,
    **kwargs,
):
    """Perform a LinkedIn search for jobs.
    :param keywords: Search keywords (str)
    :type keywords: str, optional
    :param companies: A list of company URN IDs (str)
    :type companies: list, optional
    :param experience: A list of experience levels, one or many of "1", "2", "3", "4", "5" and "6" (internship, entry level, associate, mid-senior level, director and executive, respectively)
    :type experience: list, optional
    :param job_type:  A list of job types , one or many of "F", "C", "P", "T", "I", "V", "O" (full-time, contract, part-time, temporary, internship, volunteer and "other", respectively)
    :type job_type: list, optional
    :param job_title: A list of title URN IDs (str)
    :type job_title: list, optional
    :param industries: A list of industry URN IDs (str)
    :type industries: list, optional
    :param location_name: Name of the location to search within. Example: "Kyiv City, Ukraine"
    :type location_name: str, optional
    :param remote: Whether to search only for remote jobs. Defaults to False.
    :type remote: boolean, optional
    :param listed_at: maximum number of seconds passed since job posting. 86400 will filter job postings posted in last 24 hours.
    :type listed_at: int/str, optional. Default value is equal to 24 hours.
    :param distance: maximum distance from location in miles
    :type distance: int/str, optional. If not specified, None or 0, the default value of 25 miles applied.
    :param limit: maximum number of results obtained from API queries. -1 means maximum which is defined by constants and is equal to 1000 now.
    :type limit: int, optional, default -1
    :param offset: indicates how many search results shall be skipped
    :type offset: int, optional
    :return: List of jobs
    :rtype: list
    """
    
    count = MAX_SEARCH_COUNT
    if limit is None:
        limit = -1
        
    params = {}
    if keywords:
        params["keywords"] = keywords

    filters = ["resultType->JOBS"]
    if companies:
        filters.append(f'company->{"|".join(companies)}')
    if experience:
        filters.append(f'experience->{"|".join(experience)}')
    if job_type:
        filters.append(f'jobType->{"|".join(job_type)}')
    if job_title:
        filters.append(f'title->{"|".join(job_title)}')
    if industries:
        filters.append(f'industry->{"|".join(industries)}')
    if location_name:
        filters.append(f"locationFallback->{location_name}")
    if remote:
        filters.append(f"workRemoteAllowed->{remote}")
    if distance:
        filters.append(f"distance->{distance}")
    filters.append(f"timePostedRange->r{listed_at}")
    # add optional kwargs to a filter
    for name, value in kwargs.items():
        if type(value) in (list, tuple):
            filters.append(f'{name}->{"|".join(value)}')
        else:
            filters.append(f"{name}->{value}")
    
    
    results = []
    
    results_df = pd.DataFrame(columns = columns)

    while True:
        # when we're close to the limit, only fetch what we need to
        if limit > -1 and limit - len(results) < count:
            count = limit - len(results)
        default_params = {
            "decorationId": "com.linkedin.voyager.deco.jserp.WebJobSearchHitLite-14",
            "count": count,
            "filters": f"List({','.join(filters)})",
            "origin": "JOB_SEARCH_RESULTS_PAGE",
            "q": "jserpFilters",
            "start": len(results) + offset,
            "queryContext": "List(primaryHitType->JOBS,spellCorrectionEnabled->true)",
        }
        default_params.update(params)
        

        
        sleep(random.randint(2, 5))
        uri = f"/search/hits?{urlencode(default_params, safe='(),')}"
        url = f"{API_BASE_URL}{uri}"
        
        current_time = time.time()
        
        #print('url')   
        #print(url)
        #print()
        
        res = s.get(url)
        
        data = res.json()
        
        elements = data.get("elements", [])
        
        try:
        
            for r in elements:
                
                #initialize values to extract
                i = 0
                job_title = ""
                company = ""
                job_workRemoteAllowed = ""
                location = ""
                job_type = ""
                industry = ""
                job_details = ""
                job_exp = ""
                job_function = ""
                job_details = ""
                company_name = ""
                job_time = 0
                
                #extract from listing, format will be "urn:li:fs_normalized_jobPosting:2931001414"
                record = r["hitInfo"]['com.linkedin.voyager.deco.jserp.WebSearchJobJserpLite']
                i = record["jobPosting"][record["jobPosting"].rfind(':')+1:]
                
                
                #print('id')
                #print(i)
                #print()
                
                
                job_title = record["jobPostingResolutionResult"]["title"]
                
                
                #print('job_title')
                #print(job_title)
                #print()
                
                job_workRemoteAllowed = record["jobPostingResolutionResult"]["workRemoteAllowed"]
                
                #print('remote')
                #print("remote" if job_workRemoteAllowed else "")
                #print()
                
                company_record = record["jobPostingResolutionResult"]["companyDetails"]
                
                #print(record["jobPostingResolutionResult"]["companyDetails"])
                
                if 'com.linkedin.voyager.deco.jserp.WebJobPostingWithCompanyName' in company_record:
                    if "companyResolutionResult" in company_record['com.linkedin.voyager.deco.jserp.WebJobPostingWithCompanyName']:
                        company = company_record['com.linkedin.voyager.deco.jserp.WebJobPostingWithCompanyName']["companyResolutionResult"]["name"]
                    else:
                        company = company_record['com.linkedin.voyager.deco.jserp.WebJobPostingWithCompanyName']["company"]
                else: 
                    company = company_record['com.linkedin.voyager.jobs.JobPostingCompanyName']["companyName"]
                
                #print('company')
                #print(company)
                #print()
                #['com.linkedin.voyager.deco.jserp.WebJobPostingWithCompanyName']["companyResolutionResult"]["name"]

                location = record["jobPostingResolutionResult"]["formattedLocation"]
                
                job_type, industry, job_details, job_exp, job_function, company_name = get_job_details(s, i)
                
                job_time = record["jobPostingResolutionResult"]["listedAt"]
                
                #print('job_details')
                #print(job_details)
                #print()
                
                new_row = {"id": i, "job_title": job_title, "job_type": job_type, "job_exp": job_exp, "company": company if (company == company_name) else (company_name if (company == company_name) else company), "industries": industry, "location": location, "description": job_details, "source": "Linkedin", "search_kw": keywords, "expected_salary": "", "post_date": job_time, "job_function": job_function, "remote":"remote" if job_workRemoteAllowed else "" }
                
                #print('new_row')
                #print(new_row)
                
                results_df = results_df.append(new_row, ignore_index = True)
                
                results.append(
                    [
                        record
                    ]
                )
                
        except KeyError as error:
            print(error)
            
            #make sure we append the currect record
            new_row = {"id": i, "job_title": job_title, "job_type": job_type, "job_exp": job_exp, "company": company if (company == company_name) else (company_name if (company == company_name) else company), "industries": industry, "location": location, "description": job_details, "source": "Linkedin", "search_kw": keywords, "expected_salary": "", "post_date": job_time, "job_function": job_function, "remote":"remote" if job_workRemoteAllowed else "" }
                
            results_df = results_df.append(new_row, ignore_index = True)
            
            pass

        # break the loop if we're done searching
        # NOTE: we could also check for the `total` returned in the response.
        # This is in data["data"]["paging"]["total"]
        if (
            (-1 < limit <= len(results))  # if our results exceed set limit
            or len(results) / count >= MAX_REPEATED_REQUESTS
        ) or (len(elements) == 0) or (len(results) == data["paging"]["total"]):
            break
        
        logger.debug(f"results grew to {len(results)}")
    
    results_df["post_date"] = pd.to_datetime(results_df["post_date"], unit='ms')
    
    return results_df
 
if __name__ == '__main__':
    keywords = "data scientist"
    location = "Canada"
    period = 7
    
    if len(sys.argv) == 3:
        keywords = sys.argv[1]
        location = sys.argv[2]
    elif len(sys.argv) == 4:
        keywords = sys.argv[1]
        location = sys.argv[2]
        period = int(sys.argv[3])
    
    print('web crawling keywords {} and location {} in LinkedIn...for past {} days'.format(keywords, location, period))

    credentials = 'credentials_linkedin.json'
    access_token = auth(credentials)
    headers = headers(access_token) # Make the headers to attach to the API call.
    user_info = user_info(headers) # Get user info
    #print(user_info)
    
    with requests.session() as s:
        creds = read_creds(credentials)
        s.cookies['li_at'] = creds["li_at"]
        s.cookies["JSESSIONID"] = creds["JSESSIONID"]
        s.headers = headers
        s.headers["csrf-token"] = s.cookies["JSESSIONID"].strip('"')
        results_df = search_jobs_all(session=s,keywords=keywords, location_name=location, listed_at= period * 24 * 60 * 60)
        
        print('Data Extraction completed for keywords {} and location {} for past {} days'.format(keywords, location, period))
        
        results_df.to_parquet(DESTINATION_FOLDER + "/" + "LinkedIn_{}_{}_{}.parquet".format(keywords, location, pd.datetime.now().strftime("%Y-%m-%d %H%M%S")))