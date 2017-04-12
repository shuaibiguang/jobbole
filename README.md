#使用技术列表 :blush:
### 这次爬取了伯乐在线，算是对scrapy的小试身手把
```xpath #获取页面中元素```
```Request  #请求访问后续需要的页面，在新的parse中接收到继续分析```
```loaderItem #代替item 进行数据处理，```
```from scrapy.loader.processors import MapCompose,TakeFirst,Join #用来处理item中的数据```
```ImagesPipeline #使用scrapy内置方法下载图片```
```from twisted.enterprise import adbapi #使用twisted异步往mysql中存储数据```
```config.py #详细的配置文件```
