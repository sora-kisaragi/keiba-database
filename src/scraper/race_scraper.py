import requests
import re
from bs4 import BeautifulSoup
from ..utils import html_parser

class RaceScraper:
    def __init__(self):
        self.base_url = "https://db.netkeiba.com/race/{}/"
        self.race_list_url = "https://db.netkeiba.com/race/list/{}"

    def scrape_race_data(self, race_id):
        '''
        レース結果のページから必要なデータを取得する。
        '''
        response = requests.get(self.base_url.format(race_id))
        return html_parser.parse_html(response.text)

    def parse_race_data(self, soup):
        '''
        レース結果のページから必要なデータを抽出する。
        '''
        # IDが'All_Result_Table'のテーブルを見つける
        table = soup.find('table', {'id': 'All_Result_Table'})

        # テーブルの各行をループ
        for row in table.find_all('tr'):
            # 各セルのテキストを取得
            cells = [cell.text for cell in row.find_all('td')]

            # セルのテキストをDataFrameに追加
            race_data = race_data.append(pd.Series(cells), ignore_index=True)

        return race_data

    def get_raceid_list_from_date(self, today):
        
        # 日付をYYYYMMDD形式に変換してURLを作成
        date = f'{today.year:04}{today.month:02}{today.day:02}'
        url = self.race_list_url.format(date)

        # URLからHTMLを取得
        html = requests.get(url)
        # レスポンスのステータスコードが200以外の場合は例外を発生させる
        html.raise_for_status()
        # レスポンスのエンコーディングを確認
        html.encoding = 'EUC-JP'
        # レスポンスをバイナリデータとして取得し、適切なエンコーディングでデコード
        soup = BeautifulSoup(html.text, "html.parser")
        # レース一覧のテーブルを取得
        race_list = soup.find('div', attrs={"class": 'race_list fc'})

        # レースIDをリストに格納
        if race_list is None:
            # レースが存在しない場合は空のリストを返す
            return list()
        # href属性からレースIDを取得
        a_tag_list = race_list.find_all('a')
        href_list = [a_tag.get('href') for a_tag in a_tag_list]
        race_id_list = list()
        for href in href_list:
            # href属性からレースIDを抽出
            for race_id in re.findall('[0-9]{12}', href):
                # レースIDをリストに追加
                race_id_list.append(race_id)
        return list(set(race_id_list))

    # TODO: データベースに保存する処理に変更する。
    def save_race_data(self, race_data, file_path):
        '''
        パースしたデータをCSV形式で保存する。
        '''
        # ここでrace_dataをCSV形式で保存します。
        pass