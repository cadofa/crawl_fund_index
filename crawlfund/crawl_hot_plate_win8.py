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
from email.mime.text import MIMEText
from email.header import Header
from bs4 import BeautifulSoup

mailto_list = ['cadofa@163.com']
mail_host = "smtp.163.com"
mail_user = 'cadofa@163.com'


def send_mail(to_list, sub, content, mail_pass):
    msg = MIMEText(content, 'plain', 'utf-8')
    msg['Subject'] = Header(sub, 'utf-8')
    msg['From'] = mail_user
    msg['To'] = ";".join(to_list)
    try:
        server = smtplib.SMTP()
        server.connect(mail_host, '25')
        server.login(mail_user, mail_pass)
        server.sendmail(mail_user, to_list, msg.as_string())
        server.close()
        return True
    except Exception as e:
        print(e)
        return False


class HotplateSpider(object):

    def crawl_hot_concept_plate_data(self):
        res = requests.get('http://q.10jqka.com.cn/stock/gn')
        concept_data = res.content.decode('gbk')
        soup = BeautifulSoup(concept_data)
        detail_item = soup.find('table', class_="m_table").findAll('tr')
        detail_item_list = list()
        for d in detail_item[1:]:
            item = d.findAll('td')
            detail_item_list.append((item[1].text,
                                     float(item[4].text.replace('%', '')),
                                     float(item[7].text)))
        detail_item_list.sort(key=lambda item: item[1], reverse=True)
        concept_zf_top10 = detail_item_list[:10]
        detail_item_list.sort(key=lambda item: item[2], reverse=True)
        concept_jlr_top10 = detail_item_list[:10]
        return concept_zf_top10, concept_jlr_top10

    def crawl_hot_plate_data(self, url_dict):
        res_dict = dict()
        for k, url in url_dict.items():
            res = requests.get(url)
            res_dict[k] = list()
            for r in json.loads(res.content)['data'][:10]:
                # platename = r['platename']
                res_dict[k].append(r['platename'])

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
            hot_plate_industry = k + '     ' + '   $   '.join(v)
            continue
        if k == u'热点概念板块':
            hot_plate_concept = k + '     ' + '   $   '.join(v)
            continue
        hot_plate_content.append(k + '     ' + '   $   '.join(v))
    hot_plate_content.append(hot_plate_industry)
    hot_plate_content.append(hot_plate_concept)
    return '\r\n\r\n'.join(hot_plate_content)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("mail_pass")
    args = parser.parse_args()
    mail_pass = args.mail_pass
    while True:
        try:
            hotplatespider = HotplateSpider()
            url_dict = {
                u'同花顺行业涨幅前十':
                ('http://q.10jqka.com.cn/interface/'
                 'stock/thshy/zdf/desc/1/quote/quote'),
                u'行业资金净流入前十':
                ('http://q.10jqka.com.cn/interface/'
                 'stock/thshy/jlr/desc/1/quote/quote')}
            # u'概 念 板块涨幅前十':
            # 'http://q.10jqka.com.cn/interface/stock/gn/zdf/desc/1/quote/quote',
            # u'概念资金净流入前十':
            # 'http://q.10jqka.com.cn/interface/stock/gn/jlr/desc/1/quote/quote'}
            hot_plate_dict = hotplatespider.crawl_hot_plate_data(url_dict)
            hot_plate_content = create_hot_plate_content(hot_plate_dict)
            print hot_plate_content.encode('utf8')
            #send_mail(mailto_list,  u'热点板块', hot_plate_content, mail_pass)
            break
        except Exception, e:
            print e
            time.sleep(18)
