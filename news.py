# -*- coding:utf-8 -*-

import requests
import logging
import textwrap
import time


class News:
    def __init__(self, width, api_id):
        self.width = width
        self.api_key = api_id

    def update(self):
        source = "the-washington-post"
        news_url = (
            "https://newsapi.org/v2/top-headlines?source="
            + source
            + "&apiKey="
            + self.api_key
            + "&country=us"
        )
        got_data = False

        logging.info("-------News Update Begin ")
        while got_data == False:
            logging.info("Checking News URL Status")
            try:
                news_data = requests.get(news_url)
            except:
                time.sleep(60)
                continue

            if news_data.ok:
                logging.info(news_data.status_code)
                got_data = True
                logging.info("Got data from News URL to return successfully")
                news_list = news_data.json()
            else:
                logging.info("Waiting for the News URL to return successfully")
                news_list = None
                time.sleep(15)
        logging.info("-------News Update End")
        return news_list

    def selected_title(self, news_list):
        list_news = []
        if news_list["status"] == "ok":
            for i in range(len(news_list["articles"])):
                line = news_list["articles"][i]["title"]
                line = textwrap.wrap(line, width=self.width)
                list_news.append(line)
        else:
            list_news = ["Problem getting the news"]
        return list_news
