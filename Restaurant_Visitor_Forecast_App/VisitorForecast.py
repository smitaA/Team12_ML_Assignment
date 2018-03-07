import pandas as pd
from IPython.display import display

# Air data
air_store = pd.read_csv('Data/air_store_info.csv')
air_reserve = pd.read_csv('Data/air_reserve.csv')
air_visit = pd.read_csv('Data/air_visit_data.csv')
# HPG data
hpg_store = pd.read_csv('Data/hpg_store_info.csv')
hpg_reserve = pd.read_csv('Data/hpg_reserve.csv')
# Diverse data
date_info = pd.read_csv('Data/date_info.csv')
store_ids = pd.read_csv('Data/store_id_relation.csv')
# Submission file
submission = pd.read_csv('Data/sample_submission.csv')

# Check Air dataframes
print('--------------------air_store_info.csv data------------------------------\n')
display(air_store.head(3))
print('--------------------------------------------------\n')

print('----------------------air_reserve.csv data----------------------------\n')
display(air_reserve.head(3))
print('--------------------------------------------------\n')


print('--------------------------air_visit_data.csv data------------------------\n')
display(air_visit.head(3))
print('--------------------------------------------------\n')


# Check HPG dataframes
print('--------------------hpg_store_info.csv data------------------------------\n')
display(hpg_store.head(3))
print('--------------------------------------------------\n')
print('-------------------------hpg_reserve.csv data-------------------------\n')
display(hpg_reserve.head(3))
print('--------------------------------------------------\n')

# Check diverse dataframes
print('---------------------------date_info.csv data-----------------------\n')
display(date_info.head(3))
print('--------------------------------------------------\n')
print('---------------------store_id_relation.csv data-----------------------------\n')
display(store_ids.head(3))
print('--------------------------------------------------\n')

# Check submission dataframes
print('---------------------sample_submission.csv data-----------------------------\n')
display(submission.head(3))
print('--------------------------------------------------\n')

# Check for NaN
print('--------------------Check for NaN------------------------------\n')
print(air_store.isnull().sum(), '\n', air_reserve.isnull().sum(), '\n', air_visit.isnull().sum(),
      '\n', hpg_store.isnull().sum(), '\n', hpg_reserve.isnull().sum(), '\n', date_info.isnull().sum(),
      '\n', store_ids.isnull().sum(), '\n', submission.isnull().sum())
print('--------------------------------------------------\n')

# Format all dates using datetime
air_visit.visit_date = pd.to_datetime(air_visit.visit_date)
air_reserve.visit_datetime = pd.to_datetime(air_reserve.visit_datetime)
air_reserve.reserve_datetime = pd.to_datetime(air_reserve.reserve_datetime)
hpg_reserve.visit_datetime = pd.to_datetime(hpg_reserve.visit_datetime)
hpg_reserve.reserve_datetime = pd.to_datetime(hpg_reserve.reserve_datetime)
date_info.calendar_date = pd.to_datetime(date_info.calendar_date)

# Create copy of visit data.
visit_data = air_visit.copy()
display(visit_data.head(3))
visit_data['visitors'] = visit_data.visitors.map(pd.np.log1p)

# Remove holiday_flg from weekend days
wkend_holidays = date_info.apply((lambda x:(x.day_of_week=='Sunday' or x.day_of_week=='Saturday') and x.holiday_flg==1), axis=1)
date_info.loc[wkend_holidays, 'holiday_flg'] = 0


# Add weights to date_info before merging
# date_info['weight'] = ((date_info.index + 1) / len(date_info)) ** 6  # LB 0.497
date_info['weight'] = (((date_info.index + 1) / len(date_info)) ** 6.5)  # LB 0.496
# date_info['weight'] = ((date_info.index + 1) / len(date_info)) ** 7  # LB 0.496

# Define the date weighted mean function
wmean = lambda x:( (x.weight * x.visitors).sum() / x.weight.sum() )


# Add day of the week and holiday flag to air_visit dataframe
visit_data = visit_data.merge(date_info, left_on='visit_date', right_on='calendar_date', how='left')
#display(visit_data.head(3))
# drop to avoid duplicate date in visit_date and calender_date
visit_data.drop('calendar_date', axis=1, inplace=True)
print('----------------Merged air_visit_data.csv and date_info.csv data ----------------------------------\n')
display(visit_data.head(6))
print('--------------------------------------------------\n')

# Add restaurant genre to air_visit dataframe
print('----------------Merged air_visit_data.csv and air_store_info.csv data ----------------------------------\n')
visit_data = visit_data.merge(air_store[['air_store_id', 'air_genre_name']], on='air_store_id', how='left')
display(visit_data.head(3))
print('--------------------------------------------------\n')

# Combine both reservation systems. Data structure is the same, only need to match store_ids
print('----------------Merged hpg_reserve.csv and air_store_info.csv data ----------------------------------\n')
hpg_reserve = hpg_reserve.merge(store_ids, on='hpg_store_id')
# display(hpg_reserve.head(3))
hpg_reserve.drop('hpg_store_id', axis=1, inplace=True)
display(hpg_reserve.head(3))
print('--------------------------------------------------\n')

