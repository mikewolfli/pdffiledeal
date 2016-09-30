#coding=utf-8
'''
Created on 2016年9月12日

@author: 10256603
'''
import os 
import subprocess
from os.path import isfile,join

ef = 'D:/xpdf/pdftotext.exe'
cfg = 'D:/xpdf/xpdfrc'
file  = 'D:/xpdf/1.pdf'

def convert(file):
    bo = subprocess.check_output([ef,'-f','1','-l','1','-cfg',cfg,'-raw',file,'-'])
    return bo.decode('utf-8')

dr = r'M:\0700 SPEC&GAD'
files = [f for f in os.listdir(dr) if isfile(join(dr,f)) and f.endswith('.pdf')]

for file in files:
    bo = convert(join(dr,file))
    if len(bo)!=0:
        a=bo.split('\r\n')
        b=a[8].split(' ')
        c=a[4].split(' ')
        d=c[1][:10].replace('/','')
        print(d+' '+b[1])
