# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
import datetime
import re
# 自己定义一个itemloader 用来设置一些默认属性
from scrapy.loader import ItemLoader
# 对item里面字段预处理一下
from scrapy.loader.processors import MapCompose, TakeFirst, Join
from ArticleSpider.utils.common import exteact_num,get_md5
from ArticleSpider.settings import SQL_DATETIME_FORMAT, SQL_DATA_FORMAT


class ArticlespiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


def add_jobbole(value):
    #     在标题后面添加 jobbole
    return value + "-jibbole"


def date_convert(value):
    try:
        create_time = datetime.datetime.strptime(value, "%Y/%m/%d").date()
    except Exception as e:
        create_time = str(datetime.datetime.now().date())
    return create_time


# 正则表达拿取数字
def get_nums(value):
    math_re = re.match(r'.*?(\d+).*', value)
    if math_re:
        nums = int(math_re.group(1))
    else:
        nums = 0
    return nums


# 删除tags中的评论
def remove_comment_tags(value):
    if "评论" in value:
        return ''
    else:
        return value


# 解决first冲突，下载图片需要使用list
def return_value(value):
    return value


class ArticleItemLoader(ItemLoader):
    default_output_processor = TakeFirst()


class JobBoleArticleItem(scrapy.Item):
    title = scrapy.Field(
        input_processor=MapCompose(add_jobbole)
    )
    create_time = scrapy.Field(
        input_processor=MapCompose(date_convert)
    )
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    front_image_url = scrapy.Field(
        output_processor=MapCompose(return_value)
    )
    front_image_path = scrapy.Field()
    praise_nums = scrapy.Field(
        input_processor=MapCompose(get_nums)
    )
    comment_nums = scrapy.Field(
        input_processor=MapCompose(get_nums)
    )
    fav_nums = scrapy.Field(
        input_processor=MapCompose(get_nums)
    )
    tags = scrapy.Field(
        input_processor=MapCompose(remove_comment_tags),
        output_processor=Join(',')
    )
    content = scrapy.Field()

    def get_insert_sql(self):
        insert_sql = """
            insert into jobbole_article VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """
        params = (
            self['title'], self['create_time'], self['url'], self['url_object_id'], self['front_image_url'][0],
            self['front_image_path'], self['comment_nums'], self['fav_nums'], self['praise_nums'], self['tags'],
            self['content']
        )

        return insert_sql, params


class ZhihuQuestionItem(scrapy.Item):
    # 知乎问题的 item
    zhihu_id = scrapy.Field()
    topics = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    # 时间获取不到，所以这里不写
    answer_num = scrapy.Field()
    comments_num = scrapy.Field()
    watch_user_num = scrapy.Field()
    click_num = scrapy.Field()
    crawl_time = scrapy.Field()

    # 获取insert的sql语句
    def get_insert_sql(self):
        crawl_update_time = datetime.datetime.now().strftime(SQL_DATETIME_FORMAT)
        insert_sql = """
            insert into zhihu_question (zhihu_id, topics, url, title, content,  answer_num, comments_num, watch_user_num, click_num, crawl_time) 
            values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            ON DUPLICATE KEY  UPDATE topics = VALUES(topics), title = VALUES(title), content = VALUES(content),answer_num = VALUES(answer_num),
            comments_num = VALUES(comments_num), watch_user_num = VALUES(watch_user_num),click_num = VALUES(click_num), 
            crawl_update_time=VALUES(""" + crawl_update_time + """)
        """
        # 在这里采取新的方法来处理item里面的值，这种方法比较明了简单
        zhihu_id = self['zhihu_id'][0]
        topics = ",".join(self['topics'])
        url = "".join(self['url'])
        title = "".join(self['title'])
        content = "".join(self['content'])
        answer_num = exteact_num("".join(self['answer_num']))
        comments_num = exteact_num("".join(self['comments_num']))
        watch_user_num = self['watch_user_num'][0]
        click_num = self['watch_user_num'][1]
        crawl_time = datetime.datetime.now().strftime(SQL_DATETIME_FORMAT)

        params = (
        zhihu_id, topics, url, title, content, answer_num, comments_num, watch_user_num, click_num, crawl_time)
        return insert_sql, params


class ZhihuAnswerItem(scrapy.Item):
    # 知乎的问题回答的Item
    zhihu_id = scrapy.Field()
    url = scrapy.Field()
    question_id = scrapy.Field()
    author_id = scrapy.Field()
    content = scrapy.Field()
    parise_num = scrapy.Field()
    comments_num = scrapy.Field()
    create_time = scrapy.Field()
    update_time = scrapy.Field()
    crawl_time = scrapy.Field()

    #     获取insert  sql 语句
    def get_insert_sql(self):
        crawl_update_time = datetime.datetime.now().strftime(SQL_DATETIME_FORMAT)
        insert_sql = """
            insert into zhihu_answer (zhihu_id, url, question_id, author_id, content, parise_num, comments_num, create_time, update_time, crawl_time) 
            values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            ON DUPLICATE KEY  UPDATE content = VALUES(content), parise_num = VALUES(parise_num), comments_num = VALUES(comments_num),
            update_time=VALUES(update_time),crawl_update_time=VALUES(""" + crawl_update_time + """)
        """
        create_time = datetime.datetime.fromtimestamp(self['create_time']).strftime(SQL_DATETIME_FORMAT)
        update_time = datetime.datetime.fromtimestamp(self['update_time']).strftime(SQL_DATETIME_FORMAT)
        params = (
            self['zhihu_id'], self['url'], self['question_id'], self['author_id'], self['content'],
            self['parise_num'], self['comments_num'], create_time, update_time, self['crawl_time']
        )
        return insert_sql, params


class LagouJob(scrapy.Item):
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    title = scrapy.Field()
    salary = scrapy.Field()
    job_city = scrapy.Field()
    work_years = scrapy.Field()
    degree_need = scrapy.Field()
    job_type = scrapy.Field()
    publish_time = scrapy.Field()
    tags = scrapy.Field()
    job_advantage = scrapy.Field()
    job_desc = scrapy.Field()
    job_addr = scrapy.Field()
    job_addr2 = scrapy.Field()
    company_url = scrapy.Field()
    company_name = scrapy.Field()
    crawl_time = scrapy.Field()
    crawl_update_time = scrapy.Field()

    def get_insert_sql(self):
        insert_sql = """
            insert into laogou_job (url, url_object_id, title, salary, job_city, work_years, degree_need, job_type, publish_time, tags, job_advantage, job_desc, job_addr,company_url, company_name, crawl_time)
            VALUES  (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """
        url_object_id = get_md5(self['url'])
        title = "".join(self['title'])
        #工资按照最小的来存储
        if '-' in self['salary'][0]:
            salary = self['salary'][0].split('-')[0]
        else:
            salary = self['salaty'][0]
        job_city = self['job_city'][0].strip().split('/')[1]
        work_years = re.findall('.*(\d-\d+).*', self['work_years'])[0]



