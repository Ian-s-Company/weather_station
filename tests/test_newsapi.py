import pytest
import sys
sys.path.append('/home/ianrscott/weather_station')
from weather import Weather

@pytest.fixture
def example_weather_data():
    import os

    API_KEY_NEWS = os.environ["API_KEY_NEWS"]

    return [
    {
        "latitude": "33.104191",
        "longitude": "-96.67173",
        "api_id": API_KEY_NEWS,
        "app_dir": "/opt/weather_station"
    } #,    
    #{
    #    "latitude": "34.104191",
    #    "longitude": "-96.67173",
    #    "api_id": API_KEY_WEATHER,
    #    "app_dir": "/opt/weather_station"
    #}
]

expected = {"lat":"33.1042","lon":"-96.6717"}


#@pytest.mark.parametrize(
#    "lon, lat, api_key, app_dir,expected", 
#    [
#        (testdata['lon'], testdata['lat'], '{"lat":33.1042,"lon":-96.6717,"timezone":"America/Chicago","timezone_offset":-18000,"current":')
#    ]
#)

def test_connect_to_weather_data(example_weather_data):
    for data_set in example_weather_data:
        #print(data_set['latitude'], data_set['longitude'], data_set['api_id'], data_set['app_dir'])
        weather_inst = Weather(data_set['latitude'], data_set['longitude'], data_set['api_id'], data_set['app_dir'])
        weather_data = weather_inst.update()
        print(str(weather_data['lat']))
        lat_string = str(weather_data['lat'])
        print("The lat string is: " + lat_string)
        print("The expeced lat is: " + expected["lat"])
        #assert str("wrong") == str(expected["lat"])
        assert str(weather_data['lat']) == str(expected["lat"])