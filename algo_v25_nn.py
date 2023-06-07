import pandas as pd
import numpy as np
import os
import datetime
import math

#date = "2020-06-21"
#race_date = datetime.datetime.strptime(date, '%Y-%m-%d')
#horse_past_race_date = datetime.datetime(race_date.year-1,race_date.month,race_date.day).strftime('%Y-%m-%d')
feet_per_furlong = 660


def log(stuff):
    the_type = type(stuff)
    the_type = str(the_type)
    if(the_type.find('DataFrame') > -1):
        pass
        #display(stuff)
    else:
        pass
        #print(stuff)

def get_trainer_stats(trainer_list, full_data, race_date_str):

    trainer_stats_cols = ['trainer','trainer_race_count','first_place_count','first_place_perc','second_place_count','second_place_perc','third_place_count','third_place_perc',
    'fourth_place_count','fourth_place_perc','top_three_place_count','top_three_place_perc','top_four_place_count','top_four_place_perc']

    race_date = datetime.datetime.strptime(race_date_str, '%Y-%m-%d').date()
    trainer_past_race_date = race_date - datetime.timedelta(days=180)
    trainer_stats = pd.DataFrame(columns=trainer_stats_cols)
    summary_stats = pd.DataFrame()

    count = 0
    total = len(trainer_list)
    for t in trainer_list:
        count+=1
        trainer_name = t
        
        print('{}/{} | {}'.format(count,total, t))
       
        trainer_history_query = 'trainer=="{}" and date < "{}" and date > "{}"'.format(trainer_name,race_date_str,trainer_past_race_date.strftime('%Y-%m-%d'))
        trainer_history = full_data.query(trainer_history_query)

        #display(trainer_history)

        first = trainer_history.query('pos_fin==1')[['date','trainer','pos_fin']]
        second = trainer_history.query('pos_fin==2')[['date','trainer','pos_fin']]
        third = trainer_history.query('pos_fin==3')[['date','trainer','pos_fin']]
        fourth = trainer_history.query('pos_fin==4')[['date','trainer','pos_fin']]
        top_three = trainer_history.query('pos_fin<4')[['date','trainer','pos_fin']]
        top_four = trainer_history.query('pos_fin<5')[['date','trainer','pos_fin']]

        data = {
            'trainer' : trainer_name,
            'trainer_race_count' : trainer_history.describe().loc['count', 'pos_fin'],
            'first_place_count' :  first.describe().loc['count', 'pos_fin'],
            'first_place_perc' : first.describe().loc['count', 'pos_fin'] / trainer_history.describe().loc['count', 'pos_fin'],
            'second_place_count' : second.describe().loc['count', 'pos_fin'],
            'second_place_perc' : second.describe().loc['count', 'pos_fin'] / trainer_history.describe().loc['count', 'pos_fin'],
            'third_place_count' : third.describe().loc['count', 'pos_fin'],
            'third_place_perc' : third.describe().loc['count', 'pos_fin'] / trainer_history.describe().loc['count', 'pos_fin'],
            'fourth_place_count' : fourth.describe().loc['count', 'pos_fin'],
            'fourth_place_perc' : fourth.describe().loc['count', 'pos_fin'] / trainer_history.describe().loc['count', 'pos_fin'],
            'top_three_place_count' : top_three.describe().loc['count', 'pos_fin'],
            'top_three_place_perc' : top_three.describe().loc['count', 'pos_fin'] / trainer_history.describe().loc['count', 'pos_fin'],
            'top_four_place_count' : top_four.describe().loc['count', 'pos_fin'],
            'top_four_place_perc' : top_four.describe().loc['count', 'pos_fin'] / trainer_history.describe().loc['count', 'pos_fin'],
            'rank' : 0
        }

        trainer_stats = trainer_stats.append(data, ignore_index=True)
        
        sum_up = trainer_history[['pos_fin']].describe()
        sum_up['trainer'] = trainer_name
        summary_stats = summary_stats.append(sum_up)
        #race_subset.at[idx, 'feet_per_second'] = feet_per_second

    trainer_stats = trainer_stats.fillna(0)
    trainer_stats = trainer_stats.query("trainer_race_count > 0")

    trainer_summary = trainer_stats.describe()
    trainer_normalization = pd.DataFrame()

    for i,row in trainer_stats.iterrows():
        normalize = {
            'name' : '',
            'rank' : 0
        }

        # mean_count = trainer_summary.loc['mean','trainer_race_count']
        # mean_top_three = trainer_summary.loc['mean','top_three_place_perc']
        # mean_top_four = trainer_summary.loc['mean','top_four_place_perc']
        # normalize['name'] = row['trainer']

        # if row['trainer_race_count'] > mean_count:
        #     normalize['rank'] = row['top_three_place_perc'] + row['top_four_place_perc']
        # else:
        #     under_average = row['trainer_race_count'] / mean_count
        #     diff_from_mean_three = row['top_three_place_perc'] - mean_top_three
        #     perc_earned_three = diff_from_mean_three * under_average

        #     diff_from_mean_four = row['top_four_place_perc'] - mean_top_four
        #     perc_earned_four = diff_from_mean_four * under_average

        #     normalize['rank'] = (perc_earned_three + mean_top_three) + (perc_earned_four + mean_top_four)

        med_count = trainer_summary.loc['50%','trainer_race_count']
        med_top_three = trainer_summary.loc['50%','top_three_place_perc']
        med_top_four = trainer_summary.loc['50%','top_four_place_perc']

        med_first_place = trainer_summary.loc['50%','first_place_perc']
        normalize['name'] = row['trainer']

        if row['trainer_race_count'] >= med_count:
            normalize['rank'] = row['first_place_perc'] 
        elif row['trainer_race_count'] == 0:
            normalize['rank'] = trainer_summary.loc['25%','first_place_perc']
        else:
            under_average = row['trainer_race_count'] / med_count
            diff_from_mean_first = row['first_place_perc'] - med_first_place
            perc_earned_diff = diff_from_mean_first * under_average

            normalize['rank'] = row['first_place_perc'] - abs(perc_earned_diff)
        trainer_normalization = trainer_normalization.append(normalize, ignore_index=True)
        
    return trainer_normalization.sort_values(by=['rank'], ascending=False), trainer_stats.sort_values(by=['first_place_perc'], ascending=False)

