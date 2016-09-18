#coding=utf-8
'''
Created on 2016年9月5日

@author: 10256603
'''

from dataset import *

from tkinter import *
from tkinter import simpledialog
from tkinter import font
from tkinter import scrolledtext
import logging
import threading
from configparser import ConfigParser
from asyncio.log import logger
import time
from os.path import join,isdir, isfile
import subprocess
import shutil
import datetime
import glob
import timeit

NAME = '装箱单&spec&gad拷贝应用'
PUBLISH_KEY=' R ' #R - release , B - Beta , A- Alpha
VERSION = '0.0.1'

logger = logging.getLogger()
pdf2text_exe = r'D:\xpdf\pdftotext.exe'
cfg = r'D:\xpdf\xpdfrc'

def cur_dir():
    #获取脚本路径
    path = sys.path[0]
    #判断为脚本文件还是py2exe编译后的文件，如果是脚本文件，则返回的是脚本的目录，
    #如果是py2exe编译后的文件，则返回的是编译后的文件路径
    if os.path.isdir(path):
        return path
    elif os.path.isfile(path):
        return os.path.dirname(path)

class TextHandler(logging.Handler):
    """This class allows you to log to a Tkinter Text or ScrolledText widget"""
    def __init__(self, text):
        # run the regular Handler __init__
        logging.Handler.__init__(self)
        # Store a reference to the Text it will log to
        self.text = text

    def emit(self, record):
        self.formatter = logging.Formatter('%(asctime)s-%(levelname)s : %(message)s')
        msg = self.format(record)
        def append():
            self.text.configure(state='normal')          
            self.text.insert(END, msg+"\n")
            self.text.configure(state='disabled')
            # Autoscroll to the bottom
            self.text.yview(END)
        # This is necessary because we can't modify the Text from other threads
        self.text.after(0, append)# Scroll to the bottom
               
threadLock = threading.Lock()
class refresh_thread(threading.Thread):
    def __init__(self, frame, typ=None):
        threading.Thread.__init__(self)
        self.frame=frame
        self.type=typ
               
    def run(self):
        threadLock.acquire()
        self.frame.copy_files()
        threadLock.release() 
        
