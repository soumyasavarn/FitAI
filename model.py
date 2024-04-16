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
    activity_map = {
    'Running, 5 mph (12 minute mile)': '8.0',
    'Running, 5.2 mph (11.5 minute mile)': '8.32',
    'Running, 6 mph (10 min mile)': '9.6',
    'Running, 6.7 mph (9 min mile)': '10.72',
    'Running, 7 mph (8.5 min mile)': '11.2',
    'Running, 7.5mph (8 min mile)': '12.0',
    'Running, 8 mph (7.5 min mile)': '12.8',
    'Running, 8.6 mph (7 min mile)': '13.88',
    'Running, 9 mph (6.5 min mile)': '14.4',
    'Running, 10 mph (6 min mile)': '16.0',
    'Running, 10.9 mph (5.5 min mile)': '17.44'
    }

    for original_activity, new_value in activity_map.items():
        rr.loc[rr['Activity'] == original_activity, 'Activity'] = new_value

    cols = ['Activity', '130 lb', '155 lb', '180 lb', '205 lb']
    wr = wr_f[cols]
    activity_map = {
    'Walking 2.0 mph, slow': '3.2',
    'Walking 2.5 mph': '4.0',
    'Walking 3.0 mph, moderate': '4.8',
    'Walking 3.5 mph, brisk pace': '5.6',
    'Walking 4.0 mph, very brisk': '6.4',
    'Walking 4.5 mph': '7.2'
    }

    for original_activity, new_value in activity_map.items():
        wr.loc[wr['Activity'] == original_activity, 'Activity'] = new_value

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
"""def test_train_split(df, num, df_pred):
    x_train = df[0:num, :]
    x_test = df[num::, :]
    y_train = df_pred[0:num]
    y_test = df_pred[num::]
    return (x_train, x_test, y_train, y_test)"""
def test_train_split(df, num, df_pred):
    start_index = (len(df) - num) // 2
    
    if start_index < 0:
        start_index = 0
        num = len(df) 
    
    x_test = df[start_index:start_index + num, :]
    y_test = df_pred[start_index:start_index + num]
    test_indices = np.concatenate((np.arange(start_index), np.arange(start_index + num, len(df))))
    x_train = df[test_indices, :]
    y_train = df_pred[test_indices]
    
    return x_train, x_test, y_train, y_test
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
def poly_model1(X_train, y_train, degree=2):
    poly = PolynomialFeatures(degree)
    X_poly_train = poly.fit_transform(X_train)
    reg = LinearRegression().fit(X_poly_train, y_train)
    reg_train = reg.score(X_poly_train, y_train)
    return (reg_train, reg, poly)
from sklearn.linear_model import LinearRegression
def linear_model1(X_train, y_train):
    reg = LinearRegression().fit(X_train, y_train)
    reg_train = reg.score(X_train, y_train)

    return (reg_train, reg)
def view_result_regression():
    cols = ['Weight', 'Calories']
    df_melted = data_processing()
    df_t = df_melted[cols]
    df_p = df_melted['Activity']
    df_s, scaler = scale(df_t)
    X_train, X_test, y_train, y_test = test_train_split(df_s, 15, df_p)
    reg_train, reg = linear_model1(X_train, y_train)
    reg2_train, reg2, poly2 = poly_model1(X_train, y_train, 2)
    reg3_train, reg3, poly3 = poly_model1(X_train, y_train, 3)
    X_poly_test2 = poly2.fit_transform(X_test)
    X_poly_test3 = poly3.fit_transform(X_test)
    print(f"Training set linear regression score (for degree 1)is {reg_train}")
    print(f"Test set linear regression score (for degree 1)is {reg.score(X_test, y_test)}")
    print(f"Model Coefficients for degree 1 are {reg.coef_}")
    print(f"Model intercept for degree 1 is {reg.intercept_}")
    print(f"Training set polynomial regression score (for degree 2)is {reg2_train}")
    print(f"Test set polynomial regression score (for degree 2)is {reg2.score(X_poly_test2, y_test)}")
    print(f"Model Coefficients for degree 2 are {reg2.coef_}")
    print(f"Model intercept for degree 2 is {reg2.intercept_}")
    print(f"Training set polynomial regression score (for degree 3)is {reg3_train}")
    print(f"Test set polynomial regression score (for degree 3)is {reg3.score(X_poly_test3, y_test)}")
    print(f"Model Coefficients for degree 3 are {reg3.coef_}")
    print(f"Model intercept for degree 3 is {reg3.intercept_}")
    return reg2, scaler, poly2
def predict(val1, reg, scaler, poly):
    val1 = np.reshape(val1, (1, 2))
    val1 = scaler.transform(val1)
    val1 = poly.fit_transform(val1)
    return reg.predict(val1)

if __name__ == "__main__":
    view_result_regression()
