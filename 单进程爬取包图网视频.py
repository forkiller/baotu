import time
import requests
from lxml import etree
from fake_useragent import UserAgent
from tenacity import retry, stop_after_attempt, wait_fixed

header = {
    "Referer": "https://ibaotu.com/",
    "User-Agent": UserAgent().random}


def get_video(i):
    # TODO: get_video
    url = f'https://ibaotu.com/shipin/7-0-0-0-0-{i}.html'
    response = getResponse(url)
    tits, srcs = parseHtml(response)

    for tit, src in zip(tits, srcs):
        filename = f'D:/tqdmTest/{tit}.mp4'
        response = requests.get(f"http:{src}", headers=header)
        with open(filename, 'wb') as f:
            f.write(response.content)


@retry(stop=stop_after_attempt(3), wait=wait_fixed(3))
def getResponse(url):
    response = requests.get(url, headers=header, timeout=(6, 6))
    return response



def parseHtml(response):
    xml = etree.HTML(response.text)
    tits = xml.xpath('//li/div/div/div/a/span[@class="video-title"]/text()')
    srcs = xml.xpath('//li/div/div/a/div/video/@src')
    return tits, srcs


def main():
    for i in range(1, 3):
        get_video(i)


if __name__ == '__main__':
    start = time.time()
    main()
    end = time.time()
