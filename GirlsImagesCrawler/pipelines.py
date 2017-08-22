# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo

class GirlsimagescrawlerPipeline(object):
    def process_item(self, item, spider):
        return item


class MongoPipeline(object):
    """保存到MongoDB的类
    """
    collection_name = 'mmjpg'
    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        """类方法，配置mongodb
        :param crawler:
        :return:
        """
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATEBASE', 'items')
        )

    def open_spider(self, spider):
        """打开爬虫过程
        :param spider:
        :return:
        """
        self.client = pymongo.MongoClient(host=self.mongo_uri)
        self.db = self.client[self.mongo_db]


    def close_spider(self, spider):
        """关闭爬虫过程
        :param spider:
        :return:
        """
        self.client.close()

    def process_item(self, item, spider):
        """爬行过程中存档
        :param item:
        :param spider:
        :return: 返回item
        """
        self.db[self.collection_name].insert(dict(item))
        return item