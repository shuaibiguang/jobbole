import socket,os
class Config():
    # mysql
    host = socket.gethostbyname_ex(socket.gethostname())[2][3]
    port = 3307
    db = "article_spide"
    user = "root"
    password = "root"
    # system
    project_dir = os.path.abspath(os.path.dirname(__file__))
    # down images
    images_urls_field = "front_image_url"
    images_store = os.path.join(project_dir, 'images')