print('----------------Merged air_reserve.csv and hpg_reserve.csv data ----------------------------------\n')
all_reserve = pd.concat([air_reserve, hpg_reserve])
display(all_reserve.head(3))
print('--------------------------------------------------\n')

# Extract store_id and date from submission. Add day of the week
submission['visit_date'] = pd.to_datetime(submission.id.str[-10:])  # Get date by substring last 10 subset

submission = submission.merge(date_info, left_on='visit_date', right_on='calendar_date')
# display(submission.head(3))
submission['air_store_id'] = submission.id.str[:-11]
# display(submission.head(3))
submission.drop('calendar_date', axis=1, inplace=True)
print('----------------Submission data ----------------------------------\n')
display(submission.head(3))
print('--------------------------------------------------\n')

# Check how many restaurants are included in each system (reservations and actual visits)
print ("There are %s different stores in the visits data" %len(visit_data.air_store_id.unique()))
print ("There are %s different stores in the reservations data" %len(all_reserve.air_store_id.unique()))
print ("There are %s different stores in the submission data" %len(submission.air_store_id.unique()))
print('--------------------------------------------------\n')

# Populate each store with the WEIGHTED average for the same day for the same store
g1 = visit_data.groupby(['air_store_id', 'day_of_week', 'holiday_flg']).apply(wmean)

print('gr1 data frame')
display(pd.DataFrame(g1).head())

submissionData = submission.groupby(['air_store_id', 'day_of_week', 'holiday_flg']).mean().head()
print('--------------------------------------------------\n')
display(submissionData.head(3))
print('--------------------------------------------------\n')

# Combine groupby results with the submission file. Use 'left' to keep the orinal number of rows
submission = submission.merge(g1.reset_index(), on=['air_store_id', 'day_of_week', 'holiday_flg'], how='left')
# Tidy up the resulting submission file
submission.drop('visitors', axis=1, inplace=True)
submission.rename(columns={0: "visitors"}, inplace=True)
# Check
print('--------------------------------------------------\n')
submission.head(3)
print('--------------------------------------------------\n')


# Check we still have the required 32019 rows for submission
print(len(submission))
# Check if final results have any NaN
print(submission.isnull().sum())
print('--------------------------------------------------\n')
# Fill NaN using store_id and day_of_week
g2 = visit_data.groupby(['air_store_id','day_of_week']).mean()
print('---------------------Filled NaN using store_id and day_of_week-----------------------------\n')
display(g2.head())
print('--------------------------------------------------\n')

# Merge as new visitors column ('vistors_y'...previous one is renamed as 'visitors_x')
submission = submission.merge(g2.visitors.reset_index(), on=['air_store_id','day_of_week'], how='left')
# Tidy up the resulting submission file
submission.visitors_x.fillna(submission.visitors_y, inplace=True)
print('---------------------Merged data-----------------------------\n')
display(submission.head(3))
print('--------------------------------------------------\n')


# Check we still have the required 32019 rows for submission
print (len(submission))
# Check if final results have any NaN
submission.isnull().sum()
print(submission.isnull().sum())
print('--------------------------------------------------\n')


# Fill NaN using store_id
g3 = visit_data.groupby('air_store_id').mean()
# g2 = air_visit.groupby(['day_of_week', 'holiday_flg']).mean()
print('------------------Filled NaN using store_id--------------------------------\n')
display(g3.head())
print('--------------------------------------------------\n')
# Merge as new visitors column (names as 'visitors')
submission = submission.merge(g3.visitors.reset_index(), on=['air_store_id'], how='left')

# # Fill NaN in original visitors column with values in the recently merged on
submission['visitors_x'].fillna(submission['visitors'], inplace=True)
# # Tidy up
submission.drop(['visitors_y', 'visitors'], axis=1, inplace=True)  # Drop the added ones
submission.rename(columns={'visitors_x':'visitors'}, inplace=True)  # Rename the good one
print('--------------------Submission data------------------------------\n')
display(submission.head(3))
print('--------------------------------------------------')

# Check we still have the required 32019 rows for submission
print (len(submission))
# Check if final results have any NaN
submission.isnull().sum()
print(submission.isnull().sum())
print('--------------------------------------------------')


# Undo log transformation to 'visitors'
submission['visitors'] = submission.visitors.map(pd.np.expm1)
visit_data.visitors = visit_data.visitors.map(pd.np.expm1)


results = submission[['id', 'visitors']]
results.set_index('id', inplace=True)
print('-----------------Result---------------------------------\n')
display(results)
print('--------------------------------------------------\n')

print('----------------Submission data by id----------------------------------\n')
display(submission.sort_values(by='id').head(10))
print('--------------------------------------------------')


# Save results file
results = submission[['id', 'visitors']]
results.set_index('id', inplace=True)
results.to_csv('RestaurantVisitorsPredictionResult.csv')