def jockey_query(data, query):
    jockey_history = data.query(query)
    
    first = jockey_history.query('pos_fin==1')[['date','jockey','pos_fin']]
    second = jockey_history.query('pos_fin==2')[['date','jockey','pos_fin']]
    third = jockey_history.query('pos_fin==3')[['date','jockey','pos_fin']]
    fourth = jockey_history.query('pos_fin==4')[['date','jockey','pos_fin']]
    top_three = jockey_history.query('pos_fin<4')[['date','jockey','pos_fin']]
    top_four = jockey_history.query('pos_fin<5')[['date','jockey','pos_fin']]

    data = {
        'jockey' : '',
        'jockey_race_count' : jockey_history.describe().loc['count', 'pos_fin'],
        'first_place_count' :  first.describe().loc['count', 'pos_fin'],
        'first_place_perc' : first.describe().loc['count', 'pos_fin'] / jockey_history.describe().loc['count', 'pos_fin'],
        'second_place_count' : second.describe().loc['count', 'pos_fin'],
        'second_place_perc' : second.describe().loc['count', 'pos_fin'] / jockey_history.describe().loc['count', 'pos_fin'],
        'third_place_count' : third.describe().loc['count', 'pos_fin'],
        'third_place_perc' : third.describe().loc['count', 'pos_fin'] / jockey_history.describe().loc['count', 'pos_fin'],
        'fourth_place_count' : fourth.describe().loc['count', 'pos_fin'],
        'fourth_place_perc' : fourth.describe().loc['count', 'pos_fin'] / jockey_history.describe().loc['count', 'pos_fin'],
        'top_three_place_count' : top_three.describe().loc['count', 'pos_fin'],
        'top_three_place_perc' : top_three.describe().loc['count', 'pos_fin'] / jockey_history.describe().loc['count', 'pos_fin'],
        'top_four_place_count' : top_four.describe().loc['count', 'pos_fin'],
        'top_four_place_perc' : top_four.describe().loc['count', 'pos_fin'] / jockey_history.describe().loc['count', 'pos_fin']
    }

    return data


def get_jockey_stats(jockey_list, full_data, race_date_str):
    jockey_stats_cols = ['jockey','jockey_race_count','first_place_count','first_place_perc','second_place_count','second_place_perc','third_place_count','third_place_perc',
    'fourth_place_count','fourth_place_perc','top_three_place_count','top_three_place_perc','top_four_place_count','top_four_place_perc']

    race_date = datetime.datetime.strptime(race_date_str, '%Y-%m-%d').date()
    jockey_past_race_date = race_date - datetime.timedelta(days=100)#datetime.datetime(race_date.year,race_date.month,race_date.day).strftime('%Y-%m-%d')

    jockey_stats = pd.DataFrame(columns=jockey_stats_cols)
    count = 0
    total = len(jockey_list)
    for jockey in jockey_list:
        count += 1
        print('{}/{} | {}'.format(count,total, jockey))
        jockey_history_query = 'jockey=="{}" and date < "{}" and date > "{}"'.format(jockey,race_date, jockey_past_race_date.strftime('%Y-%m-%d'))
        df_data = jockey_query(full_data,jockey_history_query)
        df_data['jockey'] = jockey
        jockey_stats = jockey_stats.append(df_data, ignore_index=True)

    jockey_stats = jockey_stats.fillna(0)
    jockey_stats = jockey_stats.query("jockey_race_count > 0")

    jockey_summary = jockey_stats.describe()
    jockey_normalization = pd.DataFrame()

    #display(jockey_stats)
    #display(jockey_summary)
    for i,row in jockey_stats.iterrows():
        normalize = {
            'name' : '',
            'rank' : 0
        }

        # mean_count = jockey_summary.loc['mean','jockey_race_count']
        # mean_top_three = jockey_summary.loc['mean','top_three_place_perc']
        # mean_top_four = jockey_summary.loc['mean','top_four_place_perc']
        med_count = jockey_summary.loc['50%','jockey_race_count']
        med_top_three = jockey_summary.loc['50%','top_three_place_perc']
        med_top_four = jockey_summary.loc['50%','top_four_place_perc']

        med_first_place = jockey_summary.loc['50%','first_place_perc']
        normalize['name'] = row['jockey']

        # if row['jockey_race_count'] > mean_count:
        #     normalize['rank'] = row['top_three_place_perc'] + row['top_four_place_perc']
        # else:
        #     under_average = row['jockey_race_count'] / mean_count
        #     diff_from_mean_three = row['top_three_place_perc'] - mean_top_three
        #     perc_earned_three = diff_from_mean_three * under_average

        #     diff_from_mean_four = row['top_four_place_perc'] - mean_top_four
        #     perc_earned_four = diff_from_mean_four * under_average

        #     normalize['rank'] = (perc_earned_three + mean_top_three) + (perc_earned_four + mean_top_four)


        if row['jockey_race_count'] >= med_count:
            normalize['rank'] = row['first_place_perc'] 
        elif row['jockey_race_count'] == 0:
            normalize['rank'] = jockey_summary.loc['25%','first_place_perc']
        else:
            under_average = row['jockey_race_count'] / med_count
            diff_from_mean_first = row['first_place_perc'] - med_first_place
            perc_earned_diff = diff_from_mean_first * under_average

            normalize['rank'] = row['first_place_perc'] - abs(perc_earned_diff)

        jockey_normalization = jockey_normalization.append(normalize, ignore_index=True)
    
    return jockey_normalization.sort_values(by=['rank'], ascending=False), jockey_stats.sort_values(by=['first_place_perc'], ascending=False)


