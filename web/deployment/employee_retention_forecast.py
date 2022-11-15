import pandas as pd
import numpy as np
import joblib

dummies_path = "C:\\Users\\dokha\\school-projects\\job-market-and-employee-engagement-dashboard\\retention_prediction\\dummies.pkl"
model_path = "C:\\Users\\dokha\\school-projects\\job-market-and-employee-engagement-dashboard\\retention_prediction\\internal_retention_train_model.pkl"
dummies = joblib.load(dummies_path)
internal_retention_model = joblib.load(model_path)
#internal_retention_model = joblib.load("/home/dathusiats733/mysite/internal_retention_train_model.pkl")

def get_prediction(employee):
    data_string = '[{"Name":"Honda", "Price": 10000, "Model":2005, "Power": 1300},{"Name":"Toyota", "Price": 12000, "Model":2010, "Power": 1600},{"Name":"Audi", "Price": 25000, "Model":2017, "Power": 1800},{"Name":"Ford", "Price": 28000, "Model":2009, "Power": 1200}]'
    data = eval(data_string)
    result_df = pd.DataFrame(data)
    return result_df

def predict(employee):
    df = pd.DataFrame(employee, index = [0])
    df.loc[(df['BusinessTravel'] == "Frequent"), 'BusinessTravel'] = "Travel_Frequently"
    df.loc[(df['BusinessTravel'] == "Rare"), 'BusinessTravel'] = "Travel_Rarely"
    df.loc[(df['BusinessTravel'] == "None"), 'BusinessTravel'] = "Non-Travel"
    employee = dummies.transform(df.drop('name', axis=1))
    #print(employee)
    col_diff = set(dummies.columns).difference(set(employee.columns))
    col_diff = list(col_diff)
    for col in col_diff:
        employee[col] = 0
    #employee = pd.get_dummies(df.drop('name', axis=1), columns=dummy_col, dtype='uint8')
    pred_array = internal_retention_model.predict_proba(employee)
    pred = []
    for p in pred_array[0]:
        p = round(p, 2)
        pred.append(p)
    return pred

