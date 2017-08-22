# -*- coding: utf-8 -*-
import scrapy
from scrapy.selector import Selector
from GirlsImagesCrawler.items import GirlsimagescrawlerItem
from datetime import datetime
import re

class MmjpgSpider(scrapy.Spider):
    name = 'mmjpg'
    allowed_domains = ['mmjpg.com']
    start_urls = ['http://www.mmjpg.com']
    regex_pub_date = re.compile(ur'发表于: (.*?)</i>')
    regex_hotness = re.compile(ur'人气\((.*?)\)')
    regex_picinfo = re.compile(ur'picinfo = (.*?);')
    regex_next_page = re.compile(ur'<a href="(\S*)" class="ch">下一页</a>')

    def parse(self, response):
        """解析基础页面
        :param response: 请求返回内容
        :return:
        """
        imageLiList = response.css('div.pic ul li')
        for item in imageLiList:
            title = item.xpath('.//img/@alt').extract()[0]
            index_url = item.xpath('.//a/@href').extract()[0]
            crawl_date = datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')
            girlsImgItem = GirlsimagescrawlerItem(title=title, index_url=index_url, crawl_date=crawl_date)
            req = scrapy.Request(url=index_url, callback=self.parse_detail)
            req.meta['girlsImgItem'] = girlsImgItem
            yield req
        next_page = Selector(response).re(self.regex_next_page)
        if next_page:
            next_page_url = self.start_urls[0] + next_page[0]
            yield scrapy.Request(url=next_page_url, callback=self.parse)

    def parse_detail(self, response):
        """解析更多详细信息
        :param response:
        :return:
        """
        girlsImgItem = response.meta['girlsImgItem']
        girlsImgItem['pub_date'] = response.css('div.info')[0].re(self.regex_pub_date)[0]
        girlsImgItem['hotness'] = int(response.css('div.info')[0].re(self.regex_hotness)[0])
        girlsImgItem['tags'] = response.css('div.tags a').xpath('./text()').extract()
        girlsImgItem['image_counts'] = int(eval(response.css('div.clearfloat')[0].re(self.regex_picinfo)[0])[2])
        image_urls = []
        for i in range(1, girlsImgItem['image_counts']+1):
            image_urls.append(girlsImgItem['index_url'] + '/' + str(i))
        girlsImgItem['image_urls'] = image_urls
        yield girlsImgItem


