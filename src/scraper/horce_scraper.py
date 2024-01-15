import pandas as pd
from bs4 import BeautifulSoup
import requests
import os
import io

class HorseScraper:
    def __init__(self):
        self.base_url = "https://db.netkeiba.com/horse/{}"

    def scrape_horse_data(self, horse_id):
        '''
        馬の情報のHTMLを取得する。
        '''

        # URLを作成
        url = self.base_url.format(horse_id)
        # URLからHTMLを取得
        response = requests.get(self.base_url.format(horse_id))
        # レスポンスのステータスコードが200以外の場合は例外を発生させる
        response.raise_for_status()
        # レスポンスのエンコーディングを確認
        encoding = response.encoding if 'charset' in response.headers.get('content-type', '').lower() else None
        # レスポンスをバイナリデータとして取得し、適切なエンコーディングでデコード
        html = response.content.decode(encoding if encoding else 'euc-jp')

        # HTMLをファイルに保存
        directory = f'../data/horse/{horse_id}'
        # ディレクトリが存在しない場合は作成
        if not os.path.exists(directory):
            os.makedirs(directory)
        # ファイルをhorse IDのdirectoryに保存
        with open(f'{directory}/{horse_id}.html', 'w', encoding='utf-8') as f:
            f.write(html)

        return response.content

    def parse_horse_data(self, horse_id):
        '''
        保存されたHTMLを読み込み、馬のデータを取得する。
        '''
        directory = f'../data/horse/{horse_id}'
        # 保存されたHTMLを読み込む
        with open(f'{directory}/{horse_id}.html', 'r') as f:
            html = f.read()

        # BeautifulSoupでHTMLをパースする
        soup = BeautifulSoup(html, 'html.parser')

        # 馬の名前を取得
        horse_name_jp = soup.find('div', class_='horse_title').h1.text
        horse_name_en = soup.find('div', class_='horse_title').p.a.text
        # データフレームを作成
        horse_name_df = pd.DataFrame({
            '馬ID': [horse_id],
            '馬名': [horse_name_jp],
            '馬名(英)': [horse_name_en]
        }, index=[0])  # インデックスを設定
        # プロフィールテーブルからデータを取得
        profile_table = soup.find('table', {'class': 'db_prof_table no_OwnerUnit'})
        profile_df = pd.read_html(io.StringIO(str(profile_table)), flavor='bs4')[0]
        # DataFrameを転置
        profile_df = profile_df.T
        # 最初の行を取得
        first_row = profile_df.iloc[0]

        # 最初の行をカラム名に設定
        profile_df = profile_df[1:]
        profile_df.columns = first_row


        profile_df = pd.concat([horse_name_df, profile_df], axis=0)

        # 血統テーブルからデータを取得
        blood_table = soup.find('table', {'class': 'blood_table'})
        blood_df = pd.read_html(io.StringIO(str(blood_table)), flavor='bs4')[0]

        # 戦績テーブルからデータを取得
        race_results_table = soup.find('table', {'class': 'db_h_race_results nk_tb_common'})
        race_results_df = pd.read_html(io.StringIO(str(race_results_table)), flavor='bs4')[0]

        horse_data = {
            'profile': profile_df,
            'bloodline': blood_df,
            'race_results': race_results_df
        }

        return horse_data

    def save_data(self, horse_id, data):
        '''
        データをファイルに保存する。
        '''
        pass

    def get_horse_data(self, horse_id, scraping=True, skip_scraping=False):
        '''
        馬の情報を取得し、HTMLとデータを保存する。
        '''
        # フラグに応じてスクレイピングを実行
        if scraping:
            html = self.scrape_horse_data(horse_id)
        # スクレイピングをスキップする場合は、保存されたHTMLを読み込む
        if skip_scraping:
            # もしhorce_id.htmlが存在する場合はスクレイピングをスキップ
            directory = f'../data/horse/{horse_id}'
            if os.path.exists(f'{directory}/{horse_id}.html'):
                html = None
            else:
                html = self.scrape_horse_data(horse_id)
        # 保存されたデータをパース
        data = self.parse_horse_data(horse_id)

        return data