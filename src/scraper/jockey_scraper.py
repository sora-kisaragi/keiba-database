import re
import time
import requests
import math
import os
import pandas as pd
from tqdm import tqdm
from bs4 import BeautifulSoup
from requests.exceptions import Timeout


class JockeyScraper:
    def __init__(self):
        self.base_url = 'https://db.netkeiba.com/'
        self.list_url = "https://db.netkeiba.com/jockey/"
        self.jockey_name = None
        # param_1 : 現役 or 引退 [0 or 1]
        # param_2 : ページ数
        self.jockey_db_url = 'https://db.netkeiba.com//?pid=jockey_list&list=100&act%5B0%5D={}&page={}'
        # param : スクレイピングを実行した日付
        self.jockey_id_list_file = '../data/jockey/jockey_id_list/{}.csv'
        self.last_page_file = '../data/jockey/last_page_{}.txt'

    def get_all_jockey_idlist(self, active=2):
        '''
            騎手のIDリストを取得する。

            param:
                active (int): 騎手の状態を指定します。
                                    0は引退
                                    1は現役
                                    2はすべて

            return:
                list: 騎手のIDリスト。
        '''
        try:
            # jockey_id_list_fileディレクトリが一つ以上存在するか確認
            dir = os.path.dirname(self.jockey_id_list_file)
            if len(os.listdir(dir)) == 0:
                # ディレクトリが存在しない場合はscrap_all_jockey_idlistを実行
                self.scrape_all_jockey_idlist(update=True)

            # jockey_id_list_fileディレクトリ内の一番最新の日付のファイル名を取得
            latest_date = os.path.splitext(
                os.path.basename(max(os.listdir(dir))))[0]

            # csvファイルを開きjockey_idをリストで取得する
            df = pd.read_csv(self.jockey_id_list_file.format(latest_date))
            jockey_id_list = df['jockey_id'].tolist()

        except Exception as e:
            print(f'エラーが発生しました。{e}')
            return None
        return jockey_id_list

    def get_jockey_data(self, jockey_id, scraping=True):
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
        name = name_div.h1.get_text(strip=True).replace(
            ' ', '').replace('.', '. ')
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
                row_data['1着'] = row.find('a', href=lambda x: x and 'mode=r1' in x).text if row.find(
                    'a', href=lambda x: x and 'mode=r1' in x) else None
                row_data['2着'] = row.find('a', href=lambda x: x and 'mode=r2' in x).text if row.find(
                    'a', href=lambda x: x and 'mode=r2' in x) else None
                row_data['3着'] = row.find('a', href=lambda x: x and 'mode=r3' in x).text if row.find(
                    'a', href=lambda x: x and 'mode=r3' in x) else None
                row_data['着外'] = row.find('a', href=lambda x: x and 'mode=r4' in x).text if row.find(
                    'a', href=lambda x: x and 'mode=r4' in x) else None
                break  # 初回のみ処理を行う

        return row_data, jockey_name

    def scrape_jockey_idlist(self, active=1, update=False):
        '''
        騎手のIDリストを取得する。

        Parameters:
            active (int): 騎手の状態を指定します。0は引退、1は現役です。
            update (bool): データを更新する場合はTrueを指定します。

        Returns:
            list: 騎手のIDと名前のリスト。

        '''
        # もし前回の処理が中断していた場合は続きから処理を行う
        if os.path.exists(self.last_page_file.format(active)) and not update:
            with open(self.last_page_file.format(active)) as f:
                # 前回処理したページのURLを取得
                last_page_url = f.read()
            # 前回処理したページのURLからページ数を取得
            last_page = int(
                re.search(r'page=([0-9]+)', last_page_url).group(1))
            # 現在のページ数を表示
            print(f'前回処理したページ: {last_page}')
        else:
            # 前回処理が中断していない場合は1ページ目から処理を開始
            last_page = 1

        # URLを作成
        url = self.jockey_db_url.format(active, last_page)

        # 処理時間をバーで表示するための設定
        try:
            response = requests.get(url)
            response.encoding = 'euc-jp'  # エンコーディングをeuc-jpに設定
            soup = BeautifulSoup(response.text, 'html.parser')
            pager = soup.find('div', class_='common_pager')
            last_url = pager.find('a', title="最後").get('href')
            max_page = int(re.search(r'page=([0-9]+)', last_url).group(1))
        except Exception as e:
            print(f'最大ページ数を取得中にエラーが発生しました。{e}')
            return False

        with tqdm(total=max_page) as pbar:
            try:
                # 開始時刻を取得
                start_time = pd.Timestamp.now()

                # 保存するファイル名を作成
                list_file = self.jockey_id_list_file.format(
                    pd.Timestamp.now().strftime('%Y%m%d'))

                # 保存ディレクトリが存在しない場合は作成
                if not os.path.exists(os.path.dirname(list_file)):
                    print(f'{os.path.dirname(list_file)}を作成します。')
                    os.makedirs(os.path.dirname(list_file))

                # ファイルが存在しupdateする場合は保管しているリストを削除
                if os.path.exists(list_file) and update:
                    if os.path.exists(list_file):
                        os.remove(list_file)

                # ファイルが存在していない場合はヘッダーを付ける
                if not os.path.exists(list_file):
                    pd.DataFrame(columns=[
                        'jockey_id', 'jockey_name', 'active']).to_csv(list_file, index=False)

                while True:
                    # 開始時刻からの経過時間を取得
                    elapsed_time = pd.Timestamp.now() - start_time
                    # 1秒待機
                    time.sleep(1)
                    # 経過時間が5分を超えた場合は処理を中断
                    if elapsed_time.seconds > 300:
                        raise Exception('処理がタイムアウトしました。')
                    # URLからHTMLを取得
                    try:
                        # タイムアウトを設定
                        response = requests.get(url, timeout=(3.0, 5))
                        response.encoding = 'euc-jp'  # エンコーディングをeuc-jpに設定
                    except Timeout:
                        # ループの処理時間を超えない限りループを続ける
                        print('タイムアウトしました。')
                        continue

                    # HTMLをパース
                    soup = BeautifulSoup(response.text, 'html.parser')

                    # pagerを取得
                    pager = soup.find('div', class_='common_pager')

                    # 次のページへのリンクがある場合はURLを取得
                    if pager.find('a', title='次'):
                        scrape_end = False
                        next_page_url = pager.find(
                            'a', title='次')['href']
                    else:
                        # 次のページへのリンクがない場合はbreak
                        scrape_end = True

                    # 表を取得
                    table = soup.find(
                        'table', class_='nk_tb_common race_table_01')

                    # 表から騎手のIDと名前を取得

                    # リスト内包表記を使わない場合は以下のように書く
                    # 実行速度計測のため
                    jockey_data = []
                    rows = table.find_all('tr')
                    for row in rows:
                        columns = row.find_all('td')
                        if len(columns) > 0:
                            # 騎手のIDをhrefから取得
                            jockey_id = columns[0].find('a').get('href').replace(
                                '/jockey/result/recent/', '').strip('/')
                            # 騎手の名前を取得
                            jockey_name = columns[0].text
                            # 騎手のIDと名前と現役かどうかをタプルにしてリストに追加
                            jockey_data.append(
                                (jockey_id, jockey_name, active))

                    # リスト内包表記を使って書くと以下のようになる
                    # 実行速度計測のためにコメントアウト
                    # 内包表記にしても早くなるどころか遅い
                    # jockey_data = [(columns[0].find('a').get('href').replace('/jockey/result/recent/', '').strip('/'), columns[0].text)
                    #                for row in table.find_all('tr') for columns in [row.find_all('td')] if len(columns) > 0]

                    # データをcsv形式で保存
                    # 存在チェックはwhile前に行う
                    pd.DataFrame(jockey_data).to_csv(
                        list_file, index=False, header=False, mode='a')

                    # バーを更新
                    pbar.update(1)

                    # breakフラグが立っていた場合はループを抜ける
                    if scrape_end:
                        break
                    else:
                        # 次のページのURLを作成
                        url = next_page_url

            except Exception as e:
                print(e)
                print('処理を中断します。')

                # 次のページURLを保管し続きから再開できるようにする
                # ファイルの存在チェックをする
                if os.path.exists(self.last_page_file.format(active)):
                    # ファイルが存在している場合は上書き
                    with open(self.last_page_file.format(active), 'w') as f:
                        f.write(next_page_url)
                else:
                    # ファイルが存在していない場合は新規作成
                    with open(self.last_page_file.format(active), 'x') as f:
                        f.write(next_page_url)

            else:
                # 保管しているページ数を削除
                if os.path.exists(self.last_page_file.format(active)):
                    os.remove(self.last_page_file.format(active))

            finally:
                # 取得したデータを返す
                jockey_data_list = pd.read_csv(list_file)
                return jockey_data_list

    def scrape_all_jockey_idlist(self, update=False):
        '''
            現役、引退両方の騎手のIDリストを取得する。
            return: 成功したらTrue、失敗したらFalseを返す。
        '''
        try:
            # 最初にUpdateを行い、二回目の実行時は追加を行うことでクリーンなファイルとする
            self.scrape_jockey_idlist(active=0, update=update)
            self.scrape_jockey_idlist(active=1)
        except Exception as e:
            print(f'エラーが発生しました。{e}')
            return False
        return True

    def scrape_jockey_list(self):
        # URLを作成
        url = self.base_url

        # URLからHTMLを取得
        response = requests.get(url)
        response.encoding = 'euc-jp'

        # レスポンスのステータスコードが200以外の場合に例外を発生させる
        response.raise_for_status()

        # HTMLをパース
        soup = BeautifulSoup(response.text, 'html.parser')

        # テーブル行を見つける
        rows = soup.find_all('tr', class_='')

    def scrape_jockey_data(self, jockey_id, page=1):

        # URLを作成
        url = f"https://db.netkeiba.com//?pid=jockey_select&id={jockey_id}&year=0000&mode=r4&page={page}"

        # URLからHTMLを取得
        response = requests.get(url)

        # レスポンスのエンコーディングを確認
        encoding = response.encoding if 'charset' in response.headers.get(
            'content-type', '').lower() else None
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
                page_data = self.scrape_jockey_data(jockey_id, page)
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
