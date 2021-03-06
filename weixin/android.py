# -*- coding:utf-8  -*-
# @Time     : 2021-04-04 18:30
# @Author   : BGLB
# @Software : PyCharm
import os
import re
import sys
from _md5 import md5
from datetime import timedelta

import jieba
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from numpy import histogram
from pysqlcipher3 import dbapi2 as sqlite
from wordcloud import WordCloud

from crawler.Android import CrawlerAndroid
from weixin.wechat.common.textutil import safe_filename, ensure_unicode
from weixin.wechat.parser import WeChatDBParser
from weixin.wechat.render import HTMLRender
from weixin.wechat.res import Resource


class Crawler(CrawlerAndroid):

    def __init__(self, crawlerConfig):
        super().__init__(crawlerConfig)
        self.app_info = {
            'PackageName': 'com.tencent.mm',
            'Activity': 'com.tencent.mm.app.WeChatSplashActivity',
            'IsReset': False,
            'IsWait': True,
            'AppName': '微信'
        }
        self.is_start_app = False
        import weixin.wechat
        from weixin.wechat import msg
        from weixin.wechat import res
        res.logger = self.log.get_logger()
        msg.logger = self.log.get_logger()
        weixin.wechat.logger = self.log.get_logger()

        self.is_decrypt = False
        self.uin = '-585799781'
        self.imei = ['86690603268572', '866906032685720', '866906032685738', '86679004148521', '866790041485219',
                     '866790041485227']
        self.decrypt_db_path = os.path.join(self.base_dir, 'decrypted.db')
        self.resource_path = os.path.join(self.base_dir, 'resource')
        self.src_db_path = os.path.join(self.base_dir, 'src.db')
        self.html_path = os.path.join(self.data_dir, '高敏洁.html')
        self.txt_path = os.path.join(self.base_dir, '高敏洁.txt')

    def saver(self):
        pass
        # pass

    def spider(self):
        if self.is_decrypt:
            for i in self.imei:
                key = self.get_key(i)

                if self.do_decrypt(self.decrypt_db_path, key):
                    self.log.info(self.uin, i)
                    break
        self.log.info('resource_path: {}'.format(self.resource_path))
        parser = WeChatDBParser(self.decrypt_db_path)
        chats = parser.msgs_by_chat.keys()
        chat_list = [{parser.contacts[k]: k} for k in chats]
        self.log.info(chat_list)
        # self.parse_msg_txt('高敏洁')
        # self.parse_msg_html('高敏洁')
        #
        # self.parse_msg_img('高敏洁')
        self.parse_msg_ciyun()

    def get_key(self, imei: str):
        """
            获取数据库密码
            密码为：IMEI与UIN组成的字符串进行MD5加密，然后取前7位
        :return:
        """
        s = imei+self.uin
        m2 = md5()
        m2.update(s.encode())
        return m2.hexdigest()[:7]

    def do_decrypt(self, output, key):
        """
        :param output:
        :param key:
        :return:
        """

        conn = sqlite.connect(self.src_db_path)
        c = conn.cursor()
        c.execute("PRAGMA key = '"+key+"';")
        try:
            c.execute("PRAGMA cipher_use_hmac = OFF;")
            # c.execute("PRAGMA cipher_page_size = 1024;")
            c.execute("PRAGMA kdf_iter = 4000;")
            c.execute('ATTACH DATABASE "{}" AS db KEY {};'.format(output, '""'))
        except Exception as e:
            self.log.error(f"Decryption failed: '{e}'")
            os.unlink(output)
            return False

        self.log.info(f"Decryption succeeded! Writing database to {output} ...")
        c.execute("SELECT sqlcipher_export('db');")
        c.execute("DETACH DATABASE db;")
        c.close()
        return True

    def parse_msg_txt(self, user_name):
        """
            解析数据库文本
        :param user_name:
        :return:
        """
        self.log.info(self.decrypt_db_path)
        if not os.path.exists(self.decrypt_db_path):
            self.log.info('不存在解密后的数据库')
            return
        parser = WeChatDBParser(self.decrypt_db_path)

        for chatid, msgs in parser.msgs_by_chat.items():
            name = parser.contacts[chatid]
            if len(name) == 0:
                self.log.info(f"Chat {chatid} doesn't have a valid display name.")
                name = str(id(chatid))
            if user_name and user_name == name:
                self.log.info(f"Writing msgs for {name}")
                safe_name = safe_filename(name)
                outf = os.path.join(self.data_dir, safe_name+'.txt')
                with open(outf, 'w', encoding='utf8') as f:
                    for m in msgs:
                        f.write(str(m))
                        f.write("\n")
                self.log.info('写入成功{}'.format(name))

    def parse_msg_html(self, user_name):
        """
         解析生成html
        :param user_name:
        :return:
        """
        parser = WeChatDBParser(self.decrypt_db_path)
        try:
            chatid = parser.get_chat_id(user_name)
        except KeyError:
            sys.stderr.write(u"Valid Contacts: {}\n".format(
                u'\n'.join(parser.all_chat_nicknames)))

            sys.stderr.write(u"Couldn't find the chat {}.".format(user_name))

            sys.exit(1)
        res = Resource(parser, self.resource_path, 'avatar.index')
        msgs = parser.msgs_by_chat[chatid]
        self.log.info(f"Number of Messages for chatid {chatid}: {len(msgs)}")
        assert len(msgs) > 0

        render = HTMLRender(parser, res)
        htmls = render.render_msgs(msgs)
        output_file = self.html_path
        if len(htmls) == 1:
            with open(output_file, 'w', encoding='utf8') as f:
                f.write(htmls[0])
        else:
            assert output_file.endswith(".html")
            basename = output_file[:-5]
            for idx, html in enumerate(htmls):
                with open(basename+f'{idx:02d}.html', 'w', encoding='utf8') as f:
                    f.write(html)
        res.emoji_reader.flush_cache()

    def parse_msg_img(self, user_name):
        """
            聊天历史统计图
        :param user_name:
        :return:
        """
        db_file = self.decrypt_db_path
        name = ensure_unicode(user_name)
        print(name)
        every_k_days = 1
        parser = WeChatDBParser(db_file)
        chat_id = parser.get_chat_id(user_name)
        msgs = parser.msgs_by_chat[chat_id]
        times = [x.createTime for x in msgs]
        start_time = times[0]
        diffs = [(x-start_time).days for x in times]
        max_day = diffs[-1]
        labels = list(set([(start_time+timedelta(x)).strftime("%m/%d") for x in diffs]))
        labels.sort()
        x_index = [i for i in range(len(labels))]
        diff_hist = histogram(diffs, bins=int(max_day/every_k_days))
        self.log.info('x: {}'.format(labels))
        self.log.info(diff_hist)
        self.log.info("{}, {}".format(len(diff_hist[0]), len(diff_hist[1])))

        chart_name = 'Chat statistics'
        fig = plt.figure(chart_name, figsize=(15, 8))
        plt.rcParams['font.sans-serif'] = ["SimHei"]  # 防止画图中文乱码
        plt.rcParams['axes.unicode_minus'] = False
        plt.title(chart_name)
        plt.bar(diff_hist[1][:-1], diff_hist[0], width=0.5)
        plt.xticks(x_index, labels)
        plt.xlabel("Date")
        plt.ylabel("Number of msgs in k days")

        file_name = self.img_dir+'/聊天統計圖.jpg'
        plt.savefig(file_name)

    def parse_msg_ciyun(self):
        """
            解析聊天文本 生成词云
        :param username:
        :return:
        """
        with open(self.txt_path, 'r', encoding='utf8') as f:
            src_txt = []
            re_list = [re.compile(r"[^a-zA-Z]\d+"), re.compile(r"\s+"),
                       re.compile(r"[^0-9A-Za-z\u4e00-\u9fa5]")]

            for i in f.readlines():
                try:
                    item = i.split(':')[4]
                except:
                    self.log.info(i)
                    item = ''
                if item.startswith('URL') or item.startswith('wxid') or item.startswith('<'):
                    continue

                for reg in re_list:
                    text = reg.sub("", item)
                    if text:
                        src_txt.append(text)
        self.log.info('len : {}'.format(len(src_txt)))
        fig = plt.figure("聊天词云", figsize=(15, 10))
        fig.patch.set_facecolor('#384151')
        alice_mask = np.array(Image.open(os.path.join(self.base_dir, "back.jpg")))
        wordcloud = WordCloud(
            font_path=os.path.join(self.base_dir, "simkai.ttf"),  # 字体的路径
            width=1000, height=1000,  # 设置宽高
            background_color='white',  # 图片的背景颜色
            mask=alice_mask,
            stopwords=['捂脸', '你', '我', '苦涩',
                       '嗯嗯', '了', '的', '感觉',
                       '是', '那', '就', '嗯', '不', '都', '把', '说',
                       '这', '也', '吗', '在', '给', '有', '吧', ],
        ).generate(" ".join(jieba.cut((''.join(src_txt).encode('utf8')))))

        plt.title('聊天记录词云', fontsize=20)
        # plt.tof(wordcloud.generate(" ".join(src_txt)), interpolation='bilinear')
        plt.axis("off")
        wordcloud.to_file(os.path.join(self.data_dir, '词云图.jpg'))
