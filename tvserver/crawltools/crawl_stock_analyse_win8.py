#!/usr/bin/env python3
# -*- coding:utf-8 -*-

'''
created on 2015-07-21

@author:caidongfang

说明：邮件测试
'''

import datetime
import smtplib
import requests
from bs4 import BeautifulSoup


class StockSpider(object):

    def __init__(self):
        self.stock_dict = dict()

    def crawl_data(self, url):
        res = requests.get(url)
        soup = BeautifulSoup(res.content)
        table_data_list = soup.find(
            "table",
            class_="table_bg001 border_box limit_sale").find_all('tr')[1:]
        data_list = [i.find_all('td') for i in table_data_list]
        trade_data_list = [[j.text for j in i] for i in data_list]
        return trade_data_list

    def crawl_stock_name(self, code, crawl_url):
        res = requests.get(crawl_url)
        soup = BeautifulSoup(res.content)
        name = soup.find("h1", class_="name").find('a').text
        self.stock_dict.update({code: name})

    def crawl_stock_data(self, code, crawl_url):
        self.crawl_stock_name(code, crawl_url)
        now = datetime.datetime.now().strftime('%Y-%m')
        year, month = now.split('-')
        year, month = int(year), int(month)
        month_to_season_dict = {1: 1, 2: 1, 3: 1, 4: 2,
                                5: 2, 6: 2, 7: 3, 8: 3,
                                9: 3, 10: 4, 11: 4, 12: 4}
        season = month_to_season_dict[int(month)]
        season_list = list()
        for i in range(4):
            if season > 0:
                season_list.append((year, season))
                season -= 1
            else:
                year -= 1
                season = 4
                season_list.append((year, season))
                season -= 1
        source_data_list = list()
        for year, season in season_list:
            # print year, season
            source_data_list += self.crawl_data(
                crawl_url + "?year=%s&season=%s" % (year, season))
        source_data_list.sort()
        return source_data_list

    def cal_volume_ratio(self, source_data_dict):
        volume_ratio_dict = dict()
        keys = source_data_dict.keys()
        for k in keys:
            volume_ratio_dict[k] = list()
            for i in range(1, 7):
                day_stock = -i
                today_amount = int(float(
                    source_data_dict[k][day_stock][-3].replace(',', '')))
                avg_amount = sum([int(float(
                    n[-3].replace(',', '')))
                    for n in source_data_dict[k][(day_stock-5):(day_stock)]])/5
                volume_ratio_dict[k].append((
                    source_data_dict[k][day_stock][0],
                    float(today_amount)/float(avg_amount)))
            volume_ratio_dict[k].sort()
        return volume_ratio_dict

    def stock_profitAndloss(self, source_data_dict):
        profitAndloss = dict()
        keys = source_data_dict.keys()
        for k in keys:
            profitAndloss[k] = list()
            for i in range(1, 7):
                day_stock = -i
                today_price = float(
                    source_data_dict[k][day_stock][4].replace(',', ''))
                end_day_stock = day_stock + 1
                if end_day_stock == 0:
                    ma34 = sum([float(n[4].replace(',', ''))
                                for n in source_data_dict[k][
                                    day_stock-33:]])/34
                    ma144 = sum([float(n[4].replace(',', ''))
                                 for n in source_data_dict[k][
                                     day_stock-143:]])/144
                else:
                    ma34 = sum([float(
                        n[4].replace(',', ''))
                        for n in source_data_dict[k][
                            day_stock-33:end_day_stock]])/34
                    ma144 = sum([float(
                        n[4].replace(',', ''))
                        for n in source_data_dict[k][
                            day_stock-143:end_day_stock]])/144
                profitAndloss_34 = (today_price-ma34)/ma34
                profitAndloss_144 = (today_price-ma144)/ma144
                profitAndloss_avg = (profitAndloss_34+profitAndloss_144)/2
                profitAndloss[k].append((source_data_dict[k][day_stock][0],
                                         profitAndloss_avg))
            profitAndloss[k].sort()
        return profitAndloss

    def long_short_trend(self, source_data_dict):
        ls_trend = dict()
        keys = source_data_dict.keys()
        for k in keys:
            ls_trend[k] = list()
            for i in range(1, 8):
                day_stock = -i
                today_price = float(
                    source_data_dict[k][day_stock][4].replace(',', ''))
                end_day_stock = day_stock + 1
                if end_day_stock == 0:
                    ma3 = sum([float(
                        n[4].replace(',', ''))
                               for n in source_data_dict[k][day_stock-2:]])/3
                    ma5 = sum([float(
                        n[4].replace(',', ''))
                               for n in source_data_dict[k][day_stock-4:]])/5
                    ma8 = sum([float(
                        n[4].replace(',', ''))
                               for n in source_data_dict[k][day_stock-7:]])/8
                else:
                    ma3 = sum([float(
                        n[4].replace(',', ''))
                               for n in source_data_dict[k][
                                   day_stock-2:end_day_stock]])/3
                    ma5 = sum([float(
                        n[4].replace(',', ''))
                               for n in source_data_dict[k][
                                   day_stock-4:end_day_stock]])/5
                    ma8 = sum([float(
                        n[4].replace(',', ''))
                               for n in source_data_dict[k][
                                   day_stock-7:end_day_stock]])/8
                ls_trend[k].append([
                    source_data_dict[k][day_stock][0],
                    today_price, ma3, ma5, ma8])
            ls_trend[k].sort()

        for k, v in ls_trend.items():
            for i in range(-1, -7, -1):
                for j in range(1, 5):
                    if v[i][j] > v[i-1][j]:
                        v[i][j] = float(1)
                    elif v[i][j] < v[i-1][j]:
                        v[i][j] = float(-1)
                    else:
                        v[i][j] = float(0)
            v = v[1:]
            for stock, t in enumerate(v):
                _temp = list()
                _temp.append(t[0])
                _temp.append(sum(t[1:]))
                v[stock] = _temp
            ls_trend[k] = v
        return ls_trend


