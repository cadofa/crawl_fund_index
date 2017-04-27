# -*-coding: utf-8 -*-

import tornado.web

from utils import url_prefix, url_pattern
from crawltools.crawl_hot_stocks_win8 import HotstockSpider, create_hot_stock_content
from crawltools.crawl_hot_plate_win8 import HotplateSpider, create_hot_plate_content
from crawltools.crawl_index_analyse_win8 import (IndexSpider,
                                                 create_volume_ratio_content,
                                                 create_profitAndloss_content,
                                                 create_lstrend_content)
from crawltools.crawl_fund_to_email_win8 import FundSpider, create_mail_content

url_pattern = url_pattern

@url_prefix(r"/stock")
class Clawl_hot_stock_Handler(tornado.web.RequestHandler):
    def get(self):
        hotplatespider = HotstockSpider()
        hot_plate, name_url_dict = hotplatespider.crawl_hot_plate_data()

        hot_stocks_dict = hotplatespider.crawl_hot_stock_data(
            hot_plate, name_url_dict)

        (increase_stocks, fall_stocks,
         amplitude_stocks, LB_stocks,
         HS_stocks) = hotplatespider.crawl_five_unusual_plate_stocks()

        final_stock_dict = hotplatespider.select_hot_stocks(
            hot_stocks_dict, increase_stocks,
            fall_stocks, amplitude_stocks, LB_stocks, HS_stocks)

        final_hot_stock_contnet = create_hot_stock_content(
            hot_stocks_dict,
            final_stock_dict)
        self.write(final_hot_stock_contnet)


@url_prefix(r"/plate")
class Clawl_hot_plate_Handler(tornado.web.RequestHandler):
    def get(self):
    	hotplatespider = HotplateSpider()
    	url_dict = {
        	u'同花顺行业涨幅前十':
        	('http://q.10jqka.com.cn/thshy/index/field/199112/order/desc/page/1/ajax/1/'),
        	u'行业资金净流入前十':
        	('http://q.10jqka.com.cn/thshy/index/field/zjjlr/order/desc/page/1/ajax/1/')}
    	hot_plate_dict = hotplatespider.crawl_hot_plate_data(url_dict)
    	hot_plate_content = create_hot_plate_content(hot_plate_dict)
        self.write(hot_plate_content.encode('utf8'))


@url_prefix(r"/index")
class Clawl_index_Handler(tornado.web.RequestHandler):
    def get(self):
        indexspider = IndexSpider()
        source_data_dict = dict()
        for i in ['000001', '399106', '399300', '399101', '399102', '399905']:
            source_data_dict[i] = indexspider.crawl_index_data(
                "http://quotes.money.163.com/trade/lsjysj_zhishu_%s.html" % i)
        volume_ratio_data = indexspider.cal_volume_ratio(source_data_dict)
        volume_ratio_mail_content = create_volume_ratio_content(volume_ratio_data)
        index_profitAndloss = indexspider.index_profitAndloss(source_data_dict)
        profitAndloss_content = create_profitAndloss_content(index_profitAndloss)
        ls_trend = indexspider.long_short_trend(source_data_dict)
        ls_trend_content = create_lstrend_content(ls_trend)
        self.write('<br><br><br>'.join([volume_ratio_mail_content,
                                        profitAndloss_content,
                                        ls_trend_content]))

@url_prefix(r"/fund")
class Clawl_fund_Handler(tornado.web.RequestHandler):
    def get(self):
        fundspider = FundSpider()
        fund, index, pos = fundspider.calculate_fund_position(
            "http://quotes.money.163.com/fund/jzzs_202011.html")
        fund = fund.items()
        fund.sort()
        index = index.items()
        index.sort()
        mail_content = create_mail_content(fund, index, pos)
        self.write(mail_content)
