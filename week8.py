import requests
import pandas as pd

API_KEY = 'ffe5d054b617b526d2b3fe87efe80904'
city_name = 'Yangon'
weather_url = f'https://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={API_KEY}'

response = requests.get(weather_url)
weather_data = response.json()

# for k, v in weather_data.items():
#     print(k, v)

weather_data_df = pd.json_normalize(weather_data)
print(weather_data_df)

# weather_data_dict = {
#     'city' : weather_data['name'],
#     'condition' : weather_data['weather'][0]['description'],
#     'temp_min' : weather_data['main']['temp_min'],
#     'temp_max' : weather_data['main']['temp_max']
# }
# weather_data_df = pd.DataFrame(weather_data_dict, index=[0,weather_data_dict.count()])

# print(weather_data_df)
