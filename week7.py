import requests
import pandas as pd

url = 'https://raw.githubusercontent.com/owid/covid-19-data/refs/heads/master/public/data/latest/owid-covid-latest.json'
response = requests.get(url)



if response.status_code == 200:
    data = response.json()

    country_covid_data = pd.DataFrame()

    for country_code, country_data in data.items():
        df = pd.json_normalize(data[country_code], sep="_")
        df['country_code'] = country_code
        country_covid_data = pd.concat([country_covid_data, df], ignore_index=True)

country_covid_data.to_csv('country_covid_data.csv')