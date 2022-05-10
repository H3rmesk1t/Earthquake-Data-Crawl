# -*- coding: utf-8 -*-

import os
import csv
import json
import requests
import argparse

id = 1
data = {}
flag = True
select = 'latest_7_days'
save_file_path = 'latest_7_days'

# Resource Links
class URL:
    def __init__(self, id):
        self.id = str(id)

    def latest_24_hours(self):
        """
        Address for the last 24 hours of earthquake data.
        :return:
        """
        url = 'http://www.ceic.ac.cn/ajax/speedsearch?num=1&&page={}'.format(self.id)
        return url

    def latest_48_hours(self):
        """
        Address for the last 48 hours of earthquake data
        :return:
        """
        url = 'http://www.ceic.ac.cn/ajax/speedsearch?num=2&&page={}'.format(self.id)
        return url

    def latest_7_days(self):
        """
        Address for the last 7 days of earthquake data
        :return:
        """
        url = 'http://www.ceic.ac.cn/ajax/speedsearch?num=3&&page={}'.format(self.id)
        return url

    def latest_30_days(self):
        """
        Address for the last 30 days of earthquake data
        :return:
        """
        url = 'http://www.ceic.ac.cn/ajax/speedsearch?num=4&&page={}'.format(self.id)
        return url

    def latest_1_year(self):
        """
        Address for the last 1 year of earthquake data
        :return:
        """
        url = 'http://www.ceic.ac.cn/ajax/speedsearch?num=5&&page={}'.format(self.id)
        return url


def select_data_source():
    """
    Select the source of earthquake data:
        latest_24_hours
        latest_48_hours
        latest_7_days
        latest_30_days
        latest_1_year
    :return:
    """
    global select
    url_class = URL(id)
    if select == 'latest_24_hours':
        return url_class.latest_24_hours()
    elif select == 'latest_48_hours':
        return url_class.latest_48_hours()
    elif select == 'latest_7_days':
        return url_class.latest_7_days()
    elif select == 'latest_30_days':
        return url_class.latest_30_days()
    elif select == 'latest_1_year':
        return url_class.latest_1_year()


def get_data():
    """
    Crawling data from http://www.ceic.ac.cn/
    :return:
    """
    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/17.17134"
    }
    response = requests.get(url=select_data_source(), headers=headers)
    if response.status_code == 200:
        return response.content.decode('utf-8')


def parse_data(earthquake_data):
    """
    Parsing of the acquired content
    :return:
    """
    earthquake_data = earthquake_data['shuju']
    for item in earthquake_data:
        yield {
            'CATA_ID': item['CATA_ID'],
            'M': item['M'],
            'O_TIME': item['O_TIME'],
            'EPI_LAT': item['EPI_LAT'],
            'EPI_LON': item['EPI_LON'],
            'EPI_DEPTH': item['EPI_DEPTH'],
            'LOCATION_C': item['LOCATION_C'],
            'link': 'https://news.ceic.ac.cn/{}.html'.format(item['CATA_ID'].split('.')[0])
        }


def save_csv(item):
    """
    Save processed data
    :return:
    """
    try:
        with open(select, 'a', encoding='utf_8_sig', newline='') as f:
            fieldnames = ['CATA_ID', 'M', 'O_TIME', 'EPI_LAT', 'EPI_LON', 'EPI_DEPTH', 'LOCATION_C', 'link']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writerow(item)
    except IOError:
        exit(0)


def judge_file():
    """
    Ensure that the file is re-updated at each runtime
    :return:
    """
    if os.path.isfile(save_file_path):
        os.remove(save_file_path)


def command():
    """
    Run the code as command line
    :return:
    """
    parser = argparse.ArgumentParser(prog='python main.py')
    parser.add_argument('select', help='latest_24_hours, latest_48_hours, latest_7_days, latest_30_days, latest_1_year', type=str)
    parser.add_argument('save_file_path', help='Please enter the path to save the file', type=str)
    args = parser.parse_args()
    return args.data_source, args.save_file_path


def main():
    """
    Logical function
    :return:
    """
    global id
    global flag
    global data
    # select, save_file_path = command()

    judge_file()
    while flag:
        earthquake_datas = get_data()[1:-1][:get_data()[1:-1].find(',"page"')] + '}'
        # Determine if the data has been fetched
        if data != earthquake_datas:
            data = earthquake_datas
            id += 1
            earthquake_datas = json.loads(earthquake_datas)
            for earthquake_data in parse_data(earthquake_datas):
                save_csv(earthquake_data)
        else:
            flag = False


if __name__ == '__main__':
    main()