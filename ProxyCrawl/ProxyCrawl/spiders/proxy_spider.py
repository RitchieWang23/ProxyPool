#!/usr/local/bin/python3
# coding: UTF-8
# Author: David
# Email: youchen.du@gmail.com
# Created: 2017-04-19 20:23
# Last modified: 2017-04-30 14:25
# Filename: proxy_spider.py
# Description:
import scrapy

from scrapy.http import Request
from ProxyCrawl.items import ProxyItem
from ProxyCrawl.loaders import ProxyItemLoader


class ProxySpider(scrapy.Spider):
    def __init__(self, rule, *args, **kwargs):
        self.rule = rule
        self.current = 1
        self.start_urls = [self.rule.url_fmt.format(self.current)]

    def parse(self, response):
        for i in range(10):
            self.current += 1
            if self.current >= self.rule.max_page:
                break
            yield Request(self.rule.url_fmt.format(self.current))
        if response.status != 200:
            return None
        ip_list = response.xpath(self.rule.row_xpath)[1:]
        for ip_item in ip_list:
            l = ProxyItemLoader(item=ProxyItem(), selector=ip_item)
            l.add_xpath('proxy', self.rule.host_xpath)
            l.add_xpath('proxy', self.rule.port_xpath)
            l.add_xpath('ip', self.rule.host_xpath)
            l.add_xpath('port', self.rule.port_xpath)
            l.add_xpath('addr', self.rule.addr_xpath)
            l.add_xpath('mode', self.rule.mode_xpath)
            l.add_xpath('protocol', self.rule.proto_xpath)
            l.add_xpath('validation_time', self.rule.vt_xpath)
            l.add_value('src_rule', self.rule.name)
            yield l.load_item()