def get_owner_stats(owner_list, full_data, race_date_str):
    owner_stats_cols = ['owner','owner_race_count','first_place_count','first_place_perc','second_place_count','second_place_perc','third_place_count','third_place_perc',
    'fourth_place_count','fourth_place_perc','top_three_place_count','top_three_place_perc','top_four_place_count','top_four_place_perc']

    race_date = datetime.datetime.strptime(race_date_str, '%Y-%m-%d').date()
    owner_past_race_date = race_date - datetime.timedelta(days=365)
    owner_stats = pd.DataFrame(columns=owner_stats_cols)
    summary_stats = pd.DataFrame()

    count = 0
    total = len(owner_list)
    for o in owner_list:
        count+=1
        print('{}/{} | {}'.format(count,total, o))
        owner_name = o
        if '"' in owner_name:
            owner_name.replace('"', '\"')
        
        try:
            owner_history_query = "owner=='{}' and date < '{}' and date > '{}'".format(owner_name,race_date_str,owner_past_race_date.strftime('%Y-%m-%d'))
            owner_history = full_data.query(owner_history_query)
        except:
            print('{} count not be parsed'.format(o))
            continue
        
        first = owner_history.query('pos_fin==1')[['date','owner','pos_fin']]
        second = owner_history.query('pos_fin==2')[['date','owner','pos_fin']]
        third = owner_history.query('pos_fin==3')[['date','owner','pos_fin']]
        fourth = owner_history.query('pos_fin==4')[['date','owner','pos_fin']]
        top_three = owner_history.query('pos_fin<4')[['date','owner','pos_fin']]
        top_four = owner_history.query('pos_fin<5')[['date','owner','pos_fin']]

        data = {
            'owner' : owner_name,
            'owner_race_count' : owner_history.describe().loc['count', 'pos_fin'],
            'first_place_count' :  first.describe().loc['count', 'pos_fin'],
            'first_place_perc' : first.describe().loc['count', 'pos_fin'] / owner_history.describe().loc['count', 'pos_fin'],
            'second_place_count' : second.describe().loc['count', 'pos_fin'],
            'second_place_perc' : second.describe().loc['count', 'pos_fin'] / owner_history.describe().loc['count', 'pos_fin'],
            'third_place_count' : third.describe().loc['count', 'pos_fin'],
            'third_place_perc' : third.describe().loc['count', 'pos_fin'] / owner_history.describe().loc['count', 'pos_fin'],
            'fourth_place_count' : fourth.describe().loc['count', 'pos_fin'],
            'fourth_place_perc' : fourth.describe().loc['count', 'pos_fin'] / owner_history.describe().loc['count', 'pos_fin'],
            'top_three_place_count' : top_three.describe().loc['count', 'pos_fin'],
            'top_three_place_perc' : top_three.describe().loc['count', 'pos_fin'] / owner_history.describe().loc['count', 'pos_fin'],
            'top_four_place_count' : top_four.describe().loc['count', 'pos_fin'],
            'top_four_place_perc' : top_four.describe().loc['count', 'pos_fin'] / owner_history.describe().loc['count', 'pos_fin'],
            'rank' : 0
        }

        owner_stats = owner_stats.append(data, ignore_index=True)
        sum_up = owner_history[['pos_fin']].describe()
        sum_up['owner'] = owner_name
        summary_stats = summary_stats.append(sum_up)
        #race_subset.at[idx, 'feet_per_second'] = feet_per_second

    owner_stats = owner_stats.fillna(0)
    owner_stats = owner_stats.query("owner_race_count > 0")
    owner_summary = owner_stats.describe()
    owner_normalization = pd.DataFrame()

    #display(trainer_stats)
    #display(owner_summary)
    for i,row in owner_stats.iterrows():
        normalize = {
            'name' : '',
            'rank' : 0
        }

        med_count = owner_summary.loc['50%','owner_race_count']
        med_top_three = owner_summary.loc['50%','top_three_place_perc']
        med_top_four = owner_summary.loc['50%','top_four_place_perc']

        med_first_place = owner_summary.loc['50%','first_place_perc']
        normalize['name'] = row['owner']

        # if row['owner_race_count'] > mean_count:
        #     normalize['rank'] = row['top_three_place_perc'] + row['top_four_place_perc']
        # elif row['owner_race_count'] == 0:
        #     normalize['rank'] = mean_top_three + mean_top_four
        # else:
        #     under_average = row['owner_race_count'] / mean_count
        #     diff_from_mean_three = row['top_three_place_perc'] - mean_top_three
        #     perc_earned_three = diff_from_mean_three * under_average

        #     diff_from_mean_four = row['top_four_place_perc'] - mean_top_four
        #     perc_earned_four = diff_from_mean_four * under_average

        #     normalize['rank'] = (perc_earned_three + mean_top_three) + (perc_earned_four + mean_top_four)

        if row['owner_race_count'] >= med_count:
            normalize['rank'] = row['first_place_perc'] 
        elif row['owner_race_count'] == 0:
            normalize['rank'] = owner_summary.loc['25%','first_place_perc']
        else:
            under_average = row['owner_race_count'] / med_count
            diff_from_mean_first = row['first_place_perc'] - med_first_place
            perc_earned_diff = diff_from_mean_first * under_average

            normalize['rank'] = row['first_place_perc'] - abs(perc_earned_diff)
        owner_normalization = owner_normalization.append(normalize, ignore_index=True)
        
    return owner_normalization.sort_values(by=['rank'], ascending=False), owner_stats.sort_values(by=['first_place_perc'], ascending=False)

def get_track_par(df,track,race_date,race_type,surface,distance):
    df = df.query("date<'{}'".format(race_date))
    query = "track=='{}' and type=='{}' and surface=='{}' and distance_float=={} and position==1.0".format(track,race_type,surface,distance)

    #print(query)
    track_history = df.query(query)
    #print('Track History')
    #display(track_history.sort_values(by=['date']))
            

    track_history = track_history.dropna(axis='columns',how='all')
    #print('DF SIZE: {}'.format(len(track_history.index)))

    if track_history.empty == True or len(track_history.index) < 5:
        #print('Small data size: {}'.format(len(track_history.index)))
        query = "type=='{}' and surface=='{}' and distance_float=={} and position==1.0".format(race_type,surface,distance)
        track_history = df.query(query)
        track_history = track_history.describe()
    else:
        track_history = track_history.describe()
    #display(track_history)
    return track_history

def setup_track_par(df, entry,  isEmpty=False):
    horse_name = entry['name']
    race_type = entry['type']
    #race_type_level = entry['claim_price']
    surface = entry['surface']
    distance = entry['distance_float']
    prev_track = entry['track']
    race_date = entry['date']
    
    # curr_race_type = the_race.iloc[0]['type']
    # #race_type_level = entry['claim_price']
    # curr_surface = the_race.iloc[0]['surface']
    # curr_distance = the_race.iloc[0]['distance_float']
    # curr_race_date = the_race.iloc[0]['date']
    # curr_track = the_race.iloc[0]['track']

    axis = '50%'
    if isEmpty is True:
        axis = '25%'

    prev_track_stats = get_track_par(df,prev_track,race_date,race_type,surface,distance)
    #prev_track_diff = prev_track_stats.loc['50%', 'ind_fin'] / entry['ind_fin']

    #curr_track_stats = get_track_par(df,curr_track,curr_race_date,curr_race_type,curr_surface,curr_distance)
    #curr_track_diff = prev_track_stats.loc['50%', 'ind_fin'] / entry['ind_fin']

    # if prev_track_stats.empty:
    #     prev_track_stats = curr_track_stats

    #display(prev_track_stats)
    #display(curr_track_stats)


    row_to_add = {
        'horse_name' : horse_name,
        'date' : race_date,
        'prev_track' : prev_track,
        'horse_time' : entry['ind_fin'],
        'track_par_med' : prev_track_stats.loc[axis, 'ind_fin'],
        'adj_diff' : prev_track_stats.loc['50%', 'ind_fin'] - prev_track_stats.loc['mean', 'ind_fin'],
        'difference_med' : prev_track_stats.loc['50%', 'ind_fin'] / entry['ind_fin'],
        #'curr_track' : curr_track,
        #'curr_track_par' : curr_track_stats.loc['50%', 'ind_fin'],
        #'track_par_diff' : curr_track_diff,       
        'distance' : distance,
    }

    return row_to_add
    

