#coding=utf-8
'''
Created on 2016年9月9日

@author: 10256603
'''
from pdfminer.pdfinterp import PDFResourceManager, process_pdf
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from io import StringIO
import time
from functools import wraps
 
def fn_timer(function):
    @wraps(function)
    def function_timer(*args, **kwargs):
        t0 = time.time()
        result = function(*args, **kwargs)
        t1 = time.time()
        print ("Total time running %s: %s seconds" %
                ('test', str(t1-t0))
                )
        return result
    return function_timer

@fn_timer
def convert_pdf(path, pages):
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, laparams=laparams)

    fp = open(path, 'rb')
    process_pdf(rsrcmgr, device, fp,pages)
    fp.close()
    device.close()
    
    str = retstr.getvalue()
    retstr.close()
    return str

#file  = r'm:\E30023919.054_致远奥林至尊_L9_7952_20160920-1040.pdf'
file = r'M:\a.pdf'
 
print(convert_pdf(file,[1,]))