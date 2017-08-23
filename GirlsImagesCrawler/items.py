# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class GirlsimagescrawlerItem(scrapy.Item):
    """图片集Item类
    公用属性：
        -title: 定义图片集名称
        -pub_date: 图片集发布日期
        -crawl_date: 项目爬行日期
        -hotness: 图片集热度
        -index_url: 图片集首页
        -tags: 图片标签
        -image_counts: 图片集包含的图片数量
        -image_urls: 图片集内图片数量
    """

    title = scrapy.Field()
    pub_date = scrapy.Field()
    crawl_date = scrapy.Field()
    hotness = scrapy.Field()
    index_url = scrapy.Field()
    index_image_url =scrapy.Field()
    tags = scrapy.Field()
    image_counts = scrapy.Field()
    image_urls = scrapy.Field()
    download_results = scrapy.Field()