def speed_figure(horse_list,df, str_end_date):

    #get unique tracks that horses participated in
    #prev_raced_tracks = the_race['track_last_raced'].unique().tolist()
    date = str_end_date
    #distance = the_race.iloc[0]['distance_float']

    total_stack_up = pd.DataFrame()
    horse_summary = pd.DataFrame()

    count = 0
    total = len(horse_list)
    for horse in horse_list:
        count+=1
        print('{}/{} | {}'.format(count,total, horse))
        trend = 0
        predicted_value = 0
        stack_up = pd.DataFrame()
        #get race history
        horse_name = horse
        #print(horse_name)
        horse_history_query = 'name=="{}" and date < "{}"'.format(horse_name,date)   
        horse_history = df.query(horse_history_query)
        horse_history = horse_history.sort_values(by=['date'])
        #display(horse_history)
        #prev_raced_tracks = horse_history['track_last_raced'].unique().tolist()
        breeds_raced = horse_history['breed'].unique().tolist()

        if horse_history.empty or len(horse_history.index) == 0:
            summary_data = {
                'horse_name' : horse_name,
                'speed_to_par' : 0,
                'trend' : trend,
                'predicted_to_par' : predicted_value
            }
            horse_summary = horse_summary.append(summary_data, ignore_index=True)
            continue
            #print('{} has no history'.format(horse_name))
            # row_to_add = setup_track_par(df,entry, isEmpty=True)
            # stack_up = stack_up.append(row_to_add, ignore_index=True)
            # total_stack_up = total_stack_up.append(row_to_add, ignore_index=True)
            # predicted_value = stack_up.describe().loc['50%', 'difference_med'] 
        
        else:
            race_times = []
            for rdx, race in horse_history.iterrows():
                #if race['distance_float'] >= (distance-1.5) and race['distance_float'] <= (distance+1.5):
                try:
                    if True:
                        row_to_add = setup_track_par(df,race)
                        stack_up = stack_up.append(row_to_add, ignore_index=True)
                        total_stack_up = total_stack_up.append(row_to_add, ignore_index=True)
                except:
                    continue

            #stack_up = stack_up.sort_values(by=['date'])
            #try:
            if stack_up.empty or len(stack_up.index) == 0:
                summary_data = {
                    'horse_name' : horse_name,
                    'speed_to_par' : 0,
                    'trend' : trend,
                    'predicted_to_par' : predicted_value
                }
                horse_summary = horse_summary.append(summary_data, ignore_index=True)
                continue

            
            stack_up = stack_up.fillna(0)
            par_trend = stack_up['difference_med'].to_list()
            
            std_dev_val = stack_up.describe().loc['std','difference_med']
            med_val = stack_up.describe().loc['50%','difference_med']
            normalized_val = []
            #remove outliers
            #print(std_dev_val)
            #print(med_val)
            #for x in range(0,len(par_trend)-1):
            for x in par_trend:
                val = x#par_trend[x]
                limit_up = med_val + std_dev_val
                limit_down = med_val - std_dev_val
                #print('{} > {} or {} < {}'.format(val,limit_up,val,limit_down))
                if val > limit_up or val < limit_down:
                    #print('popping {}'.format(val))
                    continue
                    #par_trend.pop(x)
                else:
                    #print('adding {}'.format(val))                      
                    normalized_val.append(val)
            # except Exception as e:
            #     print(e)
            #     print(normalized_val)
            #     print('par trend may be empty: {}'.format(par_trend))


            
            #print(par_trend)
            if len(normalized_val) > 0:
                for val in range(0,len(normalized_val)-2):
                    current = normalized_val[val]
                    next_itr = normalized_val[val+1]
                    trend = trend + (current - next_itr)

                horse_stats = stack_up.describe()
                #display(horse_stats)
                predicted_value = normalized_val[-1] - trend
                axis_val = 'mean'

                #if trend < 0 use 50% and 75%
                #if trend > 0 use mean and 25%
                if trend > 0 and trend <= std_dev_val :
                    axis_val = 'mean'
                    last_time = normalized_val[-1]
                    min_time = horse_stats.loc['min','difference_med']
                    mean_time = horse_stats.loc[axis_val,'difference_med']
                    lower_qtr_time = horse_stats.loc['25%', 'difference_med']
                    
                    if last_time < mean_time:
                        axis_val = '25%'
                    if last_time < lower_qtr_time:
                        axis_val = 'min'

                
                elif trend > (std_dev_val*1) and trend <= (std_dev_val*2):
                    axis_val = '25%'
                elif trend > (std_dev_val*2):
                    axis_val = 'min'

                elif trend < 0 and trend >= (std_dev_val*-1):
                    axis_val = '50%'
                elif trend < (std_dev_val*-1) and trend >= (std_dev_val*-1):
                    axis_val = '75%'
                    last_time = normalized_val[-1]
                    min_time = horse_stats.loc['min','difference_med']
                    lower_qtr_time = horse_stats.loc[axis_val,'difference_med']
                    
                    if last_time < lower_qtr_time:
                        axis_val = 'max'
                elif trend < (std_dev_val*-2):
                    axis_val = 'max'

                predicted_value = horse_stats.loc[axis_val, 'difference_med']
            else:
                trend = 0
                predicted_value = stack_up.describe().loc['50%', 'difference_med']

        summary_data = {
            'horse_name' : horse_name,
            'speed_to_par' : stack_up.describe().loc['50%', 'difference_med'] ,
            'trend' : trend,
            'predicted_to_par' : predicted_value
        }
        #display(stack_up)
        horse_summary = horse_summary.append(summary_data, ignore_index=True)
            

    column_order = ['date', 'horse_name', 'horse_time', 'distance','prev_track', 'track_par_med', 'adj_diff','difference_med','curr_track', 'curr_track_par']
    total_stack_up = total_stack_up.reindex(columns=column_order)
    #display(total_stack_up)
    

    return horse_summary.sort_values(by=['speed_to_par'], ascending=False)

