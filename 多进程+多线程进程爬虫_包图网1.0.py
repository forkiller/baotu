import threading
import time
from multiprocessing import Process
from queue import Queue
import requests
from lxml import etree
from fake_useragent import UserAgent
from tenacity import retry, stop_after_attempt, wait_fixed


class Producter(threading.Thread):
    ua = UserAgent()
    headers = {'User-Agent': ua.random}

    def __init__(self, page_queue, video_queue, *args, **kwargs):
        super(Producter, self).__init__(*args, **kwargs)
        self.page_queue = page_queue
        self.video_queue = video_queue

    def run(self):
        while True:  # 要一直获取页面中的图片img_url,使用while True：
            if (self.page_queue.empty()):  # 判断页面队列是否为空，结束while循环
                break
            url = self.page_queue.get()  # 否则不停从生产者队列中取出数据
            self.get_videoUrl(url)

    def get_videoUrl(self, url):
        response = self.getResponse(url)
        tits, srcs = self.parseHtml(response)
        # print(srcs)
        self.video_queue.put((tits, srcs))

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(3))
    def getResponse(self, url):
        response = requests.get(url, headers=self.headers,timeout=(3,7))
        return response

    def parseHtml(self, response):
        xml = etree.HTML(response.text)
        tits = xml.xpath('//li/div/div/div/a/span[@class="video-title"]/text()')
        srcs = xml.xpath('//li/div/div/a/div/video/@src')
        return tits, srcs


class Consumer(threading.Thread):
    ua = UserAgent()
    headers = {'User-Agent': ua.random}

    def __init__(self, page_queue, video_queue, *args, **kwargs):
        super(Consumer, self).__init__(*args, **kwargs)
        self.page_queue = page_queue
        self.video_queue = video_queue

    def run(self):
        while True:
            """判断img队列是否为空并且判断页面队列是否为空，当两者均为空，说明爬取完成，结束循环"""
            if (self.video_queue.empty() and self.page_queue.empty()):
                break
            tits, srcs = self.video_queue.get()
            self.down_video(tits, srcs)

    def down_video(self, tits, srcs):
        for tit, src in zip(tits, srcs):
            filename = f'D:\\pycharm\\video\\{tit}.mp4'
            response = requests.get(f"http:{src}", headers=self.headers)
            with open(filename, 'wb') as f:
                f.write(response.content)

def main(start,end): # end-start > 线程数
    start,end = pagePart
    page_queue = Queue(30)
    video_queue = Queue(50)

    # print(isinstance(page_queue,Iterable)) # queue 不可迭代

    # 通过 for 循环生成待爬取的网址,1页52个视频，后面页40个
    for page in range(start,end+1):  
        url = f'https://ibaotu.com/shipin/7-0-0-0-0-{page}.html'
        # 将 url 添加到 page 队列中
        page_queue.put(url)

    # 通过循环创建线程，这里创建的消费者线程
    for i in range(5):
        t = Producter(page_queue, video_queue)
        t.start()

    for i in range(5):
        t = Consumer(page_queue, video_queue)
        t.start()


if __name__ == '__main__':
     多进程 + queue多线程
     start = time.time()
     p1 = Process(target=main,args=(1,10))
     p2 = Process(target=main,args=(11,30))
     p1.start()
     p2.start()
     end = time.time()
     print(f'cost time {end - start:0.2f}s') # cost time 78s
