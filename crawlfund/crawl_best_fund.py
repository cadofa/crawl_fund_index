# -*- coding: utf8 -*-
import re
import smtplib
import requests
import argparse
import numpy
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


def craw_data(url):
    rs = requests.get(url)
    pattern = r'code":"(\d{6})'
    fund_code_list = re.findall(pattern, rs.content)
    #print fund_code_list
    return fund_code_list


def crawl_fund_ranking(fund_code_list, carwl_num):
    url_format = 'http://fund.10jqka.com.cn/{}/'
    fund_data = list()
    for f in fund_code_list[:carwl_num]:
        rs = requests.get(url_format.format(f))
        soup = BeautifulSoup(rs.content.decode('gbk', 'ignore'))
        name = soup.find('h2', class_='fl').find('a').get_text()
        tr = soup.find('div',
                       class_='sub_wraper_1 cb mt20').find(
                       'table').find_all('tr',
                                         class_='even')[-1].find_all('td')
        ranking_list = []
        for t in tr[1:-1]:
            try:
                ranking_list.append(int(t.text.split('/')[0]))
            except ValueError:
                pass
        if len(ranking_list)>1:
            average = int(round(numpy.mean(ranking_list)))
            variance = int(round(numpy.var(ranking_list)))
            fund_data.append([name, average, variance])
        else:
            pass
    return fund_data


def create_mail_content(fund_data, type_name):
    average_content_title = type_name + u'排名前十八:\n'
    fund_data.sort(key=lambda x: x[1])
    best_average_fund_set = set()
    content_list = list()
    for f in fund_data[:18]:
        content_list.append(f[0])
        best_average_fund_set.add(f[0])
    average_content = average_content_title + '\n'.join(content_list)

    variance_content_title = type_name + u'方差前十八:\n'
    fund_data.sort(key=lambda x: x[2])
    best_variance_fund_set = set()
    content_list = list()
    for f in fund_data[:18]:
        content_list.append(f[0])
        best_variance_fund_set.add(f[0])
    variance_content = variance_content_title + '\n'.join(content_list)

    best_fund_set = best_average_fund_set.intersection(best_variance_fund_set)
    best_fund_title = type_name + 'Best Fund:\n'
    best_content = best_fund_title + '\n'.join(best_fund_set)
    return '\n\n\n'.join([average_content,
                          variance_content,
                          best_content])


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("type",
                        choices=['mixed', 'stock', 'bond', 'guaranteed'])
    parser.add_argument("carwl_num", choices=['288', '588', '688'])
    #parser.add_argument("mail_pass")
    args = parser.parse_args()
    type_ = args.type
    carwl_num = int(args.carwl_num)
    #mail_pass = args.mail_pass
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
            carwl_num = 88
            url = ('http://fund.ijijin.cn/data/Net/info/'
                   'bbx_F008_desc_0_0_1_9999_0_0_0_jsonp_g.html')
        fund_code_list = craw_data(url)
        fund_data = crawl_fund_ranking(fund_code_list, carwl_num)
        mail_content = create_mail_content(fund_data, type_name)
        print mail_content
        #send_mail(mailto_list,
        #          type_name + 'Best Fund', mail_content, mail_pass)
