import requests
import pandas as pd 


# url
covid_data_url = 'https://raw.githubusercontent.com/owid/covid-19-data/refs/heads/master/public/data/latest/owid-covid-latest.json'
cities_url = 'https://raw.githubusercontent.com/dr5hn/countries-states-cities-database/refs/heads/master/json/countries%2Bcities.json'



# Extract covid data
covid_response = requests.get(covid_data_url)

if covid_response.status_code == 200:
    data = covid_response.json()
    covid_data = pd.DataFrame()
    for country_code in data.keys():
        df = pd.json_normalize(data[country_code], sep="_")
        df['country_code'] = country_code
        covid_data = pd.concat([covid_data, df], ignore_index=True)
else:
    print(f"Error! {covid_response.status_code}")

covid_data = covid_data[['continent','country_code', 'location', 'last_updated_date','total_cases','new_cases',  'total_deaths', 'new_deaths']]
# print(covid_data.head())



# Extract cities data
cities_response = requests.get(cities_url)

if cities_response.status_code == 200:
    data = cities_response.json()
    cities_data = pd.DataFrame(data)
else:
    print(f"Error! {cities_response.status_code}")
cities_data = cities_data[['name', 'iso3', 'capital', 'latitude', 'longitude']]


# Mergin two DataFrames
merge_covid_data = pd.merge(
    covid_data,
    cities_data,
    left_on='country_code',
    right_on='iso3',
    how='left'
)

final_covid_data = merge_covid_data[['continent', 'country_code', 'location', 'capital', 'latitude', 'longitude', 'last_updated_date','total_cases', 'new_cases', 'total_deaths', 'new_deaths']]

final_covid_data.to_csv('covid_data.csv')