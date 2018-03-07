# Team12_ML_Assignment
Recruit restaurant forecasting

Problem Statement:
 
Predict the total number of visitors to a restaurant for future dates using reservation and visitation data. The restaurants need to know how many customers to expect each day to effectively purchase ingredients and schedule staff members. This forecast isn't easy to make because many unpredictable factors affect restaurant attendance, like weather and local competition. Using reservation and visitation data to predict the total number of visitors to a restaurant for future dates.
https://www.kaggle.com/c/recruit-restaurant-visitor-forecasting



Description:

•	Read and analyzed provided data (.csv) files

•	Analyzed relationship data of Hot Pepper Gourmet and AirREGI site data

•	Identified unique identifier of data from data relation

•	Created copy of air_visit data

•	Removed holiday flag from weekend in date info 

•	Added weight to Date_info data

•	Added day of the week and holiday flag to air_visit dataframe

•	Added restaurant genre to air_visit dataframe

•	Combined both reservation systems. Data structure is the same, hence need to match store_ids

•	Merged air_reserve.csv and hpg_reserve.csv data

•	Dropped duplicate data while merging the data like date in visit_date and calender_date, hpg_store_id to match store_ids

•	Extracted store_id and date from submission. Added day of the week

•	Checked how many restaurants are included in each system

•	Defined date weighted mean function 

•	Populated each store with the weighted average for the same day for the same store

•	Combined group by results with the submission file

•	Verified we still have the required 32019 rows for submission

•	Checked NaN in final result

•	Filled NaN using store_id and day_of_week 

•	Merged as new visitor’s column 

•	Repeated till fill all NaN in the final result

•	Stored final predication result in the ‘RestaurantVisitorsPredictionResult.csv’ file.

