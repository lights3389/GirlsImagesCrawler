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
            index_image_url = item.xpath('.//img/@src').extract()
            crawl_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            imageItem = GirlsimagescrawlerItem(title=title, index_url=index_url, index_image_url=index_image_url, crawl_date=crawl_date)
            req = scrapy.Request(url=index_url, callback=self.parse_item_info)
            req.meta['imageItem'] = imageItem
            yield req
        next_page = Selector(response).re(self.regex_next_page)
        if next_page:
            next_page_url = self.start_urls[0] + next_page[0]
            yield scrapy.Request(url=next_page_url, callback=self.parse)

    def parse_item_info(self, response):
        """解析更多详细信息
        :param response:
        :return:
        """
        imageItem = response.meta['imageItem']
        imageItem['pub_date'] = response.css('div.info')[0].re(self.regex_pub_date)[0]
        imageItem['hotness'] = int(response.css('div.info')[0].re(self.regex_hotness)[0])
        imageItem['tags'] = response.css('div.tags a').xpath('./text()').extract()
        imageItem['image_counts'] = int(eval(response.css('div.clearfloat')[0].re(self.regex_picinfo)[0])[2])
        imageItem['image_urls'] = []
        for counter in range(1, imageItem['image_counts']+1):
            page_url = imageItem['index_url'] + '/' + str(counter)
            yield scrapy.Request(url=page_url,callback=self.parse_item_img_url,meta={'imageItem':imageItem})

    def parse_item_img_url(self, response):
        """继续寻找每个item下 的每个图片地址，并添加到集合中
        :param response:
        :return:
        """
        imageItem = response.meta['imageItem']
        image_url = response.css('div#content img').xpath('./@src').extract()[0]
        imageItem['image_urls'].append(image_url)
        if len(imageItem['image_urls']) == imageItem['image_counts']:
            yield imageItem


