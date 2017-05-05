# -*- coding: utf-8 -*-
import json
import scrapy
import re
import time
from PIL import Image
from urllib import parse

class ZhihuSpider(scrapy.Spider):
    name = "zhihu"
    allowed_domains = ["www.zhihu.com"]
    start_urls = ['http://www.zhihu.com/']
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
                question_id = match_obj.group(2)
                #在这里将question的网址传递出去开始解析
                yield  scrapy.Request(request_url, headers=self.headers, callback=self.parse_question)

    # question
    def parse_question(self, response):
        #在这里解析question 里面的内容
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