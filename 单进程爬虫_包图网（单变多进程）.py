import time,random
import requests
from lxml import etree
from fake_useragent import UserAgent
from multiprocess.pool import Pool
from tenacity import retry, stop_after_attempt, wait_fixed

headers = {"User-Agent":UserAgent().random}


def get_video(i):
    url = f'https://ibaotu.com/shipin/7-0-0-0-0-{i}.html'
    response = getResponse(url)
    tits, srcs = parseHtml(response)
    down_video(tits, srcs)

def down_video(tits, srcs):
    for tit, src in zip(tits, srcs):
        filename = f'D:/tqdmTest/{tit}.mp4'
        response = requests.get("http:" + src)
        with open(filename, 'wb') as f:
            f.write(response.content)
        print(filename)


@retry(stop=stop_after_attempt(3), wait=wait_fixed(3))
def getResponse(url):
    response = requests.get(url, headers=headers, timeout=(3, 7))
    return response


def parseHtml(response):
    xml = etree.HTML(response.text)
    tits = xml.xpath('//li/div/div/div/a/span[1]/text()')
    srcs = xml.xpath('//li/div/div/a/div/video/@src')
    return tits, srcs


def main(i):
    get_video(i)


if __name__ == '__main__':
    start = time.time()
    """
    由单进程爬虫变为多进程爬虫
    """
    pool = Pool()
    pool.map(main,[i for i in range(11,21)])
    end = time.time()
    print(f'cost time {end -start:0.2f}s')

    # 不用进程池
    # from multiprocessing import Process
    # for i in range(1,11): # 相当于创建了 10 进程
    #     p_getUrl = Process(get_video,args=[i]) # 这样写和单进程一样
    #     p_getUrl.start()

