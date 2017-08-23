# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo
import json
import scrapy
import codecs
from scrapy.exceptions import DropItem
from scrapy.pipelines.images import ImagesPipeline

class GirlsimagescrawlerPipeline(object):
    """将数据保存到json文件
    """
    def __init__(self):
       self.file = None

    def open_spider(self, spider):
        filename = spider.name + '.json'
        self.file = codecs.open(filename, 'wb', encoding='utf-8')

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        if item['title']:
            line = json.dumps(dict(item), ensure_ascii=False) + '\n'
            self.file.write(line)
            return item
        else:
            DropItem('没有找到Title属性值！')


class JpgDownloadPipeline(ImagesPipeline):
    """重写imagepipeline中的方法
    """
    def get_media_requests(self, item, info):
        for image_url in set(item['index_image_url']) | set(item['image_urls']):
            referer = self._find_referer(image_url)
            headers = {'Referer': referer}
            yield scrapy.Request(image_url, headers=headers, meta={'item':item, 'image_url':image_url})

    def item_completed(self, results, item, info):
        image_paths = [x['path'] for ok, x in results if ok]
        if not image_paths:
            raise DropItem('没有找到图片')
        item['download_results'] = image_paths

    def file_path(self, request, response=None, info=None):
        """对图片名称进行重命名
        :param request:
        :param response:
        :param info:
        :return:
        """
        item = request.meta['item']
        image_url = request.meta['image_url']
        filename = item['title'] + image_url.split('/')[-1]
        filepath = u'full/{0}/{1}'.format(item['title'], filename)
        return filepath

    def _find_referer(self, image_url):
        """私有方法，过滤出header中的Referer参数，有此参数才能正确下载
        :param image_url: 图片地址
        :return: referer参数
        """
        url_splits = image_url.split('/')
        referer = ''
        for s in url_splits[:-1]:
            referer += s + '/'
        return referer[:-1]


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