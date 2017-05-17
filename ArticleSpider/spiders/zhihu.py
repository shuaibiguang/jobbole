# -*- coding: utf-8 -*-
import json
import scrapy
import re
import time
import datetime
from PIL import Image
from urllib import parse
from scrapy.loader import  ItemLoader
from ArticleSpider.items import ZhihuQuestionItem, ZhihuAnswerItem

class ZhihuSpider(scrapy.Spider):
    name = "zhihu"
    allowed_domains = ["www.zhihu.com"]
    start_urls = ['http://www.zhihu.com/']
    #question的第一页answer的请求url
    start_answer_url = "https://www.zhihu.com/api/v4/questions/{0}/answers?sort_by=default&include=data%5B%2A%5D.is_normal%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2Cmark_infos%2Ccreated_time%2Cupdated_time%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%2Cupvoted_followees%3Bdata%5B%2A%5D.author.badge%5B%3F%28type%3Dbest_answerer%29%5D.topics&limit={1}&offset={2}"
    headers = {
        "HOST": "www.zhihu.com",
        "Referer": "https://www.zhihu.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36"
    }

    def parse(self, response):
        # 在这里开始正式爬取内容了
        all_urls = response.xpath("//a/@href").extract()
        all_urls = [parse.urljoin(response.url, url) for url in all_urls]
        for url in all_urls:
            match_obj = re.match("(.*zhihu.com/question/(\d+)).*", url)
            if match_obj:
                request_url = match_obj.group(1)
                question_id = int(match_obj.group(2))
                #在这里将question的网址传递出去开始解析
                yield  scrapy.Request(request_url, meta={'question_id': question_id}, headers=self.headers, callback=self.parse_question)
            else:  #如果这个页面里面的url不是question的话，那么还是访问进去，继续找question页面
                # yield  scrapy.Request(url, headers=self.headers, callback=self.parse)
                pass
    # question
    def parse_question(self, response):
        #在这里解析question 里面的内容,这里直接处理的是知乎的新版本，在当前时间线中，知乎已经全部改版，没有旧版本了
        item_loader = ItemLoader(item=ZhihuQuestionItem(), response=response)
        item_loader.add_xpath("title", '//h1[@class="QuestionHeader-title"]/text()')
        item_loader.add_xpath("content", '//div[@class="QuestionHeader-detail"]//span')
        item_loader.add_value('url', response.url)
        item_loader.add_value('zhihu_id', response.meta.get('question_id', ''))
        item_loader.add_xpath('answer_num', '//h4[@class="List-headerText"]/span/text()') #r'(^\d+).*'
        item_loader.add_xpath('comments_num', '//div[@class="QuestionHeader-actions"]/button/text()')
        item_loader.add_xpath('watch_user_num', '//div[@class="NumberBoard-value"]/text()')
        item_loader.add_xpath('topics', '//div[@class="Popover"]/div/text()')
        question_item = item_loader.load_item()

        #在这里来拿取里面具体的回答 answer 使用get请求接口来实现
        url = self.start_answer_url.format(response.meta.get('question_id'), 20, 0)
        yield scrapy.Request(url, headers=self.headers, callback=self.parse_answer)
        # yield question_item

    #在这里处理question 的 answer
    def parse_answer(self, response):
        ans_json = json.loads(response.text)
        is_end = ans_json['paging']['is_end']
        totals = ans_json['paging']['totals']
        next_url = ans_json['paging']['next']

        #在这里开始提取question里面的answer的值
        for answer in ans_json['data']:
            answer_item = ZhihuAnswerItem()
            answer_item['zhihu_id'] = answer['id']
            answer_item['url'] = answer['url']
            answer_item['question_id'] = answer['question']['id']
            answer_item['author_id'] = answer['author']['id'] if 'id' in answer['author'] else None
            answer_item['content'] = answer['content'] if 'content' in answer else None
        #     点赞数
            answer_item['parise_num'] = answer['voteup_count']
        #     评论数
            answer_item['comments_num'] = answer['comment_count']
        #     创建时间
            answer_item['create_time'] = answer['created_time']
        # 修改时间
            answer_item['update_time'] = answer['updated_time']
        #     当前爬取时间
            answer_item['crawl_time'] = datetime.datetime.now()
            yield answer_item
        if not is_end:
            yield scrapy.Request(next_url, headers=self.headers, callback=self.parse_answer)
        pass


    # 重构初始函数在开始爬取之前先进行登陆,首先拿取到登陆验证码图片
    def start_requests(self):
        t = str(int(time.time() * 1000))
        captcha_url = "https://www.zhihu.com/captcha.gif?r=%s&type=login"%(t)
        return [scrapy.Request(captcha_url, headers=self.headers ,callback=self.get_captcha)]

    # 在这里拿取验证码图片，并且打开
    def get_captcha(self, response):
        if response.status == 200:
            with open('captcha.jpg', 'wb') as f:
                f.write(response.body)
            try:
                with Image.open('captcha.jpg') as im:
                    im.show()
            except:
                pass
            return [scrapy.Request(url = "http://www.zhihu.com/", headers=self.headers, callback=self.login)]

    def login(self, response):
        # 拿取xsrf的值
        response_text = response.text
        match_obj = re.findall(r'.*name="_xsrf" value="(.*?)"/>', response.text)
        xsrf = ''
        captcha = input("请输入验证码：\n>")
        if match_obj:
            xsrf = match_obj[0]
        if xsrf:
            return  [scrapy.FormRequest(
                url = "https://www.zhihu.com/login/email",
                formdata = {
                    '_xsrf': xsrf,
                    'email': "519349139@qq.com",
                    'password': "z6028590",
                    'captcha': captcha
                },
                headers = self.headers,
                callback = self.check_login
            )]

    def check_login(self, respone):
        # 判断用户是否登陆
        text_json = json.loads(respone.text)
        if 'msg' in text_json and text_json['msg'] == '登录成功':
            for url in self.start_urls:
                yield scrapy.Request(url, dont_filter=True, headers=self.headers)