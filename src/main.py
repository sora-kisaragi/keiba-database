from scraper.jockey_scraper import JockeyScraper
from scraper.horce_scraper import HorseScraper
import pandas as pd
import argparse


def jockey_main(jockey_id, scraping, skip_scraping):
    scraper = JockeyScraper()
    # print(f'騎手ID: {jockey_id}')
    # print(f'スクレイピングフラグ: {scraping}')
    # data = scraper.get_jockey_data(jockey_id, scraping=scraping)
    # # keyをソートしてdataを表示
    # sorted_data = sorted(data.items(), key=lambda x: x[0])
    # for key, value in sorted_data:
    #     print(f'{key}着', f'{value}回')
    # # valueの合計を計算して表示
    # total = sum(data.values())
    # print('total:', total)

    # new_data = combine_values(dict(sorted_data))

    # # new_dataの着順の平均を計算して表示
    # x = 0
    # for key, value in new_data.items():
    #     x += int(key) * int(value)
    # print('騎手名 : ', scraper.jockey_name)
    # print('平均順位 : ', x / total)
    print('騎手IDをリストで取得を開始する')
    scraper.scrape_all_jockey_idlist(update=True)


def horse_main(horse_id, scraping, skip_scraping):
    scraper = HorseScraper()
    print(f'馬ID: {horse_id}')
    print(f'スクレイピングフラグ: {scraping}')
    print(f'スクレイピングスキップフラグ: {skip_scraping}')
    data = scraper.get_horse_data(horse_id, scraping=scraping)

    # # プロフィールデータを表示
    # print('プロフィールデータ')
    # print(data['profile'])

    # # 血統データを表示
    # print('血統データ')
    # print(data['bloodline'])

    # # 戦績データを表示
    # print('戦績データ')
    # print(data['race_results'])

    # 馬ID 馬名 騎手名 着順を表示
    print(f'馬ID: {horse_id}')
    print(f'馬名: {data["profile"].iloc[0]["馬名"]}')
    print(data['race_results'][['騎手', '着 順']])


def combine_values(d):
    keys_to_remove = []
    for key in d:
        if isinstance(key, str) and any(c.isalpha() for c in key):
            digit_key = ''.join(filter(str.isdigit, key))
            if digit_key in d:
                d[digit_key] += d[key]
            keys_to_remove.append(key)
    for key in keys_to_remove:
        del d[key]
    return d


def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


# コマンドライン引数から騎手IDを取得
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--jockey_id', type=str, default="00666",
                        help='騎手IDを入力してください default: 00666 武豊')
    parser.add_argument('--horse_id', type=str, default="2017105319",
                        help='馬IDを入力してください default: 2017105319 エフフォーリア')
    parser.add_argument('--no_scraping', action='store_false',
                        help='スクレイピングを行わない場合に指定 default: True')
    parser.add_argument('--skip_scraping', action='store_true',
                        help='データが存在する場合スクレイピングをスキップする場合に指定 default: False')

    args = parser.parse_args()

    jockey_main(args.jockey_id, args.no_scraping, args.skip_scraping)
    # horse_main(args.horse_id, args.no_scraping, args.skip_scraping)
