import requests
try:
    import cookielib
except:
    import http.cookiejar as cookielib

import re

agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36"

header = {
    "HOST" : "www.zhihu.com",
    "Referer": "https://www.zhihu.com",
    "User-Agent": agent
}

session = requests.session()

def get_xsrf():
    response = session.get("https://www.zhihu.com", headers=header)
    print (response.text)
    # text = '<input type="hidden" name="_xsrf" value="c1556a7c15330a7fcba2278a1bf080d1"/>'
    match_obj = re.match('.*name="_xsrf" value="(.*?)".*', response.text)
    if match_obj:
        print (match_obj.group(1))
    else:
        print ('asd')

def zhihu_login(account, password):
    # 知乎登陆
    if re.match("^1\d{10}", account):
        print ('手机号码登陆')
        post_url = "https://www.zhihu.com/login/phone_num"
        post_data = {
            '_xsrf': get_xsrf(),
            'phone_num' : account,
            'password' : password
        }
        response_text = session.post(post_url, data=post_data, headers=header)

        session.cookies.save()

get_xsrf()