#coding=utf-8
'''
Created on 2016年9月8日

@author: 10256603
'''
#从本代码的编写中，学到：print语句中，字符串和数字不能相加进行打印；使用逗号打印时会自动在相互之间生成空格，因此最好使用%格式字符串来打印
import os,time
import sys
import datetime
import filecmp

def GetFileInfo(file_path):
    """本函数用来获取指定路径的文件的属性（包括最后访问时间/创建时间/最后修改时间/文件大小）"""
    #首先判断是否是一个有效文件
    if  os.path.isfile(file_path)==False:
        print("不是一个有效文件路径")
        return
    else:
        #下面获取文件信息
        a_info = os.stat(file_path)
        print(a_info)
        atime=os.path.getatime(file_path)
        print(datetime.datetime.fromtimestamp(atime))
        ctime=os.path.getctime(file_path)
        mtime=os.path.getmtime(file_path)
        size=os.path.getsize(file_path)
        #下面处理信息，便于显示
        atime1=time.localtime(atime)
        print(atime1)
        print("文件最后访问时间：%d年%d月%d日  %d时%d分%d秒"  \
        %(atime1[0],atime1[1],atime1[2],atime1[3],atime1[4],atime1[5]))
        #不推荐使用的打印方式：print "文件最后访问时间：",atime1[0],"年",atime1[1],"月"
        ctime1=time.localtime(ctime)
        print("文件创建时间：%d年%d月%d日  %d时%d分%d秒"  \
        %(ctime1[0],ctime1[1],ctime1[2],ctime1[3],ctime1[4],ctime1[5]))        
        mtime1=time.localtime(mtime)
        print("文件最后修改时间：%d年%d月%d日  %d时%d分%d秒"  \
        %(mtime1[0],mtime1[1],mtime1[2],mtime1[3],mtime1[4],mtime1[5])) 
        print("文件大小：",size/1024,"KB")    

GetFileInfo(r'M:\s\E30013186.004-006西安市西兰房地产开发有限责任公司5809\0700 SPEC&GAD\5705-GAD-L57-L60.L73-L74.L83-L84.pdf')
#GetFileInfo("c:/20160223134528.pdf")
#print(filecmp.cmp("c:/20160223134528.pdf", "m:/d.pdf"))