import numpy as np
from sklearn.linear_model import LinearRegression

def get_linear_regression(x_array, y_array):
    x = np.array(x_array).reshape(-1, 1)
    y = np.array(y_array)
    model = LinearRegression().fit(x, y)
    return model

def calculate_estimated(linear_regression_model):
    model = linear_regression_model
    coef = model.coef_[0]
    intercept = model.intercept_
    estimated = (coef*6) + intercept
    estimated = estimated if estimated <= 360 else 360
    return estimated