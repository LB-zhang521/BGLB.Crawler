# -*- coding:utf-8  -*-
# @Time     : 2021-02-28 01:49
# @Author   : BGLB
# @Software : PyCharm

"""
    数据存储

"""
from threading import Thread


class _SaverBase(Thread):
    """
        数据存储基类
    """
    def __init__(self, path, file_ext, crawler_data: list):
        """
            文件路径 文件后缀 数据

        """
        super().__init__()
        self.path = None
        self.file_ext = None
        self.crawler_data = None  # json 和 dict 为主
        self.setName('Saver')

    def save_dict_data(self):
        file_name = self.path+self.file_ext
        pass

    def save_img(self):
        pass

    def save_audio(self):
        """
        保存音频文件
        :return:
        """

    def save_video(self):
        """
        保存视频文件
        :return:
        """

    def save_to_json(self):
        pass

    def save_to_csv(self):
        """"""

    def save_json_data(self):
        pass


class SaverWithFile(_SaverBase):
    """
    保存为本地文件
    """
    def __init__(self):
        super().__init__()

    def save_img(self):
        pass

    def save_audio(self):
        pass

    def save_video(self):
        pass

    def save_csv(self):
        pass
    pass


class SaverWithOss(_SaverBase):
    pass
