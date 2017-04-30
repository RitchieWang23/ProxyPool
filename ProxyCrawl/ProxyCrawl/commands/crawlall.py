#!/usr/local/bin/python3
# coding: UTF-8
# Author: David
# Email: youchen.du@gmail.com
# Created: 2017-04-25 16:25
# Last modified: 2017-04-30 15:27
# Filename: crawlall.py
# Description:
import redis

from twisted.internet import reactor, task
from scrapy.commands import ScrapyCommand
from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings

from ProxyCrawl.rules import Rule
from ProxyCrawl.spiders.proxy_spider import ProxySpider
from ProxyCrawl.maintainers import RuleMaintainer, ProxyMaintainer
from ProxyCrawl.maintainers import ScheduleMaintainer


class CrawlAll(ScrapyCommand):
    requires_project = True
    excludes = []

    def syntax(self):
        return '[options]'

    def short_desc(self):
        return 'Runs all of the spiders'

    def run(self, args, opts):
        conn = redis.Redis(decode_responses=True)
        runner = CrawlerRunner(get_project_settings())
        try:
            rules = Rule.loads()
            if not rules:
                raise ValueError
        except ValueError:
            print('Error in loading Redis rules, fallback to CSV rules')
            rules = Rule.loads('csv')
        for rule in rules:
            rule.save()
            if rule.name in self.excludes:
                continue
            if conn.hget('Rule:' + rule.name, 'status') == 'started':
                d = runner.crawl(ProxySpider, rule)
                # Set status to stopped if crawler finished
                d.addBoth(lambda _: conn.hset(
                    'Rule:' + rule.name, 'status', 'finished'))
        rule_maintainer = RuleMaintainer(conn, runner)
        proxy_maintainer = ProxyMaintainer(conn)
        schedule_maintainer = ScheduleMaintainer(conn)
        lc = task.LoopingCall(rule_maintainer)
        lc.start(1)
        lc = task.LoopingCall(proxy_maintainer)
        lc.start(0.5)
        lc = task.LoopingCall(schedule_maintainer)
        lc.start(10)
        reactor.run()
