from urllib import request
import flask
import pandas as pd
import json

from greeting import get_part_of_day
from employee_retention_forecast import get_prediction, get_skill_extractions, predict
#from flask_cors import CORS, cross_origin
from mongodb_retrieval_for_web import get_agv_sal, get_top_skills
# A simple Flask App which takes

# a user's name as input and responds
# with "Hello {name}!"

app = flask.Flask(__name__)
#cors = CORS(app)

@app.route('/', methods=['GET', 'POST'])

def index():
    # To use current hour:
    from datetime import datetime
    import pytz
    d = datetime.now()
    timezone = pytz.timezone("America/Los_Angeles")
    d_aware = timezone.localize(d)
    part = get_part_of_day(int(d_aware.hour))
    message = "Good "+part+"! Welcome to our project Presentation!"
    #if flask.request.method == 'POST':
    #    message = 'Hello ' + flask.request.form['name-input'] + '!'
    return flask.render_template('index.html', message=message)

@app.route('/employee_forecast', methods=['GET', 'POST'])

def forecast_results_page():
    json_results = {}
    if flask.request.method == 'POST':
        #get employee information inputs
        employee = {}
        employee['name'] = flask.request.form['name-input']
        employee['Age'] = flask.request.form['age']
        employee['Department'] = flask.request.form['department']
        employee['Gender'] = flask.request.form['gender']
        employee['MaritalStatus'] = flask.request.form['marital_status']
        employee['EducationField'] = flask.request.form['ed_field']
        employee['Education'] = flask.request.form['ed_level']
        employee['NumCompaniesWorked'] = flask.request.form['num_companies_worked']
        employee['TotalWorkingYears'] = flask.request.form['total_working_years']
        employee['JobLevel'] = flask.request.form['job_level']
        employee['JobRole'] = flask.request.form['job_role']
        employee['BusinessTravel'] = flask.request.form['business_travel']
        employee['DistanceFromHome'] = flask.request.form['distance']
        employee['OverTime'] = flask.request.form['overtime']
        employee['MonthlyIncome'] = flask.request.form['monthly_income']
        employee['PercentSalaryHike'] = flask.request.form['raise']
        employee['HourlyRate'] = flask.request.form['hourly_rate']
        employee['DailyRate'] = flask.request.form['daily_rate']
        employee['MonthlyRate'] = flask.request.form['monthly_rate']
        employee['TrainingTimesLastYear'] = flask.request.form['training_times']
        employee['JobInvolvement'] = flask.request.form['job_involvement']
        employee['PerformanceRating'] = flask.request.form['performance']
        employee['RelationshipSatisfaction'] = flask.request.form['rela_satisfaction']
        employee['EnvironmentSatisfaction'] = flask.request.form['env_satisfaction']
        employee['WorkLifeBalance'] = flask.request.form['work_life_balance']
        employee['YearsInCurrentRole'] = flask.request.form['years_curr_role']
        employee['YearsAtCompany'] = flask.request.form['years_at_company']
        employee['YearsSinceLastPromotion'] = flask.request.form['years_since_last_promo']
        employee['YearsWithCurrManager'] = flask.request.form['years_with_curr_manager']
        employee['JobSatisfaction'] = flask.request.form['job_satisfaction']
        employee['StockOptionLevel'] = flask.request.form['stock']


        #make predictions using model
        predictions = get_prediction(employee)
        pred = predict(employee)
        leave = "{:.2%}".format(pred[1])        

        #job skill extraction results
        job_title = employee['JobRole'] if employee['JobRole']!="Manager" else employee['Department']+" "+employee['JobRole']
        avg_salary = get_agv_sal(job_title)        
        skill_extracts = get_top_skills(job_title)
        # skills = []
        # skills.append({"skillset": skill_extracts.to_dict(orient = 'records')})
        #skills = json.dumps(skill_extracts)

        #pack into json
        json_data = []
        json_data.append({"charts": predictions.to_dict(orient="records")})
        #json_data.append({"skills": skill_extracts.to_dict(orient="records")})
        #json_results = json.dumps(json_data)

        #render results page
        return flask.render_template('employee_prediction_input_result.html', skills = skill_extracts, avg_salary = avg_salary, prediction = pred, leave = leave, results=json_data, name = employee['name'], job_title = job_title)
    else:
        return flask.render_template('employee_prediction_input.html')

@app.route('/select_employee_forecast', methods=['GET', 'POST'])
# <url: anywherepython, localhost, aws...>/select_employee_forcast --POST--> <url: anywherepython, localhost, aws...>/select_employee_forcast
# Since we're sending it to ourselves, in JS, use '.' (Linux's notation for current directory)
def selected_forecast_results_page():
    json_results = {}
    employee_data = {}
    with open("C:/Users/dokha/school-projects/job-market-and-employee-engagement-dashboard/web/deployment/sample_employee_table.json") as jsonfile:
        employee_list = json.load(jsonfile)
    if flask.request.method == 'POST':
        #*********TODO: get employee information inputs from selected table
        #employee = {}
        value = int(flask.request.form.get('index'))
        employee = employee_list[value - 1]
        #employee['name'] = ''
        #*********TODO END**************************

        #make predictions using model
        predictions = predict(employee)
        leave = "{:.2%}".format(predictions[1])

        #job skill extraction results
        job_title = employee['JobRole'] if employee['JobRole']!="Manager" else employee['Department']+" "+employee['JobRole']
        avg_salary = get_agv_sal(job_title)
        skill_extracts = get_top_skills(job_title)
        #skills = json.dumps(skill_extracts)

        #pack into json
        json_data = []
        json_data.append({"charts": predictions})
        # skills = []
        # skills.append({"skillset": skill_extracts.to_dict(orient = 'records')})
        #json_data.append({"skills": skill_extracts.to_dict(orient="records")})
        #json_results = json.dumps(json_data)

        #render results page
        return flask.render_template('employee_prediction_input_result.html', skills = skill_extracts, prediction=predictions, avg_salary = avg_salary, leave = leave, results=json_data, name = employee['name'], job_title = job_title)
    else:
        return flask.render_template('employee_prediction_select.html', employees = employee_list)
    """
    elif flask.request.method == 'GET':
        #*********TODO: get existing dummy data selected the table
        return flask.render_template('employee_prediction_select.html', results=employee_data)
    """

@app.route('/analysis', methods=['GET'])

def analysis_page():
    return flask.render_template('analysis.html')


@app.route('/model', methods=['GET'])

def model_page():
    return flask.render_template('models.html')

if __name__ == '__main__':
    app.run()