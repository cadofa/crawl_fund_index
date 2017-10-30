# -*- coding:utf-8 -*-

'''
created on 2015-07-21

@author:cuixiaoming

说明：邮件测试
'''

import datetime
import smtplib
import requests
import time
from email.mime.text import MIMEText
from email.header import Header
from bs4 import BeautifulSoup

mailto_list = ['cadofa@163.com']
mail_host = "smtp.163.com"
mail_user = 'cadofa@163.com'
subject = '国泰聚信仓位监控'


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


class FundSpider(object):

    def crawl_fund_data(self, url):
        res = requests.get(url)
        soup = BeautifulSoup(res.content)
        netvalue_list = soup.find('script', type="text/javascript").text[16:-2]
        netvalue_list = eval(netvalue_list)
        date_increase_tuple = [(i['date'], float(i['rate'])) for i in netvalue_list[:6]]
        date_increase_dict = dict(date_increase_tuple)
        return date_increase_dict

    def _crawl_index_data(self, url):
        res = requests.get(url)
        soup = BeautifulSoup(res.content)
        increase_list = soup.find(
            "table",
            class_="table_bg001 border_box limit_sale").find_all('tr')[1:7]
        date_increase = [i.find_all('td') for i in increase_list]
        date_increase_list = [(i[0].text,
                               float(i[6].text)) for i in date_increase]
        return date_increase_list

    def crawl_index_data(self, crawl_url):
        now = datetime.datetime.now().strftime('%Y-%m')
        year, month = now.split('-')
        year, month = int(year), int(month)
        month_to_season_dict = {1: 1, 2: 1, 3: 1, 4: 2,
                                5: 2, 6: 2, 7: 3, 8: 3,
                                9: 3, 10: 4, 11: 4, 12: 4}
        season = month_to_season_dict[int(month)]
        season_list = list()
        for i in range(2):
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
            source_data_list += self._crawl_index_data(
                crawl_url + "?year=%s&season=%s" % (year, season))
        return dict(source_data_list[:6])

    def calculate_fund_position(self, crawl_url):
        A_netvalue = self.crawl_fund_data(
            "http://fund.10jqka.com.cn/000362/historynet.html")
        C_netvalue = self.crawl_fund_data(
            "http://fund.10jqka.com.cn/000363/historynet.html")
        avg_fund_netvalue_i = dict(
            [(k, (A_netvalue[k]+C_netvalue[k])/2) for k in A_netvalue])
        # print  avg_fund_netvalue_i
        shanghai_index_increase = self.crawl_index_data(
            "http://quotes.money.163.com/trade/lsjysj_zhishu_000001.html")
        shenzhen_index_increase = self.crawl_index_data(
            "http://quotes.money.163.com/trade/lsjysj_zhishu_399001.html")
        hs300_index_increase = self.crawl_index_data(
            "http://quotes.money.163.com/trade/lsjysj_zhishu_399300.html")
        zhongxiao_index_increase = self.crawl_index_data(
            "http://quotes.money.163.com/trade/lsjysj_zhishu_399005.html")
        chuangye_index_increase = self.crawl_index_data(
            "http://quotes.money.163.com/trade/lsjysj_zhishu_399006.html")
        zz500_index_increase = self.crawl_index_data(
            "http://quotes.money.163.com/trade/lsjysj_zhishu_399905.html")
        avg_index_i = dict(
            [(k,
              (shanghai_index_increase[k] +
               shenzhen_index_increase[k] +
               hs300_index_increase[k] +
               zhongxiao_index_increase[k] +
               chuangye_index_increase[k] +
               zz500_index_increase[k])/6)
                for k in shanghai_index_increase])
        avg_fund_netvalue_i = dict(
            [(k.replace('-', ''), avg_fund_netvalue_i[k])
             for k in avg_fund_netvalue_i])
        position_num = dict(
            [(k, avg_fund_netvalue_i.get(k, 0)/avg_index_i[k.replace('-', '')])
             for k in avg_index_i])
        position_num = [
            (k, position_num[k])
            if position_num[k] > 0
            else (k, 0)
            for k in position_num]
        position_num.sort()
        return avg_fund_netvalue_i, avg_index_i, position_num


def create_mail_content(fund, index, pos):
    fund_date = list()
    fund_value = list()
    for d, v in fund:
        fund_date.append(str(d))
        fund_value.append(v)
    fund_content_list = list()
    for d, v in zip(fund_date, fund_value):
        fund_content_list.append('%s: %.2f%s' % (d.replace('-', ''), v, '%'))
    fund_content = '基金变化    ' + '   $   '.join(fund_content_list)
    index_date = list()
    index_value = list()
    for d, v in index:
        index_date.append(str(d))
        index_value.append(v)
    index_content_list = list()
    for d, v in zip(index_date, index_value):
        index_content_list.append('%s: %.2f%s' % (d, v, '%'))
    index_content = '指数变化    ' + '   $   '.join(index_content_list)
    pos_date = list()
    pos_value = list()
    for d, v in pos:
        pos_date.append(str(d))
        pos_value.append(v)
    pos_content_list = list()
    for d, v in zip(pos_date, pos_value):
        if v == 0:
            v = 'unknown'
            pos_content_list.append('%s: %s%s' % (d.replace('-', ''), v, '%'))
        else:
            pos_content_list.append('%s: %.2f%s' % (d.replace('-', ''),
                                                    v * 100, '%'))
    pos_content = '仓位变化    ' + '   $   '.join(pos_content_list)
    return '<br><br>'.join([fund_content, index_content, pos_content])

if __name__ == '__main__':
    while True:
        try:
            fundspider = FundSpider()
            fund, index, pos = fundspider.calculate_fund_position(
                "http://quotes.money.163.com/fund/jzzs_202011.html")
            fund = fund.items()
            fund.sort()
            index = index.items()
            index.sort()
            mail_content = create_mail_content(fund, index, pos)
            print mail_content
            break
        except Exception, e:
            print e
            time.sleep(18)
