# -*- coding:utf-8 -*-

'''
created on 2015-07-21

@author:cuixiaoming

说明：邮件测试
'''

import smtplib
import mechanize
import time
from email.mime.text import MIMEText
from email.header import Header
from bs4 import BeautifulSoup

mailto_list = ['cadofa@163.com']
mail_host = "smtp.163.com"
mail_user = 'cadofa@163.com'
mail_pass = ''
subject = '国泰聚信仓位监控'


def send_mail(to_list, sub, content):
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
    def init_browser(self):
        br = mechanize.Browser()
        br.set_handle_equiv(False)
        br.set_handle_gzip(True)
        br.set_handle_redirect(True)
        br.set_handle_referer(True)
        br.set_handle_robots(False)
        br.set_handle_refresh(False)
        br.set_debug_http(False)
        br.set_debug_redirects(True)
        br.set_debug_responses(True)
        br.addheaders = [
            ('User-agent',
                ('Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) '
                 'Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')),
            ('Accept',
                ('text/html,application/xhtml+xml,'
                 'application/xml;q=0.9,*/*;q=0.8'))]
        return br

    def crawl_data(self, url, flag=None):
        br = self.init_browser()
        res = br.open(url)
        soup = BeautifulSoup(res.read())
        if flag == 'fund':
            netvalue_list = soup.find_all('tr')[1:7]
            date_increase = [i.find_all('td') for i in netvalue_list]
            date_increase_tuple = [(i[0].text,
                                    float(i[3].text.replace('%', '')))
                                   for i in date_increase]
            date_increase_dict = dict(date_increase_tuple)
            return date_increase_dict
        if flag == 'index':
            increase_list = soup.find(
                "table",
                class_="table_bg001 border_box limit_sale").find_all('tr')[1:7]
            date_increase = [i.find_all('td') for i in increase_list]
            date_increase_tuple = [(i[0].text,
                                    float(i[6].text)) for i in date_increase]
            date_increase_dict = dict(date_increase_tuple)
            return date_increase_dict

    def calculate_fund_position(self, crawl_url):
        A_netvalue = self.crawl_data(
            "http://quotes.money.163.com/fund/jzzs_000362.html", 'fund')
        C_netvalue = self.crawl_data(
            "http://quotes.money.163.com/fund/jzzs_000363.html", 'fund')
        avg_fund_netvalue_i = dict(
            [(k, (A_netvalue[k]+C_netvalue[k])/2) for k in A_netvalue])
        # print  avg_fund_netvalue_i
        shanghai_index_increase = self.crawl_data(
            "http://quotes.money.163.com/trade/lsjysj_zhishu_000001.html",
            'index')
        shenzhen_index_increase = self.crawl_data(
            "http://quotes.money.163.com/trade/lsjysj_zhishu_399001.html",
            'index')
        hs300_index_increase = self.crawl_data(
            "http://quotes.money.163.com/trade/lsjysj_zhishu_399300.html",
            'index')
        zhongxiao_index_increase = self.crawl_data(
            "http://quotes.money.163.com/trade/lsjysj_zhishu_399005.html",
            'index')
        chuangye_index_increase = self.crawl_data(
            "http://quotes.money.163.com/trade/lsjysj_zhishu_399006.html",
            'index')
        zz500_index_increase = self.crawl_data(
            "http://quotes.money.163.com/trade/lsjysj_zhishu_399905.html",
            'index')
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
    return '\r\n\r\n'.join([fund_content, index_content, pos_content])

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
            send_mail(mailto_list, subject, mail_content)
            break
        except Exception, e:
            print e
            time.sleep(18)