def get_post_winning_perc(the_race, df):
    
    post_winning_perc = pd.DataFrame()
    df_subset = df.query('track=="{}" and distance_float=={} and date < "{}" and pos_fin==1'.format(the_race.iloc[0]['track'],the_race.iloc[0]['distance_float'], the_race.iloc[0]['date']))
    #unique_races = post_query.drop_duplicates(['date', 'track', 'race_number'])
    race_count = len(df_subset.index)
    log(race_count)

    for p, racer in the_race.iterrows():
        post_data = {
            'horse_name' : '',
            'post_perc' : 0
        }
        post_query = df_subset.query('pp=={}'.format(racer['pp']))
        post_winners = len(post_query.index)
        log(post_winners)
        
        post_data['horse_name'] = racer['name']
        post_data['post_perc'] = post_winners / race_count
        post_winning_perc = post_winning_perc.append(post_data, ignore_index=True)
    return post_winning_perc.sort_values(by=['post_perc'], ascending=False)

def lowest_odds_calc(the_race, winning_perc):
    the_race = the_race.sort_values(by=['odds'], ascending=True)
    lowest_odds = the_race.iloc[0]['odds']

    odds_calc = pd.DataFrame()
    for o, row in the_race.iterrows():
        data = {
            'horse_name': '',
            'odds' : 0
        }

        data['horse_name'] = row['name']
        data['odds'] = (lowest_odds / row['odds']) * winning_perc
        odds_calc = odds_calc.append(data, ignore_index=True)

    return odds_calc.sort_values(by=['odds'], ascending=False)

def horse_favorite_winning_percentage(df):
    
    fav_perc = df.query('pos_fin==1 and favorite==1')
    unique_races = df.drop_duplicates(['date', 'track', 'race_number'])
  
    race_count = len(unique_races.index)
    favorite_win_count = len(fav_perc.index)

    favorite_win_perc = favorite_win_count / race_count
    
    log(race_count)
    log(favorite_win_count)
    log(favorite_win_perc)

    return favorite_win_perc

