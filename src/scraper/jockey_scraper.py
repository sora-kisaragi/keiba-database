import requests
import math
import time
import sys
import os
import pandas as pd
from tqdm import tqdm
from bs4 import BeautifulSoup
from utils import html_parser

class JockeyScraper:
    def __init__(self, base_url):
        self.base_url = base_url
        self.jockey_name = None

    def get_jockey_data(self, jockey_id,scraping=True):
        data, self.jockey_name = self.get_jockey_record_totals(jockey_id)
        # コンマを削除してから整数に変換
        num = int(data['着外'].replace(',', ''))
        if scraping:
            # データを取得
            self.scrape_jockey_data_pages(jockey_id, num)
        # 着順のカウントを取得
        count_dict = self.parse_jockey_data(jockey_id)
        # 1~3着のカウントを結合
        count_dict['1'] = int(data['1着'].replace(',', ''))
        count_dict['2'] = int(data['2着'].replace(',', ''))
        count_dict['3'] = int(data['3着'].replace(',', ''))
        # 着順のカウントを返す
        return count_dict

    def _get_jockey_name(self, soup):
        head_div = soup.find('div', class_='db_head_name fc')
        name_div = head_div.find('div', class_='Name')
        name = name_div.h1.get_text(strip=True).replace(' ', '').replace('.', '. ')
        return name.replace('\n', ' ')

    def get_jockey_record_totals(self, jockey_id):
        # jockey_idからURLを作成
        url = f"https://db.netkeiba.com/jockey/{jockey_id}/"

        # URLからHTMLを取得
        response = requests.get(url)
        response.encoding = 'euc-jp'  # エンコーディングをeuc-jpに設定
        response.raise_for_status()  # ステータスコードが200以外の場合に例外を発生させる

        # HTMLをパース
        soup = BeautifulSoup(response.text, 'html.parser')

        # 騎手名を取得して表示
        jockey_name = self._get_jockey_name(soup)

        # テーブル行を見つける
        rows = soup.find_all('tr', class_='')
        # データを格納するための辞書を作成
        row_data = {}
        for row in rows:
            if row.find('td', class_='cel_opacity'):  # 'cel_opacity'クラスを持つ要素が存在する場合のみ処理を行う
                row_data['total'] = row.find('td', class_='cel_opacity').text
                row_data['1着'] = row.find('a', href=lambda x: x and 'mode=r1' in x).text if row.find('a', href=lambda x: x and 'mode=r1' in x) else None
                row_data['2着'] = row.find('a', href=lambda x: x and 'mode=r2' in x).text if row.find('a', href=lambda x: x and 'mode=r2' in x) else None
                row_data['3着'] = row.find('a', href=lambda x: x and 'mode=r3' in x).text if row.find('a', href=lambda x: x and 'mode=r3' in x) else None
                row_data['着外'] = row.find('a', href=lambda x: x and 'mode=r4' in x).text if row.find('a', href=lambda x: x and 'mode=r4' in x) else None
                break # 初回のみ処理を行う

        return row_data , jockey_name

    def scrape_jockey_data(self, jockey_id, page=1):

        # URLを作成
        url = f"https://db.netkeiba.com//?pid=jockey_select&id={jockey_id}&year=0000&mode=r4&page={page}"

        # URLからHTMLを取得
        response = requests.get(url)

        # レスポンスのエンコーディングを確認
        encoding = response.encoding if 'charset' in response.headers.get('content-type', '').lower() else None
        # レスポンスをバイナリデータとして取得し、適切なエンコーディングでデコード
        html = response.content.decode(encoding if encoding else 'euc-jp')

        # HTMLをファイルに保存
        directory = f'../data/jockey/{jockey_id}'
        # ディレクトリが存在しない場合は作成
        if not os.path.exists(directory):
            os.makedirs(directory)
        # ファイルをJockey IDのdirectoryに保存
        with open(f'{directory}/page_{str(page).zfill(3)}.html', 'w', encoding='utf-8') as f:
            f.write(html)

        return html

    def scrape_jockey_data_pages(self, jockey_id, num_out_of_place):
        # 着外の数を20で割って小数点を切り上げる
        num_pages = math.ceil(num_out_of_place / 20)
        print(f'合計ページ数: {num_pages}')
        print('webからデータを取得する処理を開始します。')
        # データを格納する辞書
        data = {}

        # 処理時間をバーで表示するための設定
        with tqdm(total=num_pages) as pbar:
            # 指定されたページ数だけループを回す
            for page in range(1, num_pages + 1):
                # scrape_jockey_dataメソッドを呼び出す
                page_data = self.scrape_jockey_data(jockey_id,page)
                # データを格納
                data[page] = page_data
                pbar.update(1)

        return data

    def parse_jockey_data(self, jockey_id):
        print('保存したhtmlからデータを抽出します。')
        # ディレクトリ内のすべてのファイル名を取得
        directory = f'../data/jockey/{jockey_id}'
        filenames = os.listdir(directory)

        # 着順のカウントを格納する辞書
        count_dict = {}

        with tqdm(total=len(filenames)) as pbar:
            # 各ファイルをループで開く
            for filename in filenames:
                # HTMLファイルからテーブルを読み込む
                try:
                    tables = pd.read_html(f'{directory}/{filename}', header=0)
                    # 最初のテーブルを取得
                    table = tables[0]

                    # '着順'または'着 順'カラムが存在するか確認
                    column_name = '着順' if '着順' in table.columns else '着 順' if '着 順' in table.columns else None

                    # '着順'または'着 順'カラムが存在しない場合は処理をスキップ
                    if column_name:
                        count = table[column_name].value_counts()
                        # キーを文字列に変換
                        count.index = count.index.astype(str)
                        for key, value in count.items():
                            if key in count_dict:
                                count_dict[key] += value
                            else:
                                count_dict[key] = value
                # ValueErrorが発生した場合は処理をスキップ
                except ValueError:
                    continue
                # バーを更新
                finally:
                    pbar.update(1)

        # 着順のカウントを返す
        return count_dict