def get_skill_extractions(job_title, threshold=0.5):
    data_string = '[{"text":"activities maintain complete","job_title":"Assistant Human Resources Manager - (17638)","prediction_prob":"1.0578388", "predicted_skill":"1"}, {"text":"program management teams","job_title":"Software Development Manager, RDS Custom","prediction_prob":"1.1417567", "predicted_skill":"1"}, {"text":"people management","job_title":"Software Development Manager, RDS Custom","prediction_prob":"0.9833584", "predicted_skill":"1"}, {"text":"work","job_title":"Software Development Manager, RDS Custom","prediction_prob":"0.4545587", "predicted_skill":"0"}, {"text":"complex technical information","job_title":"Software Development Manager, RDS Custom","prediction_prob":"0.85649854", "predicted_skill":"1"}, {"text":"concise manner","job_title":"Software Development Manager, RDS Custom","prediction_prob":"0.7453244", "predicted_skill":"1"}, {"text":"variety","job_title":"Software Development Manager, RDS Custom","prediction_prob":"0.43003103", "predicted_skill":"0"}, {"text":"deep","job_title":"Software Development Manager, RDS Custom","prediction_prob":"0.83181626", "predicted_skill":"1"}, {"text":"software development lifecycle","job_title":"Software Development Manager, RDS Custom","prediction_prob":"1.3628174", "predicted_skill":"1"}, {"text":"scrum","job_title":"Software Development Manager, RDS Custom","prediction_prob":"1.3733512", "predicted_skill":"1"}, {"text":"kanban","job_title":"Software Development Manager, RDS Custom","prediction_prob":"0.65091825", "predicted_skill":"0"}, {"text":"methodology","job_title":"Software Development Manager, RDS Custom","prediction_prob":"0.93597776", "predicted_skill":"1"}, {"text":"professional software engineering practices","job_title":"Software Development Manager, RDS Custom","prediction_prob":"0.4348887", "predicted_skill":"0"}, {"text":"recruiting","job_title":"Senior Associate, Technology Recruitment","prediction_prob":"0.80762446", "predicted_skill":"1"}, {"text":"technology recruitment","job_title":"Senior Associate, Technology Recruitment","prediction_prob":"1.0808266", "predicted_skill":"1"}, {"text":"corporatestaffing environment","job_title":"Senior Associate, Technology Recruitment","prediction_prob":"0.9035899", "predicted_skill":"1"}, {"text":"workday","job_title":"Senior Associate, Technology Recruitment","prediction_prob":"0.5793607", "predicted_skill":"0"}, {"text":"managerial","job_title":"Program Specialist, Managerial Experience & Leadership Strategy","prediction_prob":"1.078393", "predicted_skill":"1"}, {"text":"business strategy","job_title":"Program Specialist, Managerial Experience & Leadership Strategy","prediction_prob":"1.1265875", "predicted_skill":"1"}, {"text":"stakeholder needs","job_title":"Program Specialist, Managerial Experience & Leadership Strategy","prediction_prob":"0.789783", "predicted_skill":"1"}, {"text":"specialized","job_title":"Program Specialist, Managerial Experience & Leadership Strategy","prediction_prob":"0.47773436", "predicted_skill":"0"}, {"text":"education","job_title":"Program Specialist, Managerial Experience & Leadership Strategy","prediction_prob":"0.9603404", "predicted_skill":"1"}, {"text":"business experience project management","job_title":"Program Specialist, Managerial Experience & Leadership Strategy","prediction_prob":"1.0661898", "predicted_skill":"1"}, {"text":"north american leading talent management","job_title":"Head, Talent Digitization","prediction_prob":"0.5769564", "predicted_skill":"0"}, {"text":"leaders","job_title":"Head, Talent Digitization","prediction_prob":"0.75825083", "predicted_skill":"1"}, {"text":"employees","job_title":"Head, Talent Digitization","prediction_prob":"0.35755968", "predicted_skill":"0"}, {"text":"candidates","job_title":"Head, Talent Digitization","prediction_prob":"0.64224535", "predicted_skill":"0"}, {"text":"","job_title":"Head, Talent Digitization","prediction_prob":"0.9529425", "predicted_skill":"1"}, {"text":"horizontal strategies","job_title":"Head, Talent Digitization","prediction_prob":"0.91009146", "predicted_skill":"1"}, {"text":"cohesive narrative","job_title":"Head, Talent Digitization","prediction_prob":"0.8379471", "predicted_skill":"1"}, {"text":"leading enterprise options","job_title":"Head, Talent Digitization","prediction_prob":"0.8511173", "predicted_skill":"1"}, {"text":"horizontal teams","job_title":"Head, Talent Digitization","prediction_prob":"0.85243064", "predicted_skill":"1"}, {"text":"agile technology","job_title":"Head, Talent Digitization","prediction_prob":"1.109331", "predicted_skill":"1"}, {"text":"talent modules","job_title":"Head, Talent Digitization","prediction_prob":"0.85686314", "predicted_skill":"1"}, {"text":"expert","job_title":"Head, Talent Digitization","prediction_prob":"0.36977777", "predicted_skill":"0"}, {"text":"businessgroup challenges","job_title":"Head, Talent Digitization","prediction_prob":"0.8608242", "predicted_skill":"1"}, {"text":"business strategy","job_title":"Head, Talent Digitization","prediction_prob":"1.1265875", "predicted_skill":"1"}, {"text":"stakeholder needs","job_title":"Head, Talent Digitization","prediction_prob":"0.7897832", "predicted_skill":"1"}, {"text":"subject matter","job_title":"Head, Talent Digitization","prediction_prob":"1.0774221", "predicted_skill":"1"}]'
    data = eval(data_string)
    result_df = pd.DataFrame(data)
    return result_df