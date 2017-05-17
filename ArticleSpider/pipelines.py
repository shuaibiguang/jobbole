# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy.pipelines.images import ImagesPipeline
import codecs,json,pymysql
from scrapy.exporters import JsonItemExporter
from ArticleSpider.config import Config as C
from twisted.enterprise import adbapi

class ArticlespiderPipeline(object):
    def process_item(self, item, spider):
        return item

#使用scrapy 内部的异步存储数据库的形式来存储数据，这样更合理
class MysqlTwistedPipeline(object):
    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        dbparms = dict(
            host = C.host,
            port = C.port,
            db = C.db,
            user = C.user,
            password = C.password,
            charset = "utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,
        )
        dbpool = adbapi.ConnectionPool('pymysql', **dbparms)
        return cls(dbpool)

    def process_item(self, item, spider):
        # 使用Twisted 将mysql插入变成异步执行
        query = self.dbpool.runInteraction(self.do_insert, item)
        query.addErrback(self.handle_error, item, spider) #处理异常

    def handle_error(self, failure, item, spider):
        # 在这里做错误的处理
        print (failure)
        pass

    def do_insert(self, cursor, item):
        # 执行具体插入
        insert_sql, params = item.get_insert_sql()
        cursor.execute(insert_sql, params)

# 使用数据库来存储数据
class MysqlPipeline(object):
    def __init__(self):
        self.conn = pymysql.connect(host=C.host, port=C.port, db=C.db, user=C.user, password=C.password, charset="utf8mb4", cursorclass=pymysql.cursors.DictCursor)
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):
        insert_sql = """
            insert into jobbole_article VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """
        self.cursor.execute(insert_sql, (item['title'], item['create_time'], item['url'], item['url_object_id'], item['front_image_url'], item['front_image_path'], item['comment_nums'], item['fav_nums'], item['praise_nums'], item['tags'], item['content']))
        self.conn.commit()
        return item

# 使用scrapy内置的json方法来生成json文件
class JsonExporterPipeline(object):
    def __init__(self):
        self.file = open('ArticleExporter.json', 'wb')
        self.exporter = JsonItemExporter(self.file, encoding="utf-8", ensure_ascii=False)
        # self.exporter.start_exporting()

    def close_spider(self, spider):
        #关闭JsonExporter 的写入
        # self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item

# 在这里使用自定义的方法将数据存储到json里面
class JsonWithEncodingPipeline(object):
    def __init__(self):
        self.file = codecs.open("Article.json", "w", encoding="utf-8")
    def process_item(self, item, spider):
        line = json.dumps(dict(item), ensure_ascii=False) + '\n'
        self.file.write(line)
        return item
    def spider_closed(self, spider):
        self.file.close()

# 使用scrapy内置下载图片方法下载图片
class ArticleImagePipeline(ImagesPipeline):
    def item_completed(self, results, item, info):
        if "front_image_path" in item:
            for ok, value in results:
                image_file_path = value['path']
            item['front_image_path'] = image_file_path
            
        return item