def optimize(race_rank, tracker, tri_list, sup_list, race_info, pick_em, strict, less_strict, loose, looser):
    monitor = 0
    test_limit = 2000
    curr_itr = 0
    file_path = '../data_files\\wager_sheet.csv'
    wager = pd.read_csv(file_path, index_col='date_track_race')
    wager = wager.fillna(0)

    start = 0
    end = 100
    step = 10
    for horse in range(start,end,step):
        for jockey in range(start,end,step):
            monitor = horse+jockey
            if monitor > 100:
                break
            for trainer in range(start,end,step):
                monitor = horse+jockey+trainer
                if monitor > 100:
                    break
                for post in range(start,end,step):
                    monitor = horse+jockey+trainer+post
                    if monitor > 100:
                        break
                    for odd in range(start,end,step):
                        monitor = horse+jockey+trainer+post+odd
                        if monitor > 100:
                            break
                        for owner in range(start,end,step):
                            monitor = horse+jockey+trainer+owner+post+odd
                            if monitor > 104:
                                break
                            if monitor < 100:
                                continue
                            if monitor >= 100 and monitor <= 104:
                                curr_itr += 1
                                race_number = eval(race_info.split('_')[-1])
                                key = 'h:{} | j:{} | t:{} | o:{} | p:{} | odd:{}'.format(horse,jockey,trainer,owner,post,odd)
                                #print(key)
                                if key not in tracker.index.values:
                                    tracker = tracker.append(pd.DataFrame({'calc':key,'horse_order': '','total_races':0,'win': 0,'place': 0, 'show':0, 'exacta_12': 0, 'exacta_13':0,'trifectas':0,'superfectas':0, 'tri_cost':0, 'tri_winnings' : 0, 'sup_cost':0,'sup_winnings':0, 'race_total_cost':0, 'race_total_winnings':0, 'tri_races':'', 'sup_races':'', 'pick_3': 0, 'pick_3_win' : 0, 'pick_3_cost_lr':0, 'pick_3_type': '', 'pick_4': 0, 'pick_4_win' : 0, 'pick_4_cost_lr':0, 'pick_4_type': '','total_cost':0, 'total_winnings':0, 'win_after_cost': 0}, index=[key]))
                                if key not in strict.keys():
                                    strict[key] = []
                                    less_strict[key] = []
                                    loose[key] = []
                                    looser[key] = []
                                for ni, row in race_rank.iterrows():
                                    race_rank.at[ni,'optimize_val'] = ( (row['horse_rank'] * (horse/100)) + (row['jockey_rank'] * (jockey/100)) + (row['trainer_rank'] * (trainer/100)) + (row['owner_rank'] * (owner/100)) + (row['post_win'] * (post/100)) + (row['odds'] * (odd/100)) )
                                
                                race_rank = race_rank.sort_values(by=['optimize_val'],ascending=False)
                                strict[key].append(race_rank.iloc[0]['horse_name'])
                                less_strict[key] = less_strict[key] + race_rank.iloc[0:2]['horse_name'].tolist()
                                loose[key] = loose[key] + race_rank.iloc[0:3]['horse_name'].tolist()
                                looser[key] = looser[key] + race_rank.iloc[0:4]['horse_name'].tolist()

                                temp_place = 1
                                for h,hrow in race_rank.iterrows():
                                    tracker.at[key,'horse_order']+= 'Race: {}\n{}. {};'.format(race_number,temp_place,hrow['horse_name'])
                                    temp_place+=1

                                tracker.at[key,'horse_order']+= '\n'
                                #print(tracker.at[key,'horse_order'])
                                winner = race_rank.iloc[0]['horse_name']
                                actual_winner = tri_list[0]

                                if winner == actual_winner:
                                    #print('{} - {} is the winner'.format(key, winner))
                                    tracker.at[key,'win'] += 1

                                rank_place = race_rank.iloc[1]['horse_name']
                                rank_show = race_rank.iloc[2]['horse_name']
                                actual_place = tri_list[1]
                                actual_show = tri_list[2]

                                if winner == actual_winner and rank_place == actual_place:
                                    tracker.at[key,'place'] += 1
                                    tracker.at[key,'exacta_12'] += 1
                                    #print('{} - exacta_12'.format(key))
                                if winner == actual_winner and rank_place == actual_show:
                                    tracker.at[key,'exacta_13'] += 1
                                    #print('{} - exacta_13'.format(key))

                                if rank_show == actual_show:
                                    tracker.at[key,'show'] += 1                       

                                top_three = race_rank.iloc[0:3]['horse_name'].tolist()
                                top_four = race_rank.iloc[0:4]['horse_name'].tolist()

                                tri_count = 0
                                for n in top_three:
                                    if n in tri_list:
                                        tri_count +=1

                                sup_count = 0
                                for n in top_four:
                                    if n in sup_list:
                                        sup_count +=1

                                pick_three = wager.loc[race_info,'pick_3']
                                pick_four = wager.loc[race_info,'pick_4']

                                win4_strict = 0
                                win4_ls = 0
                                win4_loose = 0
                                win4_looser = 0
                                if pick_four > 0:
                                    tracker.at[key,'pick_4_cost_lr'] += (4*4*4*4)*wager.loc[race_info,'pick_4_unit']
                                    
                                    pick_four_actual = []
                                    pick_four_actual.append(pick_em[race_number-3])
                                    pick_four_actual.append(pick_em[race_number-2])
                                    pick_four_actual.append(pick_em[race_number-1])
                                    pick_four_actual.append(pick_em[race_number])
                                    
                                    
                                    for race_horse in pick_four_actual:
                                        if race_horse in strict[key]:
                                            win4_strict +=1
                                        if race_horse in less_strict[key]:
                                            win4_ls += 1
                                        if race_horse in loose[key]:
                                            win4_loose += 1
                                        if race_horse in looser[key]:
                                            win4_looser += 1

                                    if win4_strict == 4:
                                        tracker.at[key,'pick_4_type'] += 's,'
                                    if win4_ls == 4:
                                        tracker.at[key,'pick_4_type'] += 'ls,'
                                    if win4_loose == 4:
                                        tracker.at[key,'pick_4_type'] += 'l,'
                                    if win4_looser == 4:
                                        tracker.at[key,'pick_4_type'] += 'lr,'

                                    if win4_strict == 4 or win4_ls == 4 or win4_loose == 4 or win4_looser == 4:
                                        # print('Pick 4')
                                        # print(pick_four_actual)
                                        # print(looser[key])
                                        tracker.at[key,'pick_4'] += 1
                                        tracker.at[key,'pick_4_win'] += pick_four
                                        tracker.at[key,'total_winnings'] += pick_four
                                        

                                win3_strict = 0
                                win3_ls = 0
                                win3_loose = 0
                                win3_looser = 0
                                if pick_three > 0:
                                    tracker.at[key,'pick_3_cost_lr'] += (4*4*4)*wager.loc[race_info,'pick_3_unit']
                                    pick_three_actual = []
                                    pick_three_actual.append(pick_em[race_number-2])
                                    pick_three_actual.append(pick_em[race_number-1])
                                    pick_three_actual.append(pick_em[race_number])
                                    
                                    for race_horse in pick_three_actual:
                                        if race_horse in strict[key]:
                                            win3_strict +=1
                                        if race_horse in less_strict[key]:
                                            win3_ls += 1
                                        if race_horse in loose[key]:
                                            win3_loose += 1
                                        if race_horse in looser[key]:
                                            win3_looser += 1

                                    if win3_strict == 3:
                                        tracker.at[key,'pick_3_type'] += 's,'
                                    if win3_ls == 3:
                                        tracker.at[key,'pick_3_type'] += 'ls,'
                                    if win3_loose == 3:
                                        tracker.at[key,'pick_3_type'] += 'l,'
                                    if win3_looser == 3:
                                        tracker.at[key,'pick_3_type'] += 'lr,'

                                    if win3_strict == 3 or win3_ls == 3 or win3_loose == 3 or win3_looser == 3:
                                        # print('Pick 3')
                                        # print(pick_three_actual)
                                        # print(looser[key])
                                        tracker.at[key,'pick_3'] += 1
                                        tracker.at[key,'pick_3_win'] += pick_three
                                        tracker.at[key,'total_winnings'] += pick_three
                                        

                                tri_cost = (wager.loc[race_info,'tri_unit']*6)
                                sup_cost = (wager.loc[race_info,'super_unit']*24)
                                
                                tracker.at[key,'tri_cost'] += tri_cost
                                tracker.at[key,'sup_cost'] += sup_cost
                                tracker.at[key,'race_total_cost'] += (sup_cost+tri_cost)
                                tracker.at[key,'total_races'] += 1 #tracker.at[key,'total_races']+1
                                tracker.at[key,'total_cost'] = tracker.at[key,'tri_cost'] + tracker.at[key,'sup_cost'] + tracker.at[key,'pick_3_cost_lr'] + tracker.at[key,'pick_4_cost_lr']


                                if tri_count == 3 or sup_count == 4:
                                    #curr = tracker.query('calc={}'.format(key))
                                    #wager_key = race_info.replace('_', '-')
                                    

                                    curr_tri = tracker.loc[key,'trifectas']
                                    tri_race_list = tracker.loc[key,'tri_races']
                                    tri_win = tracker.loc[key,'tri_winnings']
                                    curr_sup = tracker.loc[key,'superfectas']
                                    sup_race_list = tracker.loc[key,'sup_races']
                                    sup_win = tracker.loc[key,'sup_winnings']

                                    if tri_count == 3:
                                        #print('Won trifecta')
                                        
                                        tri_payout = wager.loc[race_info,'trifecta']
                                        tracker.at[key,'trifectas'] = curr_tri+1
                                        tracker.at[key,'tri_races'] = tri_race_list+','+race_info
                                        tracker.at[key,'tri_winnings'] = tri_win + tri_payout
                                        tracker.at[key,'race_total_winnings'] += tri_payout
                                        tracker.at[key,'total_winnings'] += tri_payout
                                    
                                    if sup_count == 4:
                                        #print('Won superfecta')
                                        sup_payout = wager.loc[race_info,'superfecta']
                                        tracker.at[key,'superfectas'] = curr_tri+1
                                        tracker.at[key,'sup_races'] = sup_race_list+','+race_info
                                        tracker.at[key,'sup_winnings'] = sup_win + sup_payout
                                        tracker.at[key,'race_total_winnings'] += sup_payout
                                        tracker.at[key,'total_winnings'] += sup_payout                  
                                    
                                tracker.at[key,'win_after_cost'] =   tracker.at[key,'total_winnings']-tracker.at[key,'total_cost']       
    return tracker, strict, less_strict, loose, looser
                        
