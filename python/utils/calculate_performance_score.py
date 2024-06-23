from utils.logic_operations.calculate_regression import get_linear_regression, calculate_estimated

x_data = [1, 2, 3, 4, 5]
green = 0 
yellow = 2
red = 5

def calculate_performance_points(estimated, current_month_value, team_score):
    if current_month_value * 1.1 <= estimated or current_month_value + 10 <= estimated:
        return team_score['green']
    elif current_month_value * 2 >= estimated:
        return team_score['red']
    else:
        return team_score['yellow']
    

def get_performance_points(team_data, which_mtt, team_score):
    mttx = team_data[which_mtt]
    mttx_current_month = mttx.pop()
    if which_mtt == 'MTTR':
        mttx_model = get_linear_regression(x_data, mttx)
        mttx_estimated = calculate_estimated(mttx_model)
        mttx_points = calculate_performance_points(mttx_estimated, mttx_current_month, team_score)
    else:
        if mttx_current_month <= 10:
            mttx_points = team_score['green']
        elif mttx_current_month >= 20:
            mttx_points = team_score['red']
        else:
            mttx_points = team_score['yellow']
    return mttx_points
