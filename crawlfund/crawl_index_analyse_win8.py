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
import argparse
from bs4 import BeautifulSoup


class IndexSpider(object):

    def crawl_data(self, url):
        res = requests.get(url)
        soup = BeautifulSoup(res.content)
        table_data_list = soup.find(
            "table",
            class_="table_bg001 border_box limit_sale").find_all('tr')[1:]
        data_list = [i.find_all('td') for i in table_data_list]
        trade_data_list = [[j.text for j in i] for i in data_list]
        return trade_data_list

    def crawl_index_data(self, crawl_url):
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
                day_index = -i
                today_amount = int(float(
                    source_data_dict[k][day_index][-1].replace(',', '')))
                avg_amount = sum([int(float(
                    n[-1].replace(',', '')))
                    for n in source_data_dict[k][(day_index-5):(day_index)]])/5
                volume_ratio_dict[k].append((
                    source_data_dict[k][day_index][0],
                    float(today_amount)/float(avg_amount)))
            volume_ratio_dict[k].sort()
        volume_ratio_dict['888888'] = map(
            lambda x, y, z, a, b, c: (x[0],
                                      (x[1]+y[1]+z[1]+a[1]+b[1]+c[1])/6),
            volume_ratio_dict['000001'], volume_ratio_dict['399106'],
            volume_ratio_dict['399300'], volume_ratio_dict['399101'],
            volume_ratio_dict['399102'], volume_ratio_dict['399905'])
        return volume_ratio_dict

    def index_profitAndloss(self, source_data_dict):
        profitAndloss = dict()
        keys = source_data_dict.keys()
        for k in keys:
            profitAndloss[k] = list()
            for i in range(1, 7):
                day_index = -i
                today_price = float(
                    source_data_dict[k][day_index][4].replace(',', ''))
                end_day_index = day_index + 1
                if end_day_index == 0:
                    ma34 = sum([float(n[4].replace(',', ''))
                                for n in source_data_dict[k][
                                    day_index-33:]])/34
                    ma144 = sum([float(n[4].replace(',', ''))
                                 for n in source_data_dict[k][
                                     day_index-143:]])/144
                else:
                    ma34 = sum([float(
                        n[4].replace(',', ''))
                        for n in source_data_dict[k][
                            day_index-33:end_day_index]])/34
                    ma144 = sum([float(
                        n[4].replace(',', ''))
                        for n in source_data_dict[k][
                            day_index-143:end_day_index]])/144
                profitAndloss_34 = (today_price-ma34)/ma34
                profitAndloss_144 = (today_price-ma144)/ma144
                profitAndloss_avg = (profitAndloss_34+profitAndloss_144)/2
                profitAndloss[k].append((source_data_dict[k][day_index][0],
                                         profitAndloss_avg))
            profitAndloss[k].sort()
        profitAndloss['888888'] = map(
            lambda x, y, z, a, b, c: (x[0], (x[1]+y[1]+z[1]+a[1]+b[1]+c[1])/6),
            profitAndloss['000001'], profitAndloss['399106'],
            profitAndloss['399300'], profitAndloss['399101'],
            profitAndloss['399102'], profitAndloss['399905'])
        return profitAndloss

    def long_short_trend(self, source_data_dict):
        ls_trend = dict()
        keys = source_data_dict.keys()
        for k in keys:
            ls_trend[k] = list()
            for i in range(1, 8):
                day_index = -i
                today_price = float(
                    source_data_dict[k][day_index][4].replace(',', ''))
                end_day_index = day_index + 1
                if end_day_index == 0:
                    ma3 = sum([float(
                        n[4].replace(',', ''))
                               for n in source_data_dict[k][day_index-2:]])/3
                    ma5 = sum([float(
                        n[4].replace(',', ''))
                               for n in source_data_dict[k][day_index-4:]])/5
                    ma8 = sum([float(
                        n[4].replace(',', ''))
                               for n in source_data_dict[k][day_index-7:]])/8
                else:
                    ma3 = sum([float(
                        n[4].replace(',', ''))
                               for n in source_data_dict[k][
                                   day_index-2:end_day_index]])/3
                    ma5 = sum([float(
                        n[4].replace(',', ''))
                               for n in source_data_dict[k][
                                   day_index-4:end_day_index]])/5
                    ma8 = sum([float(
                        n[4].replace(',', ''))
                               for n in source_data_dict[k][
                                   day_index-7:end_day_index]])/8
                ls_trend[k].append([
                    source_data_dict[k][day_index][0],
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
            for index, t in enumerate(v):
                _temp = list()
                _temp.append(t[0])
                _temp.append(sum(t[1:]))
                v[index] = _temp
            ls_trend[k] = v
        ls_trend['888888'] = map(
            lambda x, y, z, a, b, c: [x[0],
                                      (x[1]+y[1]+z[1]+a[1]+b[1]+c[1])],
            ls_trend['000001'], ls_trend['399106'],
            ls_trend['399300'], ls_trend['399101'],
            ls_trend['399102'], ls_trend['399905'])
        return ls_trend


def create_volume_ratio_content(volume_ratio_data):
    index_dict = {'000001': u'上证指数',
                  '399106': u'深圳成指',
                  '399300': u' 沪深300',
                  '399101': u'中小板指',
                  '399102': u'创业板指',
                  '399905': u' 中证500',
                  '888888': u'平均量比'}
    volume_ratio_content = list()
    pjlb_content = ''
    for k, v in volume_ratio_data.items():
        _content = index_dict[k] + '   '
        _content += '  $  '.join(['%s: %.2f' % (i, j) for i, j in v])
        if k == '888888':
            pjlb_content = _content
            continue
        volume_ratio_content.append(_content)
    volume_ratio_content.append(pjlb_content)
    return "\r\n\r\n".join(volume_ratio_content)


def create_profitAndloss_content(index_profitAndloss):
    index_dict = {'000001': u'上证盈亏', '399106': u'深圳盈亏',
                  '399300': u'沪深盈亏', '399101': u'中小盈亏',
                  '399102': u'创业盈亏', '399905': u'中证盈亏',
                  '888888': u'平均盈亏'}
    profitAndloss_content = list()
    # plyk_content = ''
    for k, v in index_profitAndloss.items():
        _content = index_dict[k] + '   '
        _content += '  $  '.join(['%s: %.2f%s' % (i, j*100, '%')
                                  for i, j in v])
        if k == '888888':
            pjyk_content = _content
            continue
        profitAndloss_content.append(_content)
    profitAndloss_content.append(pjyk_content)
    return "\r\n\r\n".join(profitAndloss_content)


def create_lstrend_content(ls_trend):
    index_dict = {'000001': u'上证多空', '399106': u'深圳多空',
                  '399300': u'沪深多空', '399101': u'中小多空',
                  '399102': u'创业多空', '399905': u'中证多空',
                  '888888': u'综合多空'}
    ls_trend_content = list()
    zhdk_content = ''

    def create_content(num, key):
        num = int(num)
        if key != '888888':
            per = float(num)/4
        else:
            per = float(num)/24
        if num > 0:
            return '%.2f%s' % (per*100, '%') + ',' + u'净多'
        elif num < 0:
            return '%.2f%s' % (per*100, '%') + ',' + u'净空'
        else:
            return '%.2f%s' % (per*100, '%') + ',' + u'净平'
    for k, v in ls_trend.items():
        _content = index_dict[k] + '   '
        _content += '  $  '.join(['%s: %s' % (i, create_content(j, k))
                                  for i, j in v])
        if k == '888888':
            zhdk_content = _content
            continue
        ls_trend_content.append(_content)
    ls_trend_content.append(zhdk_content)
    return "\r\n\r\n".join(ls_trend_content)

if __name__ == '__main__':
    indexspider = IndexSpider()
    source_data_dict = dict()
    for i in ['000001', '399106', '399300', '399101', '399102', '399905']:
        source_data_dict[i] = indexspider.crawl_index_data(
            "http://quotes.money.163.com/trade/lsjysj_zhishu_%s.html" % i)
    volume_ratio_data = indexspider.cal_volume_ratio(source_data_dict)
    volume_ratio_mail_content = create_volume_ratio_content(volume_ratio_data)
    # print volume_ratio_mail_content.encode('utf8')
    index_profitAndloss = indexspider.index_profitAndloss(source_data_dict)
    profitAndloss_content = create_profitAndloss_content(index_profitAndloss)
    print profitAndloss_content.encode('utf8')
    ls_trend = indexspider.long_short_trend(source_data_dict)
    ls_trend_content = create_lstrend_content(ls_trend)
    # print ls_trend_content.encode('utf8')
