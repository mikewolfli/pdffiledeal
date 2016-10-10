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
import ctypes
import ctypes.wintypes
import win32api

def getpath(path):
    ctypes.windll.kernel32.GetShortPathNameW.argtypes = [
        ctypes.wintypes.LPCWSTR, # lpszLongPath
        ctypes.wintypes.LPWSTR, # lpszShortPath
        ctypes.wintypes.DWORD # cchBuffer
        ]
    ctypes.windll.kernel32.GetShortPathNameW.restype = ctypes.wintypes.DWORD

    buf = ctypes.create_unicode_buffer(1024) # adjust buffer size, if necessary
    ctypes.windll.kernel32.GetShortPathNameW(path, buf, len(buf))

    return buf.value   
 
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
#file = r'm:\\E30023919.054_致远•奥林至尊_L9_7952_20160920-1040.pdf'
#file = r'P:\Public\CE\6.Temp\数据组\E30023919.054_致远•奥林至尊_L9_7952_20160920-1040.pdf'
file = r'\\10.126.35.6\Drawing\SJ\Nonstandard Project Files\E30023919.054-057致远•奥林至尊7952\0700 SPEC&GAD\E30023919.054_致远•奥林至尊_L9_7952_20160920-1040.pdf'
fi = getpath(file)
#fi = win32api.GetShortPathName(file)
print(fi)
#file = r'M:\h25yosan2.pdf'
 
print(convert_pdf(file,[1,]))