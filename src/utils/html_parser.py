from bs4 import BeautifulSoup
import requests

# todo : 現在有効利用出来ていないため将来的に削除の可能性あり
# 別のpackageから呼び出すことが出来ていない
class HtmlParser:
    def __init__(self):
        pass

    def parse_html(self,html):
        soup = BeautifulSoup(html, 'html.parser')
        return soup