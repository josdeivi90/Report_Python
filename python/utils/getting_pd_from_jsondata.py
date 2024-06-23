def get_pd_from_json_data(data):
    pd_data = {}
    for data_month in data:
        performance_data = data_month['pd_data']
        for team in performance_data:
            team_name = team['team']['name']
            mtta = team['data']['MTTA']
            mttr = team['data']['MTTR']
            if team_name not in pd_data:
                pd_data[team_name] = {
                    'MTTA': [],
                    'MTTR': []
                }
            mtta = mtta if mtta else 0
            mttr = mttr if mttr else 0

            pd_data[team_name]['MTTA'].append(mtta)
            pd_data[team_name]['MTTR'].append(mttr)
    return pd_data