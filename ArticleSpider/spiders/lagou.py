# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from ArticleSpider.items import LagouJob
from scrapy.loader import ItemLoader


class LagouSpider(CrawlSpider):
    name = 'lagou'
    allowed_domains = ['www.lagou.com']
    start_urls = ['https://www.lagou.com/']

    rules = (
        Rule(LinkExtractor(allow=r'zhaopin/.*'), follow=True),  # 招聘列表页面
        Rule(LinkExtractor(allow=r'gongsi/.*'), follow=True),  # 公司页面
        Rule(LinkExtractor(allow=r'jobs/\d+.html'), callback='parse_item', follow=True),
    )

    def parse_item(self, response):
        item_loader = ItemLoader(item=LagouJob(), response=response)
        item_loader.add_value('url', response.url)
        item_loader.add_xpath('title', '//div[@class="job-name"]/@title')
        item_loader.add_xpath('salary', '//dd[@class="job_request"]/p/span[@class="salary"]/text()')
        item_loader.add_xpath('job_city', '//dd[@class="job_request"]/p/span[2]/text()')
        item_loader.add_xpath('work_years', '//dd[@class="job_request"]/p/span[3]/text()')
        item_loader.add_xpath('degree_need', '//dd[@class="job_request"]/p/span[4]/text()')
        item_loader.add_xpath('job_type', '//dd[@class="job_request"]/p/span[5]/text()')
        item_loader.add_xpath('publish_time', '//p[@class="publish_time"]/text()')
        item_loader.add_xpath('tags', '//ul[contains(@class, "position-label")]//li/text()')
        item_loader.add_xpath('job_advantage', '//dd[@class="job-advantage"]/p/text()')
        item_loader.add_xpath('job_desc', '//dd[@class="job_bt"]/div//p/text()')
        item_loader.add_xpath('job_addr', '//div[@class="work_addr"]//a/text()')
        item_loader.add_xpath('job_addr2', '//div[@class="work_addr"]/text()')
        item_loader.add_xpath('company_url', '//dl[@id="job_company"]/dt/a/@href')
        item_loader.add_xpath('company_name', '//h2[@class="fl"]/text()')
        lagou_item = item_loader.load_item()
        yield lagou_item
