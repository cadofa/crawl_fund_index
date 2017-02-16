# -*- coding:utf-8 -*-

'''
created on 2015-07-21

@author:cuixiaoming

说明：邮件测试
'''

import datetime
import smtplib
import requests
import traceback
import json
import time
import argparse
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


class HotstockSpider(object):

    def crawl_hot_concept_plate_data(self):
        res = requests.get('http://q.10jqka.com.cn/gn/')
        concept_data = res.content.decode('gbk')
        soup = BeautifulSoup(concept_data)
        detail_item = soup.find('input', {'id': 'gnSection'}).get('value')
        detail_item = json.loads(detail_item)
        detail_item_list = list()
        for k, v in detail_item.items():
            detail_item_list.append((v['platename'], v['zjjlr'], v['199112'], v['cid']))
        detail_item_list.sort(key=lambda item: item[2], reverse=True)
        concept_zf_top10 = detail_item_list[:10]
        detail_item_list.sort(key=lambda item: item[1], reverse=True)
        concept_jlr_top10 = detail_item_list[:10]
        return concept_zf_top10, concept_jlr_top10

    def crawl_hot_plate_data(self):
        (concept_zf_top10,
         concept_jlr_top10) = self.crawl_hot_concept_plate_data()
        hot_plate_concept = list(set(concept_zf_top10).intersection(set(concept_jlr_top10)))
        return hot_plate_concept

    def crawl_hot_stock_data(self, hot_plate_concept):
        url_template = "http://q.10jqka.com.cn/gn/detail/field/199112/order/desc/page/1/ajax/1/code/%s"
        hot_stock_url_list = [url_template%h[3] for h in hot_plate_concept]
        hot_stocks_dict = dict()
        for u in hot_stock_url_list:
            res = requests.get(u)
            html_data = res.content.decode('gbk')
            soup = BeautifulSoup(html_data)
            detail_item = soup.find('table', class_="m-table m-pager-table").findAll('tr')
            for d in detail_item[1:]:
                item = d.findAll('td')
                hot_stocks_dict[item[1].text] = item[2].text
        return hot_stocks_dict

    def crawl_stock_history_data(self, url):
        res = requests.get(url)
        soup = BeautifulSoup(res.content)
        table_data_list = soup.find(
            "table",
            class_="table_bg001 border_box limit_sale").find_all('tr')[1:]
        data_list = [i.find_all('td') for i in table_data_list]
        trade_data_list = [[j.text for j in i] for i in data_list]
        return trade_data_list

    def stock_profitAndloss(self, stock_code):
        stock_data_list = self.crawl_stock_trade_data(stock_code)
        day_index = -1
        today_price = float(stock_data_list[day_index][4].replace(',', ''))
        # end_day_index = day_index + 1
        ma34 = sum([float(n[4].replace(',', ''))
                    for n in stock_data_list[day_index-33:]])/34
        ma144 = sum([float(n[4].replace(',', ''))
                     for n in stock_data_list[day_index-143:]])/144
        profitAndloss_34 = (today_price-ma34)/ma34
        profitAndloss_144 = (today_price-ma144)/ma144
        profitAndloss_avg = (profitAndloss_34+profitAndloss_144)/2
        return profitAndloss_avg

    def crawl_stock_trade_data(self, stock_code):
        crawl_url = ('http://quotes.money.163.com'
                     '/trade/lsjysj_%s.html?year=%s&season=%s')
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
        stock_data_list = list()
        for year, season in season_list:
            stock_data_list += self.crawl_stock_history_data(
                crawl_url % (stock_code, year, season))
        stock_data_list.sort()
        return stock_data_list

    def cal_hot_stocks_profitAndloss(self, final_stock_dict):
        final_stock_profitAndloss = dict()
        for k in final_stock_dict:
            final_stock_profitAndloss[k] = self.stock_profitAndloss(k)
        return final_stock_profitAndloss

    def crawl_rank_stock_data(self, url, sort, order):
        res = requests.get(url % (sort, order))
        res_dict = json.loads(res.content)
        tmp_dict_data = dict()
        for s in res_dict['list']:
            tmp_dict_data[s['SYMBOL']] = s['SNAME']
        return tmp_dict_data

    def crawl_five_unusual_plate_stocks(self):
        crawl_url_tpl = ("http://quotes.money.163.com/hs/service/diyrank.php?"
                         "host=http://quotes.money.163.com"
                         "/hs/service/diyrank.php&page=0"
                         "&query=STYPE:EQA&fields=NO,SYMBOL,"
                         "NAME,PRICE,PERCENT,UPDOWN,"
                         "FIVE_MINUTE,OPEN,YESTCLOSE,"
                         "HIGH,LOW,VOLUME,TURNOVER,HS,LB,WB,ZF,"
                         "PE,MCAP,TCAP,MFSUM,"
                         "MFRATIO.MFRATIO2,MFRATIO.MFRATIO10,SNAME,"
                         "CODE,ANNOUNMT,UVSNEWS&sort=%s"
                         "&order=%s&count=68&type=query")
        increase_rank_stocks_dict = self.crawl_rank_stock_data(
            crawl_url_tpl, "PERCENT", "desc")
        fall_rank_stocks_dict = self.crawl_rank_stock_data(
            crawl_url_tpl, "PERCENT", "asc")
        amplitude_rank_stocks_dict = self.crawl_rank_stock_data(
            crawl_url_tpl, "ZF", "desc")
        volumeratio_rank_stocks_dict = self.crawl_rank_stock_data(
            crawl_url_tpl, "LB", "desc")
        turnoverrate_rank_stocks_dict = self.crawl_rank_stock_data(
            crawl_url_tpl, "HS", "desc")

        return (increase_rank_stocks_dict,
                fall_rank_stocks_dict, amplitude_rank_stocks_dict,
                volumeratio_rank_stocks_dict, turnoverrate_rank_stocks_dict)

    def select_hot_stocks(self, hot_stocks_dict, increase_stocks, fall_stocks,
                          amplitude_stocks, LB_stocks, HS_stocks):
        hot_and_increase = list(
            set(hot_stocks_dict.keys()).intersection(
                set(increase_stocks.keys())))
        hot_and_fall = list(
            set(hot_stocks_dict.keys()).intersection(
                set(fall_stocks.keys())))
        hot_and_amplitude = list(
            set(hot_stocks_dict.keys()).intersection(
                set(amplitude_stocks.keys())))
        hot_and_LB = list(
            set(hot_stocks_dict.keys()).intersection(
                set(LB_stocks.keys())))
        hot_and_HS = list(
            set(hot_stocks_dict.keys()).intersection(
                set(HS_stocks.keys())))
        total_stocks = list(set(hot_and_increase + hot_and_fall +
                            hot_and_amplitude + hot_and_LB + hot_and_HS))
        final_stock_dict = dict()
        for s in total_stocks:
            if s in hot_and_increase:
                final_stock_dict[s] = final_stock_dict.get(s, 0) + 1
            if s in hot_and_fall:
                final_stock_dict[s] = final_stock_dict.get(s, 0) + 1
            if s in hot_and_amplitude:
                final_stock_dict[s] = final_stock_dict.get(s, 0) + 1
            if s in hot_and_LB:
                final_stock_dict[s] = final_stock_dict.get(s, 0) + 1
            if s in hot_and_HS:
                final_stock_dict[s] = final_stock_dict.get(s, 0) + 1
        return final_stock_dict


