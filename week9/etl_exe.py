# Import required libraries
import requests
import pandas as pd
import numpy as np
import logging
import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename="./etl.log"
)


def get_json_from_url(url: str) -> dict:
    """Fetch JSON data from a URL with error handling."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logging.error(f"Error fetching data from {url}: {e}")
        return {}


def get_covid_data() -> pd.DataFrame:
    """Fetch COVID-19 data and return a cleaned DataFrame."""
    url = "https://raw.githubusercontent.com/owid/covid-19-data/refs/heads/master/public/data/latest/owid-covid-latest.json"
    covid_data_json = get_json_from_url(url)

    if not covid_data_json:
        return pd.DataFrame()

    covid_data_list = [
        pd.json_normalize(data).assign(country_code=code)
        for code, data in covid_data_json.items()
    ]

    covid_df = pd.concat(covid_data_list, ignore_index=True)
    covid_df.replace(r"^\s*$", np.nan, regex=True, inplace=True)

    selected_cols = ['continent', 'country_code', 'location', 'last_updated_date',
                     'total_cases', 'new_cases', 'total_deaths', 'new_deaths', 'population']
    covid_df = covid_df[selected_cols].dropna(subset=['continent'])

    return covid_df


def get_city_data() -> pd.DataFrame:
    """Fetch city data and return a structured DataFrame."""
    city_url = "https://raw.githubusercontent.com/dr5hn/countries-states-cities-database/refs/heads/master/json/countries%2Bstates%2Bcities.json"
    city_json = get_json_from_url(city_url)

    if not city_json:
        logging.error("Failed to retrieve city data")
        return pd.DataFrame()

    cities_list = [
        {
            'country_id': country.get('id', np.nan),
            'country_name': country.get('name', np.nan),
            'country_code': country.get('iso3', np.nan),
            'country_numeric_code': country.get('numberic_code', np.nan),
            'country_phonecode': country.get('phonecode', np.nan),
            'country_capital': country.get('capital', np.nan),
            'country_region': country.get('region', np.nan),
            'country_subregion': country.get('subregion', np.nan),
            'country_latitude': country.get('latitude', np.nan),
            'country_longitude': country.get('longitude', np.nan),
            'state_id': state.get('id', np.nan),
            'state_name': state.get('name', np.nan),
            'state_latitude': state.get('latitude', np.nan),
            'state_longitude': state.get('longitude', np.nan),
            'city_id': city.get('id', np.nan),
            'city_name': city.get('name', np.nan),
            'city_latitude': city.get('latitude', np.nan),
            'city_longitude': city.get('longitude', np.nan)
        }
        for country in city_json
        for state in country.get('states', [])
        for city in state.get('cities', [])
    ]

    logging.info(f"Fetched data for {len(cities_list)} cities.")
    return pd.DataFrame(cities_list)


def get_city_weather_data_by_lat_lon(latitude: str, longitude: str) -> dict:
    """Fetch weather data for a city using latitude and longitude."""
    API_KEY = os.getenv("OPENWEATHER_API_KEY")
    if not API_KEY:
        logging.error("Missing OpenWeather API Key.")
        return {}

    weather_url = f"https://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid={API_KEY}&units=metric"

    try:
        weather_json = get_json_from_url(weather_url)
        if not weather_json:
            return {}

        return {
            "city": weather_json.get('name', "Unknown"),
            "latitude": latitude,
            "longitude": longitude,
            "condition": weather_json.get('weather', [{}])[0].get('description', "Unknown"),
            "temperature_min": weather_json.get('main', {}).get('temp_min', np.nan),
            "temperature_max": weather_json.get('main', {}).get('temp_max', np.nan)
        }
    except Exception as e:
        logging.error(f"Failed to fetch weather data for {latitude}, {longitude}: {e}")
        return {}


def get_all_cities_weather_data(lat_lon_list: list) -> pd.DataFrame:
    """Fetch weather data for all cities."""
    weather_data = [
        get_city_weather_data_by_lat_lon(city['city_latitude'], city['city_longitude'])
        for city in lat_lon_list
    ]
    return pd.DataFrame(filter(None, weather_data))


def transform_data() -> pd.DataFrame:
    """Transform and merge COVID, city, and weather data into a final dataset."""
    covid_df = get_covid_data()
    if covid_df.empty:
        logging.error("No COVID-19 data available.")
        return pd.DataFrame()

    covid_df = covid_df.nlargest(3, 'total_cases')

    cities_df = get_city_data()
    if cities_df.empty:
        logging.error("No city data available.")
        return pd.DataFrame()

    # Merge city and COVID-19 data
    merged_df = cities_df.merge(covid_df, on='country_code', how="inner")
    selected_cols = ['country_region', 'country_subregion', 'country_name', 'country_code',
                     'country_capital', 'state_name', 'city_name', 'city_latitude', 'city_longitude',
                     'total_cases', 'new_cases', 'total_deaths', 'new_deaths']
    merged_df = merged_df[selected_cols]

    # Fetch weather data
    lat_lon_list = merged_df[['city_latitude', 'city_longitude']].to_dict(orient='records')
    weather_df = get_all_cities_weather_data(lat_lon_list)

    # Merge weather data
    final_df = merged_df.merge(weather_df, left_on=['city_latitude', 'city_longitude'],
                               right_on=['latitude', 'longitude'], how="inner")

    selected_final_cols = ['country_region', 'country_subregion', 'country_name', 'country_code',
                           'country_capital', 'state_name', 'city_name', 'city_latitude', 'city_longitude',
                           'total_cases', 'new_cases', 'total_deaths', 'new_deaths', 'condition',
                           'temperature_min', 'temperature_max']
    return final_df[selected_final_cols]


def load_data(df: pd.DataFrame):
    """Load DataFrame into an SQLite database."""
    if df.empty:
        logging.error("No data to load into database.")
        return

    engine = create_engine('sqlite:///w9_demo.db')
    df.to_sql("covid_city_demo", engine, if_exists="replace", index=False)
    logging.info("Data successfully loaded into SQLite database.")
    print("Successfully loaded into SQLite DB!")


if __name__ == "__main__":
    final_df = transform_data()
    print(final_df.shape)
    load_data(final_df)
