# -*- coding: utf-8 -*-
import multiprocessing
import random
import re
import urllib
from urllib import request

import requests
import time
from multiprocessing import Pool
from requests_html import HTMLSession
from bs4 import BeautifulSoup

session = HTMLSession()


# 获取URL的协议
def url_protocol(url):
    domain = re.findall(r'.*(?=://)', url)
    if domain:
        return domain[0]
    else:
        return url


# 获取URL的域名
def same_url(urlprotocol,url):
    url = url.replace(urlprotocol + '://', '')
    if re.findall(r'^www', url) == []:
        sameurl = 'www.' + url
        if sameurl.find('/') != -1:
            sameurl = re.findall(r'(?<=www.).*?(?=/)', sameurl)[0]
        else:
            sameurl = sameurl + '/'
            sameurl = re.findall(r'(?<=www.).*?(?=/)', sameurl)[0]
    else:
        if url.find('/') != -1:
            sameurl = 'www.' + re.findall(r'(?<=www.).*?(?=/)', url)[0]
        else:
            sameurl = url + '/'
            sameurl = 'www.' + re.findall(r'(?<=www.).*?(?=/)', sameurl)[0]
    print('the domain is：' + sameurl)
    return sameurl


# 随机获取ua
def requests_headers():
    with open('ua.txt', 'r') as k:
        lineslist = [i.strip('\n') for i in k]
    UA = random.choice(lineslist)
    headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'User-Agent':UA,'Upgrade-Insecure-Requests':'1','Connection':'close','Cache-Control':'max-age=0',
    'Accept-Encoding':'gzip, deflate, sdch','Accept-Language':'zh-CN,zh;q=0.8',
    }
    return headers


# 随机获取IP代理
def proxies_dict_get():
    proxies_dict = {}
    url = 'http://api5.uuhttp.com:39005/index/api/return_data?mode=http&count=50&b_time=300&return_type=1&line_break=6&secert=MTMzOTQyMTMwODM6ZGE4NDJmMTc0MTY0YjlhZTdlMWJmOTcyNDcxODM1MDk='
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36 Edg/87.0.664.47'
    }
    response = requests.get(url, timeout=5, headers=headers)
    html = response.text
    a = re.findall('<body><pre style=".*?">(.*?)</pre>', html)
    if a is not None:
        urls = re.findall(r'\d+\.\d+\.\d+\.\d+:+\d*', html)
        if len(urls):
            tmp = random.choice(urls)
            proxies_dict['http'] = 'http://{}'.format(tmp)
            proxies_dict['https'] = 'https://{}'.format(tmp)
    else:
        proxies_dict_get()
    return proxies_dict


# 创建队列，将得到的url都加入到里面，逐个处理
class linkQuence:
    def __init__(self):
        self.visited = []    # 已访问过的url初始化列表
        self.unvisited = []  # 未访问过的url初始化列表
        self.external_url=[]  # 外部链接

    def getVisitedUrl(self):  # 获取已访问过的url
        return self.visited

    def getUnvisitedUrl(self):  # 获取未访问过的url
        return self.unvisited

    def getExternal_link(self):
        return self.external_url   # 获取外部链接地址

    def addVisitedUrl(self,url):  # 添加已访问过的url
        return self.visited.append(url)

    def addUnvisitedUrl(self,url):   # 添加未访问过的url
        if url != '' and url not in self.visited and url not in self.unvisited:
            return self.unvisited.insert(0,url)

    def addExternalUrl(self,url):  # 添加外部链接列表
        if url!='' and url not in self.external_url:
            return self.external_url.insert(0,url)

    def popUnvisitedUrl(self):  # 从未访问过的url中取出一个url
        try:                      # pop动作会报错终止操作，所以需要使用try进行异常处理
            return self.unvisited.pop()
        except:
            return None

    def unvisitedUrlEmpty(self):  # 判断未访问过列表是不是为空
        return len(self.unvisited) == 0


