# 競馬データベース 作成プログラム

このプロジェクトは競馬予想用のデータを収集してデータベース化するプロジェクトです。
WebAPIで自作データを自作アプリからのみ呼び出すことを想定しています。

## セットアップ

1. リポジトリをクローンします。
2. pipを使用して必要なPythonパッケージをインストールします：

```bash
pip install -r requirements.txt
```

## 使用方法

コマンドラインからメインスクリプトを実行します：

```bash
python src/main.py
```

### オプション引数

* --jockey_id [JOCKEY_ID] : 騎手IDを入力してください
  * default: 00666 武豊
* --horse_id [HORSE_ID] : 馬IDを入力してください
  * default: 2017105319 エフフォーリア
* --no_scraping : スクレイピングを行わない場合に指定
  * default: True
* --skip_scraping : データが存在する場合スクレイピングをスキップする場合に指定
  * default: False

例えば、ヘルプメッセージを表示するには以下のようにします：

```bash
python src/main.py --help
```

スクレイプしたデータはdataディレクトリに保存されます。

## テスト

ユニットテストを実行するには、以下のコマンドを使用します：

```bash
python -m unittest discover tests
```

## 貢献

私たちの行動規範や、プルリクエストを送るプロセスの詳細については、`CONTRIBUTING.md`をご覧ください。

## ライセンス

このプロジェクトはMITライセンスの下でライセンスされています - 詳細は`LICENSE.md`ファイルをご覧ください。
