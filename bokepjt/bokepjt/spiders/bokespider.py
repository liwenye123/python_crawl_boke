# -*- coding: utf-8 -*-
import scrapy
from bokepjt.items import BokepjtItem
from scrapy.http import Request
import re
import urllib.request



class BokespiderSpider(scrapy.Spider):
    name = 'bokespider'
    allowed_domains = ['hexun.com']
    #设置要爬取用户的uid
    uid = "19940007"
    def start_requests(self):
        #首次爬取模拟成浏览器进行
        yield Request("http://"+str(self.uid)+".blog.hexun.com/p1/default.html",
                      headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36'})

    def parse(self, response):
        item = BokepjtItem()
        #用XPath表达式提取文章名和对应链接
        item['name'] = response.xpath("//span[@class='ArticleTitleText']/a/text()").extract()
        item['url'] = response.xpath("//span[@class='ArticleTitleText']/a/@href").extract()
        #接下来使用urllib和re模块获取博文的评论数和阅读数
        #首先提取存储评论数和点击数网址的正则表达式
        pat1 = '<script type="text/javascript" src="(http://click.tool.hexun.com/.*?)">'
        #hcurl为存储评论数和点击数的网址
        hcurl = re.compile(pat1).findall(str(response.body))[0]
        #模拟成浏览器
        headers2 = ('User-Agent',
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36')
        opener = urllib.request.build_opener()
        opener.addheaders = [headers2]
        urllib.request.install_opener(opener)
        data = urllib.request.urlopen(hcurl).read()
        #pat2 为提取阅读数的正则表达式
        pat2 = "click\d*?','(\d*?)'"
        #pat3 为提取评论数的正则表达式
        pat3 = "comment\d*?','(\d*?)'"
        item["hits"] = re.compile(pat2).findall(str(data))
        item["comment"] = re.compile(pat3).findall(str(data))
        yield item
        #提取博文列表页的总页数
        pat4 = "blog.hexun.com/p(.*?)/"
        #通过正则表达式获取的数据是一个列表，倒数第二个元素为总页数
        data2 = re.compile(pat4).findall(str(response.body))
        if (len(data2)) >= 2:
            totalurl = data[-2]
        else:
            totalurl = 1

        #进入for循环，依次爬取各博文列表的数据
        for i in range(2, int(totalurl)+1):
            #构造下一次要爬取的URL
            nexturl = "http://"+str(self.uid)+".blog.hexun.com/p"+str(i)+"/default.html"
            #进行下一次爬取。
            yield Request(nexturl, callback=self.parse, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36'})




