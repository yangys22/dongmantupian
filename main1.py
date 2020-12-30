import datetime
import hashlib
import os
import asyncio
import aiohttp

md5_list = []
num = 0


async def download():
    global num
    global md5_list
    url = 'http://setu.awsl.ee/api/setu!'
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as req:
                await asyncio.sleep(1)
                img = await req.read()
                md5 = hashlib.md5(img).hexdigest()
                if md5 not in md5_list:
                    md5_list.append(md5)
                    l = round(len(img) / 1024, 2)
                    if l < 1024:
                        s = str(l)+'k'
                    else:
                        l = round(l / 1024, 2)
                        s = str(l)+'m'
                    if num % 50 == 0:
                        print('下载第%7d张,%8s' % ((num + 1), s))
                    num += 1
                    with open(str(num) + '.jpg', 'wb') as f:
                        f.write(img)
    except Exception as e:
        print('\033[31m[!]'+str(e)+'\033[0m')
        await asyncio.sleep(6)



def run():
    try:
        os.chdir('setu1')
    except:
        os.mkdir('setu1')
        os.chdir('setu1')
    flag = True
    n = 0
    while flag:
        tasks = []
        for i in range(50):
            task = asyncio.ensure_future(download())
            tasks.append(task)
        global md5_list
        l = len(md5_list)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.wait(tasks))
        if l == len(md5_list):
            n += 1
            if n > 20:
                flag = False


if __name__ == '__main__':
    s = datetime.datetime.now()
    run()
    e = datetime.datetime.now()
    print(e-s)
