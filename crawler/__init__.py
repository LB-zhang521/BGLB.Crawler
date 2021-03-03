# -*- coding:utf-8  -*-
# @Time     : 2021-02-21 01:28
# @Author   : BGLB
# @Software : PyCharm
import sys
from crawler.base import CrawlerBrower, CrawlerRequest, CrawlerAndroid
i = __import__('crawler.base')
sys.modules['crawler.base'] = None
