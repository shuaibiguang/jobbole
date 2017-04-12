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
from scrapy.loader.processors import MapCompose,TakeFirst,Join

class ArticlespiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

def add_jobbole(value):
#     在标题后面添加 jobbole
    return value+"-jibbole"

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
        input_processor = MapCompose(add_jobbole)
    )
    create_time = scrapy.Field(
        input_processor = MapCompose(date_convert)
    )
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    front_image_url = scrapy.Field(
        output_processor = MapCompose(return_value)
    )
    front_image_path = scrapy.Field()
    praise_nums = scrapy.Field(
        input_processor = MapCompose(get_nums)
    )
    comment_nums = scrapy.Field(
        input_processor = MapCompose(get_nums)
    )
    fav_nums = scrapy.Field(
        input_processor = MapCompose(get_nums)
    )
    tags = scrapy.Field(
        input_processor = MapCompose(remove_comment_tags),
        output_processor = Join(',')
    )
    content = scrapy.Field()

