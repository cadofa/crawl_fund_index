# -*- coding: utf8 -*-
import re
import smtplib
import requests
import json
import argparse
import numpy
from email.mime.text import MIMEText
from email.header import Header
from bs4 import BeautifulSoup

code_name_list = ['F003N_FUND33', 'F008', 'F009', 'F011', 'F015N_FUND33', 'F012']
weights_list =   [ 1,              0.9,    0.8,    0.7,    0.6,            0.5]

def sort_dict(response_dict, key_to_sort):
    sorted_dict= sorted(response_dict.items(), key=lambda d:d[1][key_to_sort], reverse = True)
    rank = 1
    for s in sorted_dict:
        try:
            float(s[1][key_to_sort])
            response_dict[s[0]][key_to_sort] = rank
            rank += 1
        except ValueError:
            continue

    return response_dict


def handle_fund_name(response_dict):
    for s in response_dict:
        ss = response_dict[s]['name'].encode('utf8')
        x = json.loads('{"foo":"%s"}' % ss)
        response_dict[s]['name'] = x['foo']

    return response_dict

def crawl_data(url):
    global code_name_list

    rs = requests.get(url)
    print "***************fund text******************"
    response_str = rs.text[2:-1].replace("null", "'null'")
    response_dict = eval("{}".format(response_str))
    response_dict = response_dict['data']['data']
    for k, v in response_dict.items():
        for key, value in v.items():
            if key == "code":
                continue
            try:
                v[key] = float(value)
            except ValueError:
                continue


    response_dict = handle_fund_name(response_dict)
    for k in code_name_list:
        response_dict = sort_dict(response_dict, k)

    return response_dict


def Computing_rankings(response_dict):
    global code_name_list
    fund_data = list()
    for k, v in response_dict.items():
        try:
            ranking_list = [int(v[c]) for c in code_name_list]
            ranking_list = [r*w for r, w in zip(ranking_list, weights_list)]
        except ValueError:
            continue
        average = int(round(numpy.mean(ranking_list)))
        variance = int(round(numpy.var(ranking_list)))
        fund_data.append([v['code'] + "  " + v['name'], average, variance])

    return fund_data


def create_mail_content(fund_data, type_name):
    gt_best_fund_set = set()

    average_content_title = type_name + u'排名靠前基金:\n'
    fund_data.sort(key=lambda x: x[1])
    best_average_fund_set = set()
    content_list = list()
    for f in fund_data[:38]:
        content_list.append(f[0])
        if u"国泰" in f[0]:
            gt_best_fund_set.add("  ".join([f[0], str(f[1]), str(f[2])]))
        best_average_fund_set.add("  ".join([f[0], str(f[1]), str(f[2])]))
    average_content = average_content_title + '\n'.join(content_list)

    variance_content_title = type_name + u'方差靠前基金:\n'
    fund_data.sort(key=lambda x: x[2])
    best_variance_fund_set = set()
    content_list = list()
    for f in fund_data[:38]:
        content_list.append(f[0])
        if u"国泰" in f[0]:
            gt_best_fund_set.add("  ".join([f[0], str(f[1]), str(f[2])]))
        best_variance_fund_set.add("  ".join([f[0], str(f[1]), str(f[2])]))
    variance_content = variance_content_title + '\n'.join(content_list)

    best_fund_set = best_average_fund_set.intersection(best_variance_fund_set)
    best_fund_set.update(gt_best_fund_set)
    best_fund_title = type_name + 'Best Fund:\n'
    best_fund_list = list(best_fund_set)
    best_fund_list.sort(key=lambda x: int(x.split()[3]))
    best_content = best_fund_title + '\n'.join(best_fund_list)
    return '\n\n\n'.join([average_content,
                          variance_content,
                          best_content])


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("type",
                        choices=['mixed', 'stock', 'bond', 'guaranteed'])
    args = parser.parse_args()
    type_ = args.type
    if type_:
        if type_ == 'mixed':
            type_name = u'混合型'
            url = ('http://fund.ijijin.cn/data/Net/info/'
                   'hhx_F008_desc_0_0_1_9999_0_0_0_jsonp_g.html')
        if type_ == 'stock':
            type_name = u'股票型'
            url = ('http://fund.ijijin.cn/data/Net/info/'
                   'gpx_F008_desc_0_0_1_9999_0_0_0_jsonp_g.html')
        if type_ == 'bond':
            type_name = u'债券型'
            url = ('http://fund.ijijin.cn/data/Net/info/'
                   'zqx_F008_desc_0_0_1_9999_0_0_0_jsonp_g.html')
        if type_ == 'guaranteed':
            type_name = u'保本型'
            url = ('http://fund.ijijin.cn/data/Net/info/'
                   'bbx_F008_desc_0_0_1_9999_0_0_0_jsonp_g.html')
        response_dict = crawl_data(url)
        fund_data = Computing_rankings(response_dict)
        mail_content = create_mail_content(fund_data, type_name)
        print mail_content

