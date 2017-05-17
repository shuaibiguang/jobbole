import socket,os
class Config():
    # mysql
    host = socket.gethostbyname_ex(socket.gethostname())[2][0]
    port = 3306
    db = "article_spider"
    user = "root"
    password = "root"
    # system
    project_dir = os.path.abspath(os.path.dirname(__file__))
    # down images
    images_urls_field = "front_image_url"
    images_store = os.path.join(project_dir, 'images')