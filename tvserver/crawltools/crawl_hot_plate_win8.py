# -*- coding:utf-8 -*-

'''
created on 2015-07-21

@author:cuixiaoming

说明：邮件测试
'''

import smtplib
import requests
import argparse
import json
import time
from selenium import webdriver
from bs4 import BeautifulSoup


class HotplateSpider(object):

    def __init__(self):
        self.driver = webdriver.Chrome()

    def crawl_hot_concept_plate_data(self):
        self.driver.get('http://q.10jqka.com.cn/gn/')
        soup = BeautifulSoup(self.driver.page_source)
        detail_item = soup.find('input', {'id': 'gnSection'}).get('value')
        detail_item = json.loads(detail_item)
        detail_item_list = list()
        for k, v in detail_item.items():
            detail_item_list.append((v['platename'], v['zjjlr'], v['199112']))
        detail_item_list.sort(key=lambda item: item[2], reverse=True)
        concept_zf_top10 = detail_item_list[:10]
        detail_item_list.sort(key=lambda item: item[1], reverse=True)
        concept_jlr_top10 = detail_item_list[:10]
        return concept_zf_top10, concept_jlr_top10

    def crawl_hot_plate_data(self, url_dict):
        res_dict = dict()
        for k, url in url_dict.items():
            res_dict[k] = list()
            self.driver.get(url)
            soup = BeautifulSoup(self.driver.page_source)
            tr_list = soup.find_all('tr')[1:]
            for i in tr_list[:10]:
                platename = i.find_all('td')[1].text
                res_dict[k].append(platename)
        (concept_zf_top10,
         concept_jlr_top10) = self.crawl_hot_concept_plate_data()
        res_dict[u'概 念 板块涨幅前十'] = [c[0] for c in concept_zf_top10]
        res_dict[u'概念资金净流入前十'] = [c[0] for c in concept_jlr_top10]
        hot_plate_industry = list(set(
            res_dict[u'同花顺行业涨幅前十']).intersection(
                set(res_dict[u'行业资金净流入前十'])))
        hot_plate_concept = list(
            set(res_dict[u'概 念 板块涨幅前十']).intersection(
                set(res_dict[u'概念资金净流入前十'])))
        res_dict[u'热点行业板块'] = hot_plate_industry
        res_dict[u'热点概念板块'] = hot_plate_concept
        return res_dict


def create_hot_plate_content(hot_plate_dict):
    hot_plate_content = list()
    hot_plate_industry = ''
    hot_plate_concept = ''
    for k, v in hot_plate_dict.items():
        if k == u'热点行业板块':
            hot_plate_industry = k + '  $  ' + '   $   '.join(v)
            continue
        if k == u'热点概念板块':
            hot_plate_concept = k + '  $  ' + '   $   '.join(v)
            continue
        hot_plate_content.append(k + '  $  ' + '   $   '.join(v))
    hot_plate_content.append(hot_plate_industry)
    hot_plate_content.append(hot_plate_concept)
    return '<br><br>'.join(hot_plate_content)


if __name__ == '__main__':
    hotplatespider = HotplateSpider()
    url_dict = {
        u'同花顺行业涨幅前十':
        ('http://q.10jqka.com.cn/thshy/index/field/199112/order/desc/page/1/ajax/1/'),
        u'行业资金净流入前十':
        ('http://q.10jqka.com.cn/thshy/index/field/zjjlr/order/desc/page/1/ajax/1/')}
    hot_plate_dict = hotplatespider.crawl_hot_plate_data(url_dict)
    hotplatespider.driver.quit()
    hot_plate_content = create_hot_plate_content(hot_plate_dict)
    print hot_plate_content.encode('utf8')
