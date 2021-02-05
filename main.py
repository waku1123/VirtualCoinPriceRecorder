#!/usr/bin/python
import csv
import datetime
import glob
import pathlib
import re
import requests
from requests import Response
import os
from typing import Dict, List

# Output Directry
directry: str = "./output/"
# ENDPOINT URL
endpoint: str = "https://api.bitflyer.jp/v1/"
# PUBLIC API METHODS
methods: Dict = {
    "markets": "getmarkets",  # マーケットの一覧
    "board": "getboard",  # 板情報
    "ticker": "getticker",  # Ticker
    "executions": "getexecutions",  # 約定履歴
    "health": "gethealth",  # 取引所の状態
    "chat": "getchats",  # チャット
}


# marketsからproduct_codeを取得
def getproduct_codes(endpoint_: str, methods_: Dict) -> List:
    # PRODUCTS
    r1 = requests.get(endpoint_ + methods_["markets"])
    tmplist: Dict = r1.json()
    outlist: List = list()
    for dict in tmplist:
        key = list(dict.keys())
        outlist.append(dict.get(key[0]))
    return outlist


# csv書き込み
def write_csv(year_month: str, datestr: str, timestr: str, price: float) -> None:
    file_change_by_every_month(year_month_=year_month, directry_name_=directry)
    latest_file: str = getlatest_file_name(year_month=year_month, directry_name=directry)
    # ファイル追記処理
    with open(directry + latest_file, "a") as csv_file:
        writer = csv.writer(csv_file, lineterminator="\n")
        writer.writerow([datestr, timestr, price])


# 出力ディレクトリ内の最新ファイル名を返す
def getlatest_file_name(year_month: str, directry_name: str) -> str:
    inner_dir = os.listdir(directry_name)
    if len(inner_dir) < 1:
        return year_month + ".csv"
    else:
        return get_last_element_og_list(inner_dir)


def get_last_element_og_list(list_: List) -> str:
    # ファイル名から数字部分（6桁）を取り出してintにキャストしてリストにする
    tmplist = [int(re.search("[0-9]{6}", str(elem)).group()) for elem in list_]
    tmplist.sort()  # 昇順ソート
    return str(tmplist[-1]) + ".csv"  # 最後の要素をファイル名に復元して文字列を返却する


# csvファイル作成
def make_csv_file(year_month_: str, directry_: str) -> None:
    with open(directry_ + year_month_ + ".csv", "w") as csv_file:
        writer = csv.writer(csv_file, lineterminator="\n")
        writer.writerow(["Date", "Time", "Price"])


# 月単位でファイルを新規作成する。
def file_change_by_every_month(year_month_: str, directry_name_: str) -> None:
    # file_list: List[str] = os.listdir(directry_name_)
    file_list = list(pathlib.Path(directry_name_).glob("*[!gitkeep]"))
    if len(file_list) < 1:
        make_csv_file(year_month_=year_month_, directry_=directry_name_)
        return
    else:
        file_name = get_last_element_og_list(list_=file_list)
        file_yyyymm: int = int(file_name[0:6])
        today_yyyymm: int = int(year_month_[0:6])
        if file_yyyymm < today_yyyymm:
            make_csv_file(year_month_=year_month_, directry_=directry_name_)
    return


def main():
    # PRODUCTS
    product_codes_list: List = getproduct_codes(endpoint_=endpoint, methods_=methods)

    # リクエスト。Responseオブジェクトを生成
    r: Response = requests.get(
        endpoint + methods["board"] + "?product_code=" + product_codes_list[0]
    )

    # ステータスコードの取得
    status_code: int = r.status_code

    # ステータスが成功ならデータをcsvに書き込む
    if status_code == 200:
        # jsonデータでもあるレスポンスをデコードして辞書型に変換する
        r_dict: Dict = r.json()
        # 中央値をfloatで取り出す　例）'mid_price' :'718450.0' → 718450.0
        mid_price: float = float(r_dict["mid_price"])

        # 現在日時の取得
        now: datetime.datetime = datetime.datetime.now()
        year_month: str = now.strftime("%Y%m")
        # 日付文字列フォーマット  20181018_20_15_34
        formated_date: str = now.strftime("%Y%m%d")
        formated_time: str = now.strftime("%H:%M:%S")
        # csv出力
        write_csv(
            year_month=year_month, datestr=formated_date, timestr=formated_time, price=mid_price
        )


if __name__ == "__main__":
    main()
