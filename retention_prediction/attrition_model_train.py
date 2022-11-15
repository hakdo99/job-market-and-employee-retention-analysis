import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split, GridSearchCV
#from sklearn.preprocessing import StandardScaler
from sklearn.metrics import confusion_matrix, accuracy_score, classification_report, roc_auc_score, log_loss
from sklearn.preprocessing import LabelEncoder
from sklearn.linear_model import LogisticRegression
import joblib
from get_dummies import GetDummies

df = pd.read_csv("C:/Users/dokha/school-projects/job-market-and-employee-engagement-dashboard/retention_prediction/IBM-HR.csv")
df.drop(['EmployeeCount', 'EmployeeNumber', 'Over18', 'StandardHours'], axis="columns", inplace=True)
label = LabelEncoder()
df["Attrition"] = label.fit_transform(df.Attrition)
dummy_col = [column for column in df.drop('Attrition', axis=1).columns if str(df[column].dtypes) == 'object']
dummies = GetDummies(dummy_col)
data = dummies.fit_transform(df)



#dummy_col = [column for column in df.drop('Attrition', axis=1).columns if str(df[column].dtypes) == 'object']
# data = pd.get_dummies(df, columns=dummy_col, dtype='uint8')
#print(data.columns)
X = dummies.fit_transform(df.drop('Attrition', axis=1))
joblib_dummies_file = "C:/Users/dokha/school-projects/job-market-and-employee-engagement-dashboard/retention_prediction/dummies.pkl"  
joblib.dump(dummies, joblib_dummies_file)
y = df.Attrition
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42,
                                                    stratify=y)
lr_clf = LogisticRegression(solver='liblinear', penalty='l1')
lr_clf.fit(X_train, y_train)
lr_train_pred = lr_clf.predict_proba(X_train)
lr_train_log_loss = log_loss(y_train, lr_train_pred)
print("Train log loss: " + str(lr_train_log_loss))
train_auc = roc_auc_score(y_train, lr_train_pred[:, 1])
print("Train AUC: " + str(train_auc))
lr_test_pred = lr_clf.predict_proba(X_test)
lr_test_log_loss = log_loss(y_test, lr_test_pred)
print("Test log loss: " + str(lr_test_log_loss))
test_auc = roc_auc_score(y_test, lr_test_pred[:, 1])
print("Test AUC: " + str(test_auc))
#print(X_test.columns)
joblib_file = "C:/Users/dokha/school-projects/job-market-and-employee-engagement-dashboard/retention_prediction/internal_retention_train_model.pkl"  
joblib.dump(lr_clf, joblib_file)

dummies = joblib.load(joblib_dummies_file)
print(dummies)
print(dummies.columns)
internal_retention_model = joblib.load(joblib_file)
employee = {'Age': 30, 'Department' : 'Sales', 'Gender': 'Female', 'MaritalStatus': 'Married',
            'EducationField': 'Marketing', 'Education': 4, 'NumCompaniesWorked': 3, 'TotalWorkingYears': 10,
            'JobLevel': 3, 'JobRole': 'Sales Executive', 'BusinessTravel': 'Travel_Rarely', 'DistanceFromHome': 3,
            'OverTime': 'No', 'MonthlyIncome': 20000, 'MonthlyRate': 20000, 'DailyRate': 600, 'HourlyRate': 70,
            'PercentSalaryHike': 11, 'TrainingTimesLastYear': 3, 'JobInvolvement': 4, 'PerformanceRating': 4,
            'RelationshipSatisfaction': 3, 'EnvironmentSatisfaction': 4, 'WorkLifeBalance': 4, 'YearsInCurrentRole': 2,
            'YearsAtCompany': 3, 'YearsSinceLastPromotion': 2, 'YearsWithCurrManager': 1, 'JobSatisfaction': 4, 'StockOptionLevel': 4}
employee = pd.DataFrame(employee, index = [0])
employee = dummies.transform(employee)
print(employee.columns)
#print(set(dummies.columns))
#print(set(employee.columns))
col_diff = set(dummies.columns).difference(set(employee.columns))
col_diff = list(col_diff)
#print(col_diff)
for col in col_diff:
    employee[col] = 0
#print(employee.columns)
prediction = internal_retention_model.predict_proba(employee)
print(prediction)
leave = prediction[0][1]
print(type(leave))
leave = "{:.2%}".format(leave)
print(leave)   