def apply_weights(race_rank, the_race, race_tracker, summary_tracker, race_info):

    key = race_info.split('_')[0] + '_' + race_info.split('_')[1]
    if key not in summary_tracker.index.values:
        summary_tracker = summary_tracker.append(pd.DataFrame({'key':key,'win': 0,'place': 0, 'show':0, 'exacta_box': 0,'trifectas':0,'superfectas':0, 'tri_cost':0, 'tri_winnings' : 0, 'sup_cost':0,'sup_winnings':0, 'race_total_cost':0, 'race_total_winnings':0, 'total_cost':0, 'total_winnings':0, 'win_after_cost': 0}, index=[key]))

    race_tracker = race_tracker.append(pd.DataFrame({'race':race_info,'horse_order': '','win': 0,'place': 0, 'show':0, 'exacta_box': 0,'trifectas':0,'superfectas':0, 'tri_cost':0, 'tri_winnings' : 0, 'sup_cost':0,'sup_winnings':0, 'race_total_cost':0, 'race_total_winnings':0, 'total_cost':0, 'total_winnings':0, 'win_after_cost': 0}, index=[race_info]))
    file_path = '../data_files\\wager_sheet.csv'
    wager = pd.read_csv(file_path, index_col='date_track_race')
    wager = wager.fillna(0)

    horse = 90
    jockey = 0
    trainer = 0
    owner = 0
    post = 0
    odd = 10
    for ni, row in race_rank.iterrows():
        race_rank.at[ni,'optimize_val'] = ( (row['horse_rank'] * (horse/100)) + (row['jockey_rank'] * (jockey/100)) + (row['trainer_rank'] * (trainer/100)) + (row['owner_rank'] * (owner/100)) + (row['post_win'] * (post/100)) + (row['odds'] * (odd/100)) )

    race_rank = race_rank.sort_values(by=['optimize_val'],ascending=False)
    
    rank_winner = race_rank.iloc[0]['horse_name']
    rank_place = race_rank.iloc[1]['horse_name']
    rank_show = race_rank.iloc[2]['horse_name']

    actual_winner = the_race.iloc[0]['name']
    actual_place = the_race.iloc[1]['name']
    actual_show = the_race.iloc[2]['name']

    if rank_winner == actual_winner:
        race_tracker.at[race_info,'win'] += 1
        summary_tracker.at[key,'win'] += 1

    if rank_place == actual_place:
        race_tracker.at[race_info,'place'] += 1
        summary_tracker.at[key,'place'] += 1

    if rank_show == actual_show:
        race_tracker.at[race_info,'show'] += 1
        summary_tracker.at[key,'show'] += 1  

    if (rank_winner == actual_winner and rank_place == actual_place) or (rank_winner == actual_place and rank_place == actual_winner):     
        race_tracker.at[race_info,'exacta_box'] += 1
        summary_tracker.at[key,'exacta_box'] += 1 

    top_three = race_rank.iloc[0:3]['horse_name'].tolist()
    top_four = race_rank.iloc[0:4]['horse_name'].tolist()
    tri_list = the_race.iloc[0:3]['name'].tolist()
    sup_list = the_race.iloc[0:4]['name'].tolist()
    tri_count = 0
    sup_count = 0
    
    for n in top_three:
        if n in tri_list:
            tri_count +=1
    
    for n in top_four:
        if n in sup_list:
            sup_count +=1

    tri_cost = (wager.loc[race_info,'tri_unit']*6)
    sup_cost = (wager.loc[race_info,'super_unit']*24)
    
    race_tracker.at[race_info,'tri_cost'] += tri_cost
    race_tracker.at[race_info,'sup_cost'] += sup_cost
    race_tracker.at[race_info,'race_total_cost'] = (sup_cost+tri_cost)
    race_tracker.at[race_info,'total_cost'] += (sup_cost+tri_cost)

    summary_tracker.at[key,'tri_cost'] += tri_cost
    summary_tracker.at[key,'sup_cost'] += sup_cost
    summary_tracker.at[key,'race_total_cost'] = (sup_cost+tri_cost)
    summary_tracker.at[key,'total_cost'] += (sup_cost+tri_cost)

    if tri_count == 3 or sup_count == 4:
        #curr = tracker.query('calc={}'.format(key))
        #wager_key = race_info.replace('_', '-')
        

        curr_tri = race_tracker.loc[race_info,'trifectas']
        tri_win = race_tracker.loc[race_info,'tri_winnings']
        curr_sup = race_tracker.loc[race_info,'superfectas']
        sup_win = race_tracker.loc[race_info,'sup_winnings']

        if tri_count == 3:
            #print('Won trifecta')
            
            tri_payout = wager.loc[race_info,'trifecta']
            race_tracker.at[race_info,'trifectas'] = curr_tri+1
            race_tracker.at[race_info,'tri_winnings'] = tri_win + tri_payout
            race_tracker.at[race_info,'race_total_winnings'] += tri_payout
            race_tracker.at[race_info,'total_winnings'] += tri_payout

            summary_tracker.at[key,'trifectas'] = curr_tri+1
            summary_tracker.at[key,'tri_winnings'] = tri_win + tri_payout
            summary_tracker.at[key,'race_total_winnings'] += tri_payout
            summary_tracker.at[key,'total_winnings'] += tri_payout
        
        if sup_count == 4:
            #print('Won superfecta')
            sup_payout = wager.loc[race_info,'superfecta']
            race_tracker.at[race_info,'superfectas'] = curr_sup+1
            race_tracker.at[race_info,'sup_winnings'] = sup_win + sup_payout
            race_tracker.at[race_info,'race_total_winnings'] += sup_payout
            race_tracker.at[race_info,'total_winnings'] += sup_payout   

            summary_tracker.at[key,'superfectas'] = curr_sup+1
            summary_tracker.at[key,'sup_winnings'] = sup_win + sup_payout
            summary_tracker.at[key,'race_total_winnings'] += sup_payout
            summary_tracker.at[key,'total_winnings'] += sup_payout                
        
    race_tracker.at[race_info,'win_after_cost'] = race_tracker.at[race_info,'total_winnings'] - race_tracker.at[race_info,'total_cost']     
    summary_tracker.at[key,'win_after_cost'] = summary_tracker.at[key,'total_winnings'] - summary_tracker.at[key,'total_cost']    


    return race_tracker, summary_tracker
    
