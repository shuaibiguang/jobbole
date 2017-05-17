import hashlib
import re
def get_md5(url):
    if isinstance(url, str):
        url = url.encode('utf-8')
    m = hashlib.md5()
    m.update(url)
    return m.hexdigest()

def exteact_num(text):
#     从字符串中提取数字
    math_re = re.match(r'.*?(\d+).*', text)
    if math_re:
        nums = int(math_re.group(1))
    else:
        nums = 0
    return nums

if __name__ == '__main__':
    # print (get_md5("http://www.jobbole.com/"))
    # print (exteact_num("330 个回答"))
    pass