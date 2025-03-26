import requests
import pandas as pd
import os
from dotenv import load_dotenv
from pathlib import Path

dotenv_path = Path("week9/.env")
load_dotenv(dotenv_path=dotenv_path)


# urls
covid_data_url = 'https://raw.githubusercontent.com/owid/covid-19-data/refs/heads/master/public/data/latest/owid-covid-latest.json'
cities_url = "https://raw.githubusercontent.com/dr5hn/countries-states-cities-database/refs/heads/master/json/countries%2Bstates%2Bcities.json"



# covid dataframe
covid_response = requests.get(covid_data_url)
try:
    covid_response.raise_for_status()
    data = covid_response.json()
    covid_data_df = pd.DataFrame()
    for country_code in data.keys():
        df = pd.json_normalize(data[country_code], sep="_")
        df['country_code'] = country_code
        covid_data_df = pd.concat([covid_data_df, df], ignore_index=True)
except requests.exceptions.RequestException as e:
    print(f"Error! {e}")

covid_data_df = covid_data_df[['continent','country_code', 'location', 'last_updated_date','total_cases','new_cases',  'total_deaths', 'new_deaths']]



# cities dataframe
cities_response = requests.get(cities_url)
if cities_response.status_code == 200:  
    cities_data = cities_response.json()
    cities_df = pd.DataFrame(cities_data)
    cities_df = cities_df[['name', 'iso3', 'capital', 'latitude', 'longitude']]
else:
    print(f"Error! {covid_response.status_code}")


# cities' weather_data_df
API_KEY = os.getenv("OPENWEATHER_API_KEY")
weather_data_list = []
for city in cities_df['capital']:
    # print(city)
    weather_url = f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}'
    response = requests.get(weather_url)
    if response.status_code == 200:
        data = response.json()
        weather_data_list.append({
            'city' : data.get('name','N/A'),
            'condition' : data['weather'][0].get('description', 'N/A'),
            'temp_min' : data['main'].get('temp_min','N/A'),
            'temp_max' : data['main'].get('temp_max', 'N/A')
        })
    else:
        print(f'Error due to {response.status_code}')

weather_data_df = pd.DataFrame(weather_data_list)


# checking data
print(covid_data_df.head())
print(cities_df.head())
print(weather_data_df.head())


# merging dataframes
# cities_covid_data_df = pd.merge(covid_data_df, cities_df, how="left", left_on="country_code", right_on="iso3")
cities_covid_data_df = pd.merge(covid_data_df, cities_df, how="left", left_on="location", right_on="name")
print(cities_covid_data_df.head())

cities_covid_data_df = cities_covid_data_df[['location', 'capital', 'latitude', 'longitude', 'last_updated_date', 'total_cases', 'new_cases', 'total_deaths', 'new_deaths']]
cities_covid_data_df.head()

cities_covid_weather_data_df = pd.merge(cities_covid_data_df, weather_data_df, how="left", left_on="location", right_on="city")
cities_covid_weather_data_df = cities_covid_weather_data_df[['location', 'capital', 'latitude', 'longitude', 'last_updated_date', 'total_cases', 'new_cases', 'total_deaths', 'new_deaths', 'condition', 'temp_min', 'temp_max']]
print(cities_covid_weather_data_df.head())


# CSV file
cities_covid_weather_data_df.to_csv("cities_covid_weather_data.csv")