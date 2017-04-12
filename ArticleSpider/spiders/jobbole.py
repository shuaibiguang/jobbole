# -*- coding: utf-8 -*-
import scrapy,re,datetime
from scrapy.http import Request
from urllib import parse
from ArticleSpider.items import JobBoleArticleItem,ArticleItemLoader
from ArticleSpider.utils.common import get_md5
# from scrapy.loader import ItemLoader

class JobboleSpider(scrapy.Spider):
    name = "jobbole"
    allowed_domains = ["blog.jobbole.com"]
    start_urls = ['http://blog.jobbole.com/all-posts/']

    def parse(self, response):
        # 将所有文章当前页面单个文章的url拿出来，交给parse_detail 解析下载，
        post_nodes = response.xpath('//div[@id="archive"]//div[@class="post-thumb"]/a')
        for post_node in post_nodes:
            front_images_url = post_node.xpath('img/@src').extract()[0]
            post_url = post_node.xpath('@href').extract()[0]
            yield Request(url=parse.urljoin(response.url, post_url), meta={'front_images_url':front_images_url}, callback=self.parse_detail)
        # 拿取下一页的连接，交给scrapy进行下载
        next_page = response.xpath('//a[@class="next page-numbers"]/@href').extract()
        if len(next_page) > 0:
            yield Request(url=parse.urljoin(response.url, next_page[0]), callback=self.parse)


    def parse_detail(self, response):
        article_item = JobBoleArticleItem()
        # 封面图
        front_image_url = response.meta.get('front_images_url', '')
        title = response.xpath("//div[@class='entry-header']/h1/text()").extract()
        create_time = response.xpath('//p[@class="entry-meta-hide-on-mobile"]/text()').extract()[0].strip().replace('·','').strip()
        praise_nums = response.xpath('//span[contains(@class,"vote-post-up")]/h10/text()').extract()[0]
        fav_nums = response.xpath('//span[contains(@class,"bookmark-btn")]/text()').extract()[0]
        # 有可能拿取到的赞没有数字， 这个时候默认为0
        math_re = re.match(r'.*?(\d+).*', fav_nums)
        if math_re:
            fav_nums = int(math_re.group(1))
        else:
            fav_nums = 0

        comment_nums = response.xpath('//a[@href="#article-comment"]/span/text()').extract()[0]
        math_re = re.match(r'.*?(\d+).*', comment_nums)
        if math_re:
            comment_nums = int(math_re.group(1))
        else:
            comment_nums = 0

        content = response.xpath('//div[@class="entry"]').extract()[0]
        
        tag_list = response.xpath('//p[@class="entry-meta-hide-on-mobile"]/a/text()').extract()
        tag_list = [element for element in tag_list if not "评论" in element]
        tags = ','.join(tag_list)

        #将过滤出来的内容存入到item里面
        article_item['title'] = title

        # article_item['create_time'] = create_time
        # article_item['title'] = title
        # article_item['url'] = response.url
        # article_item['front_image_url'] = [parse.urljoin(response.url, front_image_url)]
        # article_item['comment_nums'] = comment_nums
        # article_item['praise_nums'] = praise_nums
        # article_item['fav_nums'] = fav_nums
        # article_item['tags'] = tags
        # article_item['content'] = content
        # article_item['url_object_id'] = get_md5(response.url)

        # 在这里加载itemloader
        item_loader = ArticleItemLoader(item = JobBoleArticleItem(), response=response)
        item_loader.add_xpath("title", "//div[@class='entry-header']/h1/text()")
        item_loader.add_xpath("create_time", '//p[@class="entry-meta-hide-on-mobile"]/text()')
        item_loader.add_value("url",response.url)
        item_loader.add_value('front_image_url', parse.urljoin(response.url, front_image_url))
        item_loader.add_xpath('comment_nums', '//a[@href="#article-comment"]/span/text()')
        item_loader.add_xpath('praise_nums', '//span[contains(@class,"vote-post-up")]/h10/text()')
        item_loader.add_xpath('fav_nums','//span[contains(@class,"bookmark-btn")]/text()')
        item_loader.add_xpath('tags', '//p[@class="entry-meta-hide-on-mobile"]/a/text()')
        item_loader.add_xpath('content', '//div[@class="entry"]')
        item_loader.add_value('url_object_id', get_md5(response.url))
        article_item = item_loader.load_item()
        yield article_item
