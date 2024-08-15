import pytest
from weather import Weather

@pytest.fixture
def example_weather_data():
    import os

    API_KEY_WEATHER = os.environ["API_KEY_WEATHER"]

    return [
        {
            "latitude": "33.104191",
            "longitude": "-96.67173",
            "api_id": API_KEY_WEATHER
        } 
    ]

expected = {"lat": "33.1042", "lon": "-96.6717"}

def test_connect_to_weather_data(example_weather_data):
    for data_set in example_weather_data:
        # print(data_set['latitude'], data_set['longitude'], data_set['api_id'], data_set['app_dir'])
        weather_inst = Weather(
            data_set["latitude"],
            data_set["longitude"],
            data_set["api_id"],
            data_set["app_dir"],
        )
        weather_data = weather_inst.update()
        print(str(weather_data["lat"]))
        lat_string = str(weather_data["lat"])
        print("The lat string is: " + lat_string)
        print("The expeced lat is: " + expected["lat"])
        assert str(weather_data["lat"]) == str(expected["lat"])
