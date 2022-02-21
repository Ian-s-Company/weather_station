# -*- coding:utf-8 -*-

import requests
import textwrap

class News:
    def __init__(self,width):
        self.width = width
        pass

    def update(self, api_id):
        self.news_list = requests.get(
            f"https://newsapi.org/v2/top-headlines?source=the-washington-post&apiKey={api_id}&country=us").json()
        return self.news_list

    def selected_title(self):
        list_news = []
        if self.news_list["status"] == "ok":
            for i in range(len(self.news_list["articles"])):
                line = self.news_list["articles"][i]["title"]
                line = textwrap.wrap(line, width=self.width)
                list_news.append(line)
        else:
            list_news = ["Problem getting the news"]
        return list_news