# 整个程序
class Spider():
    def __init__(self, url, domain_url, urlprotocol):
        self.linkQuence = linkQuence()
        self.linkQuence.addUnvisitedUrl(url)   # 将需要爬取的url添加进linkQuence对列中
        self.current_deepth = 1
        self.domain_url = domain_url
        self.urlprotocol = urlprotocol

    def processUrl(self, url):
        global pageLinks
        pageLinks = []
        headers = requests_headers()
        proxies = proxies_dict_get()
        s = requests.session()
        s.keep_alive = False
        try:
            pageSource = session.get(url, timeout=50, proxies=proxies, headers=headers)
            pageSource.html.render()
            pages = pageSource.text
            pageLinks = re.findall(r'(?<=href=\").*?(?=\")|(?<=href=\').*?(?=\')', pages)
        except requests.exceptions.ProxyError:
            print('当前URL代理不可用')
        except requests.exceptions.ConnectionError:
            print('当前URL无法连接')
        except requests.exceptions.ChunkedEncodingError:
            print('网页连接中断')
        except:
            print("未知错误")
        true_url = []
        excludeext = ['.zip', '.rar', '.pdf', '.doc', '.xls', '.jpg', '.mp3', '.mp4', '.png', '.ico', '.gif', '.svg',
                      '.jpeg', '.mpg', '.wmv', '.wma', 'mailto', 'data:image']
        for suburl in pageLinks:
            exit_flag = 0
            for ext in excludeext:
                if ext in suburl:
                    print("break:" + suburl)
                    exit_flag = 1
                    break
            if exit_flag == 0:
                if re.findall(r'/', suburl):
                    if re.findall(r':', suburl):
                        true_url.append(suburl)
                    else:
                        true_url.append(self.urlprotocol + '://' + self.domain_url + '/' + suburl)
                else:
                    true_url.append(self.urlprotocol + '://' + self.domain_url + '/' + suburl)
        for suburl in true_url:
            print('from:' + url + ' get suburl：' + suburl)
        return true_url

    def sameTargetUrl(self,url):
        same_target_url = []
        for suburl in self.processUrl(url):
            if re.findall(self.domain_url,suburl):
                same_target_url.append(suburl)
            else:
                self.linkQuence.addExternalUrl(suburl)
        return same_target_url

    def unrepectUrl(self,url):
        unrepect_url = []
        for suburl in self.sameTargetUrl(url):
            if suburl not in unrepect_url:
                unrepect_url.append(suburl)
        return unrepect_url

    # 入口
    def crawler(self, crawl_deepth):
        self.current_deepth=0
        while self.current_deepth < crawl_deepth:
            if self.linkQuence.unvisitedUrlEmpty():break
            links = []
            while not self.linkQuence.unvisitedUrlEmpty():
                visitedUrl = self.linkQuence.popUnvisitedUrl()
                if visitedUrl is None or visitedUrl == '':
                    continue
                for sublurl in self.unrepectUrl(visitedUrl):
                    links.append(sublurl)
                self.linkQuence.addVisitedUrl(visitedUrl)
            for link in links:
                self.linkQuence.addUnvisitedUrl(link)
            self.current_deepth += 1
            print("已爬取完成深度：", self.current_deepth)
        urllist=[]
        urllist.append("#" * 30 + ' VisitedUrl ' + "#" * 30)
        for suburl in self.linkQuence.getVisitedUrl():
            urllist.append(suburl)
        urllist.append('\n'+"#" * 30 + ' UnVisitedUrl ' + "#" * 30)
        for suburl in self.linkQuence.getUnvisitedUrl():
            urllist.append(suburl)
        urllist.append('\n'+"#" * 30 + ' External_link ' + "#" * 30)
        for sublurl in self.linkQuence.getExternal_link():
            urllist.append(sublurl)
        return urllist


# 写入将得到的urllist写入txt文件
def writelog(log, urllist):
    filename = log
    outfile = open(filename, 'w',encoding="utf-8")
    for suburl in urllist:
        outfile.write(suburl+'\n')
    outfile.close()


# 主程序入口
def kaishi(url, craw_deepth):
    urlprotocol = url_protocol(url)
    domain_url = same_url(urlprotocol, url)
    spider = Spider(url, domain_url, urlprotocol)
    urllist = spider.crawler(craw_deepth)
    writelog(domain_url + '.txt', urllist)


