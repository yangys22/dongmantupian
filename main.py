import time
import requests
import os
import re
from threading import *
from lxml import etree


class myThread(Thread):
    def __init__(self, func, args=()):
        super(myThread, self).__init__()
        self.func = func
        self.args = args

    def run(self):
        self.result = self.func(*self.args)

    def get_result(self):
        try:
            return self.result  # 如果子线程不使用join方法，此处可能会报没有self.result的错误
        except Exception:
            return None


class Spider:
    file_path = r'G:\pic'
    num = 0

    def get(self, url, lock, flag):
        max_num = 10
        try_num = 0
        while try_num < max_num:
            try:
                response = requests.get(url)
                time.sleep(0.3)
                if flag:
                    lock.release()
                return response
            except:
                try_num += 1
                time.sleep(3)
        if flag:
            lock.release()
        return None

    def get_response(self, url_list):
        tasks = []
        lock = BoundedSemaphore(value=6)
        for url in url_list:
            lock.acquire()
            t = myThread(self.get, (url, lock, True))
            tasks.append(t)
            t.start()
        response_list = []
        for t in tasks:
            t.join()
            response = t.result
            if response is not None:
                response_list.append(response)
        return list(set(response_list))

    def get_page(self):
        url = 'https://www.jder.net/cosplay/page/'
        max_page_num = 185
        url_list = []
        for i in range(max_page_num):
            url_ = url + str(i+1)
            url_list.append(url_)
        response_list = self.get_response(url_list)
        print(len(response_list))
        page_list = []
        for response in response_list:
            html = etree.HTML(response.text)
            L = html.xpath('/html/body/div/div/div/div/div/div/ul/li/div/div/a/@href')
            page_list += L

        page_list = list(set(page_list))
        page_list.sort()
        print(len(page_list))  # 4416
        lock = BoundedSemaphore(value=10)
        lock1 = Lock()
        tasks = []
        for page in page_list:
            lock.acquire()
            t = Thread(target=self.get_img_src, args=(page, lock, lock1))
            tasks.append(t)
            t.start()
        for t in tasks:
            t.join()
    """
    bad_url = [
                    'https://www.jder.net/cosplay/152701.html',
                    'https://www.jder.net/cosplay/152889.html',
                    'https://www.jder.net/cosplay/46418.html',
                    'https://www.jder.net/cosplay/51696.html',
                    'https://www.jder.net/cosplay/62680.html',
                    'https://www.jder.net/cosplay/49119.html',
                    'https://www.jder.net/cosplay/48437.html',
                    'https://www.jder.net/cosplay/44890.html',
                    'https://www.jder.net/cosplay/48208.html',

               ]
    """

    def get_img_src(self, page_url, lock, lock1):
        response = self.get(page_url, None, False)
        if response:
            html = etree.HTML(response.text)
            L = html.xpath('/html/body/div/div[2]/div[1]/div/article/header/h1')
            n = re.findall('\w+', str(L[0].text).replace('Cn', '').replace('摄影', ''))
            name = '_'.join(n)
            L = html.xpath('/html/body/div/div/div/div/article/div/div/p/img/@src')
            L += html.xpath('/html/body/div/div/div/div/article/div/p/img/@src')
            L += html.xpath('/html/body/div/div/div/div/article/div/div/img/@src')
            L += html.xpath('/html/body/div/div/div/div/article/div/div/div/p/img/@src')
            L += html.xpath('/html/body/div/div/div/div/article/div/div/p/a/img/@src')
            L += html.xpath('/html/body/div/div/div/div/article/div/div/div/img/@src')
            L += html.xpath('/html/body/div/div/div/div/article/div/div/ul/li/img/@src')
            L += html.xpath('/html/body/div/div/div/div/article/div/div/div/div/img/@src')
            L += html.xpath('/html/body/div/div/div/div/article/div/div/div/div/div/img/@src')

            if L:
                L = list(set(L))
                name += ('_' + str(len(L)))
                date = {'name': name, 'src_list': L, 'page': page_url}
                self.downlond_pic(date, lock1)
        lock.release()

    def downlond_pic(self, data, lock):
        response_list = self.get_response(data['src_list'])
        lock.acquire()
        print('start download page%d...' % self.num)
        print('name: %s , page: %s' % (data['name'], data['page']), end='\n\n')
        self.num += 1
        os.chdir(self.file_path)
        if not os.path.exists(data['name']):
            os.mkdir(data['name'])
        os.chdir(data['name'])
        # print(response_list)
        num = 0
        for response in response_list:
            num += 1
            with open(str(num) + '.jpg', 'wb') as f:
                f.write(response.content)
        lock.release()

    def run(self):
        self.get_page()


Spider().run()