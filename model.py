import numpy as np 
import pandas as pd

def data_processing():
    df = pd.read_csv('data/exercise.csv')

    running_rows = df[df['Activity, Exercise or Sport (1 hour)'].str.startswith('Running')].reset_index()

    rr = running_rows.iloc[0:11,:]
    walking_rows = df[df['Activity, Exercise or Sport (1 hour)'].str.startswith('Walking')].reset_index(drop=True)
    wr = walking_rows.iloc[3:11,:]
    indexes = [0,1,2,3,4,6,7]
    wr_fil = wr.iloc[indexes, :]
    wr_f = wr_fil.rename(columns = {'Activity, Exercise or Sport (1 hour)' : 'Activity'})
    rr_f = rr.rename(columns = {'Activity, Exercise or Sport (1 hour)' : 'Activity'})
    co = ['Activity', '130 lb', '155 lb', '180 lb', '205 lb']
    rr = rr_f[co]
    rr['Activity'].replace('Running, 5 mph (12 minute mile)', '8.0', inplace=True)
    rr['Activity'].replace('Running, 5.2 mph (11.5 minute mile)', '8.32', inplace=True)
    rr['Activity'].replace('Running, 6 mph (10 min mile)', '9.6', inplace=True)
    rr['Activity'].replace('Running, 6.7 mph (9 min mile)', '10.72', inplace=True)
    rr['Activity'].replace('Running, 7 mph (8.5 min mile)', '11.2', inplace=True)
    rr['Activity'].replace('Running, 7.5mph (8 min mile)', '12.0', inplace=True)
    rr['Activity'].replace('Running, 8 mph (7.5 min mile)', '12.8', inplace=True)
    rr['Activity'].replace('Running, 8.6 mph (7 min mile)', '13.88', inplace=True)
    rr['Activity'].replace('Running, 9 mph (6.5 min mile)', '14.4', inplace=True)
    rr['Activity'].replace('Running, 10 mph (6 min mile)', '16.0', inplace=True)
    rr['Activity'].replace('Running, 10.9 mph (5.5 min mile)', '17.44', inplace=True)
    cols = ['Activity', '130 lb', '155 lb', '180 lb', '205 lb']
    wr = wr_f[cols]
    wr['Activity'].replace('Walking 2.0 mph, slow', '3.2', inplace=True)
    wr['Activity'].replace('Walking 2.5 mph', '4.0', inplace=True)
    wr['Activity'].replace('Walking 3.0 mph, moderate', '4.8', inplace=True)
    wr['Activity'].replace('Walking 3.5 mph, brisk pace', '5.6', inplace=True)
    wr['Activity'].replace('Walking 4.0 mph, very brisk', '6.4', inplace=True)
    wr['Activity'].replace('Walking 4.5 mph', '7.2', inplace=True)
    wr = wr.rename(columns={"130 lb": 59, "155 lb": 70, "180 lb": 82, "205 lb" : 93})
    rr = rr.rename(columns={"130 lb": 59, "155 lb": 70, "180 lb": 82, "205 lb" : 93})
    wr = wr.iloc[1::, :]
    dr = pd.concat([wr, rr])
    dr = dr.reset_index()
    dr.columns = dr.columns.astype(str)
    cols = ['Activity', '59', '70', '82', '93']
    dr_f = dr[cols]
    df = pd.DataFrame({
        'Activity': [3.2, 4.0, 4.8, 5.6, 6.4, 7.2, 8.0, 8.32, 9.6, 10.72, 11.2, 12.0, 12.8, 13.88, 14.4, 16.0, 17.44],
        '59': [148, 177, 195, 224, 295, 372, 472, 531, 590, 649, 679, 738, 797, 826, 885, 944, 1062],
        '70': [176, 211, 232, 267, 352, 443, 563, 633, 704, 774, 809, 880, 950, 985, 1056, 1126, 1267],
        '82': [204, 245, 270, 311, 409, 515, 654, 735, 817, 899, 940, 1022, 1103, 1144, 1226, 1308, 1471],
        '93': [233, 279, 307, 354, 465, 586, 745, 838, 931, 1024, 1070, 1163, 1256, 1303, 1396, 1489, 1675]
    })

    df_melted = df.melt(id_vars=['Activity'], var_name='Weight', value_name='Calories')
    df_melted['Weight'] = df_melted['Weight'].astype(int)
    df_melted.head()
    return df_melted
from sklearn.preprocessing import StandardScaler
def scale(df):
    scaler = StandardScaler()
    scaler.fit(df)
    df_scaled = scaler.transform(df)
    return df_scaled, scaler
def test_train_split(df, num, df_pred):
    x_train = df[0:num, :]
    x_test = df[num::, :]
    y_train = df_pred[0:num]
    y_test = df_pred[num::]
    return (x_train, x_test, y_train, y_test)
def cv_test_train_split(df, num, df_pred, num1):
    x_train = df[0:num, :]
    x_cv = df[num:num+num1, :]
    x_test = df[num+num1::, :]
    y_train = df_pred[0:num]
    y_cv = df_pred[num:num+num1]
    y_test = df_pred[num+num1::]
    return (x_train, x_cv, x_test, y_train, y_cv, y_test)
from sklearn.linear_model import LinearRegression
def linear_model(x_train, y_train, x_test, y_test):
    reg = LinearRegression().fit(x_train, y_train)
    reg_train = reg.score(x_train, y_train)
    reg_test = reg.score(x_test, y_test)
    model_coef = reg.coef_
    model_intercept = reg.intercept_
    return (reg_train, reg_test, model_coef, model_intercept, reg)
from sklearn.preprocessing import PolynomialFeatures
def poly_model(x_train, y_train, x_test, y_test, degree=2):
    poly = PolynomialFeatures(degree)
    x_poly_train = poly.fit_transform(x_train)
    x_poly_test = poly.fit_transform(x_test)
    reg = LinearRegression().fit(x_poly_train, y_train)
    model_coef = reg.coef_
    model_intercept = reg.intercept_
    reg_train = reg.score(x_poly_train, y_train)
    reg_test = reg.score(x_poly_test, y_test)
    return (reg_train, reg_test, model_coef, model_intercept, reg)
from sklearn.linear_model import LinearRegression
def linear_model1(X_train, y_train):
    reg = LinearRegression().fit(X_train, y_train)
    reg_train = reg.score(X_train, y_train)
    model_coef = reg.coef_
    model_intercept = reg.intercept_
    return (reg_train, model_coef, model_intercept, reg)
def view_result_regression():
    cols = ['Weight', 'Calories']
    df_melted = data_processing()
    df_t = df_melted[cols]
    df_p = df_melted['Activity']
    df_s, scaler = scale(df_t)
    X_train = df_s
    y_train = df_p
    reg_train, model_coef, model_intercept, reg = linear_model1(X_train, y_train)
    print(f"Regression score is {reg_train}")
    print(f"Model Coefficients are {reg.coef_}")
    print(f"Model intercept is {reg.intercept_}")
    return reg, scaler
def predict(val, reg, scaler):
    val = np.reshape(val, (1, 2))
    val = scaler.transform(val)
    return reg.predict(val)

if __name__ == "__main__":
    view_result_regression()