# 将主程序加入多线程模式，加快处理速度
def startCraw(url, craw_deepth):
    print("爬取深度为:", craw_deepth)
    print("程序开始爬取,请等待... ...")
    time_start = time.time()
    pool = Pool(61)
    func = kaishi(url, craw_deepth)
    pool.apply_async(func)
    pool.close()
    pool.join()
    time_end = time.time()
    a = time_end - time_start
    print('爬取结束,总共耗时', a)


# ------------------------爬取百度搜索结果--------------------------------


# url去重
def del_rep():
    readPath = 'old_url.txt'  # 要处理的文件
    writePath = 'url.txt'  # 要写入的文件
    lines_seen = set()
    outfiile = open(writePath, 'a+', encoding='utf-8')
    f = open(readPath, 'r', encoding='utf-8')
    for line in f:
        if line not in lines_seen:
            outfiile.write(line)
            lines_seen.add(line)


# 爬百度专用header
# headers1 = {
#         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:73.0) Gecko/20100101 Firefox/73.0",
#         "Host": "www.baidu.com",
#     }
#
#
# def convert_url(url):
#     try:
#         resp = requests.get(url= url,
#                                 headers=headers1,
#                                 allow_redirects=False
#                                 )
#         return resp.headers['Location']
#     except:
#         print("url error")
#
#
# def paURL(keyword, num):
#     urls = []
#     number = num * 10
#     s = requests.session()
#     for i in range(0, number, 10):  # 翻页
#         url = 'https://www.baidu.com/s'
#         params = {
#             "wd": keyword,
#             "pn": i,
#         }
#         r = s.get(url=url, headers=headers1, params=params)
#         soup = BeautifulSoup(r.text, 'lxml')
#         for so in soup.select('#content_left .t a'):
#             g_url = so.get('href')
#             urls.append(convert_url(g_url))
#         print("第" + str(i/10+1) + "页爬取完成")
#     print("总共" + str(num) + "全部爬取完成！")
#     file = open('old_url.txt', 'a')
#     for var in urls:
#         if 'http' not in str(var):  # 删除没用的url链接
#             print("错误URL，已删除")
#         else:
#             file.writelines(var)
#             file.write('\n')
#     file.close()
#     del_rep()
#     print("写入完成！")

import multiprocessing  # 利用pool进程池实现多进程并行
import time
from bs4 import BeautifulSoup  # 处理抓到的页面
import requests
from urllib import request
import urllib

urlsa = []
headers1 = {
     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:73.0) Gecko/20100101 Firefox/73.0",
     "Host": "www.baidu.com",
    }  # 定义头文件，伪装成浏览器


def paURL(keyword, num):
    url = 'http://www.baidu.com.cn/s?wd=' + urllib.parse.quote(keyword) + '&pn='  # word为关键词，pn是百度用来分页的..
    pool = multiprocessing.Pool(multiprocessing.cpu_count())
    for k in range(1, num):
        result = pool.apply_async(geturl, (url, k))  # 多进程
        print("第" + str(k) + "页爬取完成")
    pool.close()
    pool.join()
    print("总共" + str(num) + "全部爬取完成！")
    print("写入完成！")


def geturl(url, k):
    path = url + str((k - 1) * 10)
    response = request.urlopen(path)
    page = response.read()
    soup = BeautifulSoup(page, 'lxml')
    tagh3 = soup.find_all('h3')
    for h3 in tagh3:
        href = h3.find('a').get('href')
        baidu_url = requests.get(url=href, headers=headers1, allow_redirects=False)
        real_url = baidu_url.headers['Location']  # 得到网页原始地址
        if real_url.startswith('http'):
            urlsa.append(real_url)
            print(urlsa)
    file = open('old_url.txt', 'a')
    for var in urlsa:
        if 'http' not in str(var):  # 删除没用的url链接
            print("错误URL，已删除")
        else:
            file.writelines(var)
            file.write('\n')
    file.close()
    del_rep()

def pachong(deepth):
    with open('url.txt', 'r') as f:
        a = [i.strip('\n') for i in f]
    for i in range(0, len(a)):
        startCraw(a[i], deepth)
    print("全部爬取完成!")
