import pytest
from news import News


@pytest.fixture
def example_news_data():
    import os

    API_KEY_NEWS = os.environ["API_KEY_NEWS"]

    return [
        {
            "api_id": API_KEY_NEWS,
        }
    ]


expected = {"status": "ok"}


def test_connect_to_news_data(example_news_data):
    for data_set in example_news_data:
        news_inst = News(170)
        news_data = news_inst.update(data_set["api_id"])
        print(news_data)
        status_string = str(news_data["status"])
        print("The status string is: " + status_string)
        print("The expeced status is: " + expected["status"])
        # assert str("wrong") == str(expected["lat"])
        assert str(news_data["status"]) == str(expected["status"])