def predict_race(race, jrank, trank, orank, hrank, odds, post):

    race_rank = pd.DataFrame()
    for row_index,row in race.iterrows():
        data_row = {
            'jockey_name' : row['jockey'],
            'jockey_rank' : 0,
            'trainer_name' : row['trainer'],
            'trainer_rank' : 0,
            'owner_name' : row['owner'],
            'owner_rank' : 0,
            'horse_name' : row['name'],
            'horse_rank' : 0,
            'odds' : 0,
            'post_win' : 0,
            'final_rank' : 0
        }

        jrank = jrank.sort_values(by=['rank'], ascending=False)
        for j, jrow in jrank.iterrows():
            if jrow['name'] == data_row['jockey_name']:
                data_row['jockey_rank'] = jrow['rank']
                data_row['final_rank'] += jrow['rank']
                break

        trank = trank.sort_values(by=['rank'], ascending=False)
        for t, trow in trank.iterrows():
            if trow['name'] == data_row['trainer_name']:
                data_row['trainer_rank'] = trow['rank']
                data_row['final_rank'] += trow['rank']
                break

        
        orank = orank.sort_values(by=['rank'], ascending=False)
        for o, orow in orank.iterrows():
            if orow['name'] == data_row['owner_name']:
                data_row['owner_rank'] = orow['rank']
                data_row['final_rank'] += orow['rank']
                break

        for h, hrow in hrank.iterrows():
            if hrow['horse_name'] == data_row['horse_name']:
                data_row['horse_rank'] = hrow['speed_to_par']
                data_row['final_rank'] += hrow['speed_to_par']
                break

        for od,odds_row in odds.iterrows():
            if odds_row['horse_name'] == data_row['horse_name']:
                data_row['odds'] = odds_row['odds']
                data_row['final_rank'] += odds_row['odds']
                break

        for ppx,post_row in post.iterrows():
            if post_row['horse_name'] == data_row['horse_name']:
                data_row['post_win'] = post_row['post_perc']
                data_row['final_rank'] += post_row['post_perc']
                break
            
        race_rank = race_rank.append(data_row, ignore_index=True)

    return race_rank.sort_values(by=['final_rank'], ascending=False)

   

if __name__ == '__main__':
    ###
###Calculates rank of jockey, trainer, owner and exports a full dataset with the relevant ranks
###Executing this in all one script would take a very long time to process for all four data sets (jockey, trainer, owner, horse)
###Command line args all to be broken up into different machines
###Should add arg to process specific dataset (jockey, trainer, owner, horse)

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--start_num', help='Start date yyyy-mm-dd')
    parser.add_argument('--end_num', help='End date yyyy-mm-dd')
    args = parser.parse_args()
    print(args)

    pd.options.display.max_columns = None
    #pd.options.display.max_rows = None

    file_path = '../data_files\\processed_csv_testing\\full_race_table.csv'
    file_path = 'C:\\Users\\bod\\OneDrive\\Dev\\Personal\\exit_strategy\\predictions\\full_race_table_jockey_trainer_owner.csv' #'E:\\OneDrive\\Dev\\Personal\\exit_strategy\\predictions\\full_race_table_jockey_trainer_owner.csv'
    df = pd.read_csv(file_path)
    df['track_last_raced'].fillna('', inplace=True)

    start_date = datetime.datetime(year=2020,month=6,day=1)
    current_date = datetime.datetime(year=2020,month=6,day=15)
    str_start_date = start_date.strftime('%Y-%m-%d')
    str_end_date = current_date.strftime('%Y-%m-%d')
    post_query = df.query("date >'{}' and date <'{}'".format(str_start_date, str_end_date))
    unique_races = post_query.drop_duplicates(['date', 'track', 'race_number'])
    #display(unique_races.index)
    #first_race = df.query('pos_fin==1 and track_last_raced == ""')
    #display(first_race)

    #PROCESS ALL JOCKEYS
    # jockeys = df['jockey'].drop_duplicates().to_list()
    # print('Jockey processing: {} items'.format(len(jockeys)))
    # jockey_rank, jockey_stats = get_jockey_stats(jockeys,df, str_end_date)

    # df['jockey_rank'] = 0
    # for j, jrow in jockey_stats.iterrows():
    #     jockey_name = jrow['jockey']
    #     try:
    #         jrank = jockey_rank.loc[(jockey_rank.name == jockey_name),'rank']
    #         df.loc[(df.jockey == jockey_name), 'jockey_rank'] = jrank.iloc[0]
    #         #print('SUCCESS: {}'.format(jockey_name))
    #     except:
    #         print('jockey name not found: {}'.format(jockey_name))

    # df.to_csv('full_race_table_jockey.csv', index=False)

    #PROCESS ALL TRAINERS
    # trainers = df['trainer'].drop_duplicates().to_list()
    # print('Trainer processing: {} items'.format(len(trainers)))
    # trainer_rank,trainer_stats = get_trainer_stats(trainers,df, str_end_date)

    # df['trainer_rank'] = 0
    # for t, trow in trainer_stats.iterrows():
    #     trainer_name = trow['trainer']
    #     try:
    #         trank = trainer_rank.loc[(trainer_rank.name == trainer_name),'rank']
    #         df.loc[(df.trainer == trainer_name), 'trainer_rank'] = trank.iloc[0]
    #         #print('SUCCESS: {}'.format(jockey_name))
    #     except:
    #         print('trainer name not found: {}'.format(trainer_name))

    # df.to_csv('full_race_table_jockey_trainer.csv', index=False)

    #PROCESS ALL OWNERS
    # owners = df['owner'].drop_duplicates().to_list()
    # print('Owner processing: {} items'.format(len(owners)))
    # owner_rank, owner_stats = get_owner_stats(owners,df, str_end_date)

    # df['owner_rank'] = 0
    # for o, orow in owner_stats.iterrows():
    #     owner_name = orow['owner']
    #     try:
    #         orank = owner_rank.loc[(owner_rank.name == owner_name),'rank']
    #         df.loc[(df.owner == owner_name), 'owner_rank'] = orank.iloc[0]
    #         #print('SUCCESS: {}'.format(jockey_name))
    #     except:
    #         print('owner name not found: {}'.format(owner_name))

    # df.to_csv('full_race_table_jockey_trainer_owner.csv', index=False)


    #PROCESS ALL HORSES
    horses = df['name'].drop_duplicates().to_list()#df.drop_duplicates(['name', 'distance_float'])
    horses = sorted(horses)
    horses = horses[eval(args.start_num):eval(args.end_num)]
    horse_rank = speed_figure(horses,df, str_end_date)

    horse_rank.to_csv('horse_rank_{}.csv'.format(args.end_num), index=False)
    df['horse_rank'] = 0
    
    for h, hrow in horse_rank.iterrows():
        horse_name = hrow['horse_name']
        try:
            hrank = horse_rank.loc[(horse_rank.horse_name == horse_name),'speed_to_par']
            df.loc[(df.name == horse_name), 'horse_rank'] = hrank.iloc[0]
            #print('SUCCESS: {}'.format(jockey_name))
        except:
            print('owner name not found: {}'.format(horse_name))

    df.to_csv('full_race_table_jockey_trainer_owner_horses_{}.csv'.format(args.end_num), index=False)