def create_hot_stock_content(hot_stocks_dict,
                             final_stock_dict,
                             final_stock_profitAndloss=None):
    if not final_stock_profitAndloss:
        final_stock_profitAndloss = dict()
    final_stock_items = final_stock_dict.items()
    final_stock_items.sort(key=lambda i: i[1], reverse=True)
    hot_stocks_content_list = list()
    if len(final_stock_items) > 18:
        final_stock_items = final_stock_items[:18]
    for k, v in final_stock_items:
        profitAndloss = final_stock_profitAndloss.get(k, '')
        profitAndloss = profitAndloss*100 if profitAndloss else float(0)
        hot_stocks_content_list.append('%s  &nbsp;&nbsp;&nbsp;&nbsp; %s &nbsp;&nbsp;&nbsp;&nbsp; %.f%s' %
                                       (str(k),
                                        str(hot_stocks_dict[k].encode('utf8')),
                                        float(v)/5*100, '%',))
    #return '\r\n\r\n'.join(hot_stocks_content_list)
    return '<br><br>'.join(hot_stocks_content_list)
if __name__ == '__main__':
    hotplatespider = HotstockSpider()
    hot_plate_concept = hotplatespider.crawl_hot_plate_data()
    hot_stocks_dict = hotplatespider.crawl_hot_stock_data(hot_plate_concept)
    (increase_stocks, fall_stocks,
     amplitude_stocks, LB_stocks,
     HS_stocks) = hotplatespider.crawl_five_unusual_plate_stocks()
    final_stock_dict = hotplatespider.select_hot_stocks(
        hot_stocks_dict, increase_stocks,
        fall_stocks, amplitude_stocks, LB_stocks, HS_stocks)
    final_hot_stock_contnet = create_hot_stock_content(
        hot_stocks_dict,
        final_stock_dict)
    print final_hot_stock_contnet.decode('utf8')
