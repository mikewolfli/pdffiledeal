#coding=utf-8
'''
Created on 2016年9月5日

@author: 10256603
'''
from urllib.request import urlopen
from multiprocessing.dummy import Pool as ThreadPool

urls = [
    'http://www.python.org',
    'http://www.python.org/about/',
    'http://www.python.org/doc/',
    ]

pool=ThreadPool(4)
results=pool.map(urlopen,urls)
'''
for re in results:
    page = re.read()
    print(page.decode('utf-8'))
'''   

pool.close()
pool.join()