class Application(Frame):
    copy_thread=None
    def __init__(self,master=None):
        Frame.__init__(self, master)
        self.pack()
        
        self.master = master        
        self.create_widgets()
        
        if not db.get_conn():
            db.connect()
            
        self.get_dirs()
        
        self.start_thread()
             
    def create_widgets(self):
        self.log_label=Label(self)
        self.log_label["text"]="后台操作记录"
        self.log_label.grid(row=0,column=0, sticky=W)
        self.log_text=scrolledtext.ScrolledText(self, state='disabled')
        self.log_text.config(font=('TkFixedFont', 10, 'normal'))
        self.log_text.grid(row=1, column=0, rowspan=4, columnspan=6, sticky=NSEW)
        self.min_button=Button(self, text='最小化')
        self.min_button.grid(row=0, column=4)
        self.min_button['command']=self.minimize
        self.close_button=Button(self, text='关闭')
        self.close_button.grid(row=0, column=5)
        self.close_button['command']=self.quit_func
        
        # Create textLogger
        text_handler = TextHandler(self.log_text)        
        # Add the handler to logger
        
        logger.addHandler(text_handler)
        
        hdlr = logging.FileHandler(join(cur_dir(),'op.log'))
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        hdlr.setFormatter(formatter)
        logger.addHandler(hdlr)
              
        logger.setLevel(logging.INFO) 
        
        self.rowconfigure(3, weight=1)
        self.columnconfigure(1, weight=1) 
        
    def minimize(self):
        self.master.iconify()

    def quit_func(self):        
        if db.get_conn():
            db.close()
            
        sys.exit() 
        
    def copy_files(self):
        start = time.time()
        dirs =  [ d for d in os.listdir(self.s_dir) if isdir(join(self.s_dir, d)) ]
        logger.info('获得原文件夹下所有文件夹清单,共计 '+str(len(dirs))+' 个文件夹.')
        
        for dr in dirs:
            dr = join(self.s_dir, dr, self.pl_dir)
            files = [f for f in os.listdir(dr) if isfile(join(dr,f)) and f.endswith('.pdf')]
            logger.info('扫描文件夹'+dr+',共计文件'+str(len(files)))
            aim_dir = self.scan_files(dr, files)
            
            if len(aim_dir)==0:
                logger.warning('装箱清单未生成，故跳过文件夹'+dr)
                continue
            
            if len(self.copies)==0:
                logger.warning('文件夹:'+dr+'没有待处理文件，故跳过')
                continue
            
            logger.info('待处理文件数:'+str(len(self.copies)))
            
            logger.info('正在拷贝文件...')
            self.copy_file(dr,aim_dir)
            logger.info('文件夹:'+dr+'下文件处理完成.')
        
        finish = time.time()
        cost = finish-start 
        logger.info('本次任务处理完成。用时：'+str(cost)+'秒，任务ID'+self.copy_thread.getName()+'\n')
                       
    def scan_files(self, dr, files):
        self.copies = []
        
        aim_dir = ''
        for file in files:
            accord = self.parse_pdf(dr, file)
            if accord is None:
                continue
            
            if accord['dir'] is not None:
                aim_dir = accord['dir']

            if not self.check_flag(dr, accord) :
                self.copies.append(accord)
                            
        return aim_dir

    def check_flag(self, dr, res):
        for r in self.copies:
            if r['flag']==res['flag']:
                r_time = os.path.getmtime(join(dr,r['file']))
                a_time = os.path.getmtime(join(dr,res['file']))
                if a_time >r_time:
                    self.copies.remove(r)
                    self.copies.append(res)
                                       
                return True
        
        return False     
    
    def copy_file(self, dr, aim):
        aim_path = join(self.a_dir, aim)
        source_path = join(self.s_dir, dr)
        
        if not os.path.exists(aim_path):
            os.makedirs(aim_path)
        
        for r in self.copies:
            self.cmp_file(source_path, aim_path, r)
                    
    def make_copy_log(self, source, aim,res, a_list, s_time, a_time=None):
        over_on = datetime.datetime.now()

        try:
            r = filelog.get(filelog.file_flag==res['flag'], filelog.from_dir==source)
            
            file = r.file
            q = filelog.update(cur_file=res['file'], cur_file_modified_on=s_time).where(filelog.file==file)
            if q.execute()>0:
                if len(a_list)==0:
                    changelog.insert(file=file,m_name=res['file'],m_modified=s_time, over_on=over_on).execute()   
                else:
                    changelog.insert(file=file,f_name=a_list[0],f_modified=a_time,m_name=res['file'],m_modified=s_time, over_on=over_on).execute()          
        except filelog.DoesNotExist:
            r = filelog.select(fn.Count().alias('count')).get()
            f = r.count
            file = 'F'+str(f+1)
            q = filelog.create(file=file,file_flag=res['flag'],from_dir=source,aim_dir=aim,cur_file=res['file'],cur_file_modified_on=s_time)
            if q.file==file:
                if len(a_list)==0:
                    changelog.insert(file=file,m_name=res['file'],m_modified=s_time, over_on=over_on).execute()   
                else:
                    changelog.insert(file=file,f_name=a_list[0],f_modified=a_time,m_name=res['file'],m_modified=s_time, over_on=over_on).execute()  

    def cmp_file(self, source, aim, res): #0-目标文件不存在，1-目标文件更改日期<原文件，2-目标文件更改日期>=原文件
        s_file = join(source,res['file'])
        s_mtime = datetime.datetime.fromtimestamp(os.path.getmtime(s_file))
        file = res['flag']+'*.pdf'
        a_list = glob.glob(join(aim,file))
        if len(a_list)==0:
            a_file = join(aim, res['file'])
            shutil.copyfile(s_file, a_file)
            self.make_copy_log(source, aim, res, a_list,s_mtime)
            return 0
        
        a_file = join(aim, a_list[0])
        a_mtime = datetime.datetime.fromtimestamp(os.path.getmtime(a_file))
        if s_mtime<=a_mtime:
            return 2
        else:
            shutil.copyfile(source,aim)
            self.make_copy_log(source,aim, s_mtime, a_mtime)
            return 1
                   
    def parse_pdf(self,dr, file):
        res = {}
        pdf = join(dr,file)
        try:
            re = subprocess.check_output([pdf2text_exe,'-f','1','-l','1','-cfg',cfg,'-raw',pdf,'-'])            
        except subprocess.CalledProcessError as e:
            logger.error('Calledprocerr:'+e.output.decode('utf-8'))
            return None
            
        re = re.decode('utf-8')

        if file.lower().find('gad')!=-1 or file.lower().find('spec')!=-1:
            res['flag']=self.get_file_flag(file, '更新')
            res['file']=file
            res['dir']=None
        elif len(re)!=0:
        #if len(re)!=0:
            ra = re.split('\r\n')
            ar = ra[4].split(' ')
            prj = ar[1][:10].replace('/','')
            ar = ra[8].split(' ')
            prj_name = ar[1]
            res['flag']=self.get_file_flag(file, '_')
            res['file']=file
            res['dir']= prj+' '+prj_name
        else:
            return None
        
        return res
        
    def get_file_flag(self,file_name, sp):
        pos = file_name.rfind(sp)
        if pos ==-1:
            return file_name[:-4]
        else:
            return file_name[:pos]
                           
    def get_dirs(self):
        config = ConfigParser()
        config.read('path.cfg')
        para  = config._sections['path']
        self.s_dir = para['source']
        self.a_dir = para['aim']
        self.pl_dir = para['pl_dir']
          
    def start_thread(self):
        if self.copy_thread is not None:
            while self.copy_thread.is_alive():
                logger.warning('后台进程尚未结束，5分钟后继续...')
                time.sleep(300)         
        
        logger.info('整理进程启动...')
        self.copy_thread = refresh_thread(self)
        self.copy_thread.setDaemon(True)
        self.copy_thread.start()  
        
        self.after(14400000, self.start_thread)               

if __name__ == '__main__':   
    root=Tk() 
    #root.resizable(0, 0)
    root.wm_state('iconic')        
    root.title(NAME+PUBLISH_KEY+VERSION)
    default_font = font.nametofont("TkDefaultFont")
    default_font.configure(size=10)  
    root.option_add("*Font", default_font)
    app=Application(root)
    
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    app.grid(row=0, column=0, sticky =NSEW)
    root.geometry('800x600')
    root.mainloop()
    root.destroy()