def create_stock_volume_ratio_content(volume_ratio_data, stock_dict):
    volume_ratio_content = list()
    pjlb_content = ''
    template = "<a href='http://doctor.10jqka.com.cn/%s/' target='view_window'>%s</a>"
    for k, v in volume_ratio_data.items():
        _content = stock_dict[k] + u'量比' + '&nbsp;'*5
        _content += '  $  '.join(['%s: %.2f' % (i, j) for i, j in v])
        link_url = template % (k, stock_dict[k])
        _content += '&nbsp;' * 8 + link_url
        volume_ratio_content.append(_content)
    return "<br><br>".join(volume_ratio_content)


def create_stock_profitAndloss_content(stock_profitAndloss, stock_dict):
    profitAndloss_content = list()
    # plyk_content = ''
    for k, v in stock_profitAndloss.items():
        _content = stock_dict[k] + u'盈亏' + '&nbsp;'*5
        _content += '  $  '.join(['%s: %.2f%s' % (i, j*100, '%')
                                  for i, j in v])
        profitAndloss_content.append(_content)
    return "<br><br>".join(profitAndloss_content)


def create_stock_lstrend_content(ls_trend, stock_dict):
    ls_trend_content = list()
    zhdk_content = ''

    def create_content(num, key):
        num = int(num)
        per = float(num)/4
        if num > 0:
            return '%.2f%s' % (per*100, '%') + ',' + u'↑净多↑'
        elif num < 0:
            return '%.2f%s' % (per*100, '%') + ',' + u'↓净空↓'
        else:
            return '%.2f%s' % (per*100, '%') + ',' + u'＝平＝'
    for k, v in ls_trend.items():
        _content = stock_dict[k] + u'多空' + '&nbsp;'*5
        _content += '  $  '.join(['%s: %s' % (i, create_content(j, k))
                                  for i, j in v])
        ls_trend_content.append(_content)
    return "<br><br>".join(ls_trend_content)

if __name__ == '__main__':
    stockspider = StockSpider()
    source_data_dict = dict()
    for i in ['600739', '300181']:
        source_data_dict[i] = stockspider.crawl_stock_data(i,
            "http://quotes.money.163.com/trade/lsjysj_%s.html" % i)
    volume_ratio_data = stockspider.cal_volume_ratio(source_data_dict)
    volume_ratio_mail_content = create_stock_volume_ratio_content(volume_ratio_data, stockspider.stock_dict)
    print volume_ratio_mail_content.encode('utf8')
    stock_profitAndloss = stockspider.stock_profitAndloss(source_data_dict)
    profitAndloss_content = create_stock_profitAndloss_content(stock_profitAndloss, stockspider.stock_dict)
    print profitAndloss_content.encode('utf8')
    ls_trend = stockspider.long_short_trend(source_data_dict)
    ls_trend_content = create_stock_lstrend_content(ls_trend, stockspider.stock_dict)
    print ls_trend_content.encode('utf8')
