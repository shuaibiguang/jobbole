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
session.cookies = cookielib.LWPCookieJar(filename="cookies.txt")

# 加载ckkoies
try:
    session.cookies.load(ignore_discard=True)
except:
    print ('未能加载cookie')

def get_xsrf():
    response = session.get("https://www.zhihu.com", headers=header)
    match_obj = re.findall(r'.*name="_xsrf" value="(.*?)"/>', response.text)
    if match_obj:
        return match_obj[0]
    else:
        return ""

def is_login():
    #判断用户是否登陆 用过访问用户中心
    inbox_index = "https://www.zhihu.com/inbox"
    response = session.get(inbox_index, headers=header, allow_redirects=False)
    if response.status_code != 200:
        return False
    else:
        return True

# 拿取验证码图片，使用验证码登陆
def get_captcha():
    import time
    t = str(int(time.time()*1000))
    captcha_url = "https://www.zhihu.com/captcha.gif?r=%s&type=login"%(t)
    t = session.get(captcha_url, headers=header)
    with open('captcha.jpg', 'wb') as f:
        f.write(t.content)
    from PIL import Image
    try:
        with Image.open('captcha.jpg') as im:
            im.show()
    except:
        pass

    captcha = input("请输入途中验证码:\n>")
    return captcha


def zhihu_login(account, password):
    # 知乎登陆
    captcha = get_captcha()
    if re.match("^1\d{10}", account):
        print ('手机号码登陆')
        post_url = "https://www.zhihu.com/login/phone_num"
        post_data = {
            '_xsrf': get_xsrf(),
            'phone_num' : account,
            'password' : password,
            'captcha': captcha
        }
    else:
        # 判断用户名是否为邮箱
        if '@' in account:
            post_url = "https://www.zhihu.com/login/email"
            post_data = {
                '_xsrf': get_xsrf(),
                'email' : account,
                'password' : password,
                'captcha': captcha
            }

    response_text = session.post(post_url, data=post_data, headers=header)
    session.cookies.save()

zhihu_login('@qq.com','z0')
is_login()
# get_captcha()