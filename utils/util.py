# -*- coding:utf-8  -*-
# @Time     : 2021-03-27 01:09
# @Author   : BGLB
# @Software : PyCharm
from functools import wraps


def singleton(cls):
    """
        单例装饰器 singleton
    :param cls:
    :return:
    """
    _singleton = {}

    @wraps(cls)
    def wrapper(*args, **kwargs):
        if not _singleton.get(cls):
            _singleton[cls] = cls(*args, **kwargs)
        return _singleton[cls]
    return wrapper


def code_template(project_name: str, crawler_type:str):
    """
        代码模板
    :return: str
    """

    code_main = "from crawler.{crawler_type} import Crawler{crawler_type}\r\n\n" \
                "class Crawler{project_name}(Crawler{crawler_type}):\r\n\t" \
                "def __init__(self, crawler_config):\n\t\t" \
                "super().__init__(crawler_config)\n\n\t" \
                "def saver(self):\n\t\tpass\n\n\t" \
                "def spider(self):\n\t\tpass\n\t" \
                "def __del__(self):\n\t\tsuper().__del__()\n" \
                "".format(crawler_type=crawler_type.title(), project_name=project_name.title())


    return code_main