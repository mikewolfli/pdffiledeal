#coding=utf-8
'''
Created on 2016年9月5日

@author: 10256603
'''

from dataset import *
from configparser import ConfigParser
import codecs
import time
from os.path import join,isdir, isfile
import subprocess
import shutil
import datetime
#import glob
#import timeit
from multiprocessing.dummy import Pool as ThreadPool
#import win32api
import ctypes
import ctypes.wintypes

NAME = '装箱单&spec&gad拷贝应用'
PUBLISH_KEY=' R ' #R - release , B - Beta , A- Alpha
VERSION = '0.0.2'

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

def getshortpath(path):
    ctypes.windll.kernel32.GetShortPathNameW.argtypes = [
        ctypes.wintypes.LPCWSTR, # lpszLongPath
        ctypes.wintypes.LPWSTR, # lpszShortPath
        ctypes.wintypes.DWORD # cchBuffer
        ]
    ctypes.windll.kernel32.GetShortPathNameW.restype = ctypes.wintypes.DWORD

    buf = ctypes.create_unicode_buffer(1024) # adjust buffer size, if necessary
    ctypes.windll.kernel32.GetShortPathNameW(path, buf, len(buf))

    return buf.value 
'''              
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
'''
        
class Application():
    def __init__(self,master=None):       
        self.master = master        
        
        if not db.get_conn():
            db.connect()
            
        self.get_dirs()
        
        self.copy_files()
        

    def log_result(self,results):
        now = datetime.datetime.now()
        log_time = now.strftime("%Y-%m-%d %H:%M:%S")
        
        f_file = join(cur_dir(),'operate.log')
        fp = codecs.open(f_file,'a','utf-8')
        fp.write(log_time+'\n')
        for r in results:
            if isinstance(r, dict):
                for t in r.keys():
                    fp.write(str(t)+':'+r[t]+'\n')
            elif isinstance(r, str):
                fp.write(r+'\n')
            elif isinstance(r,list):
                for t in r:
                    fp.write(str(r)+'\n')       
        fp.close()   
        
    def copy_files(self):
        start = time.time()
        #dirs =  [ d for d in os.listdir(self.s_dir) if isdir(join(self.s_dir, d)) ]
        dirs =  os.listdir(self.s_dir)
        total = len(dirs)
        
        print('获得原文件夹下所有文件夹清单,共计 '+str(total)+' 个文件夹.')
        self.spec_str=[]
      
        results= pool.map(self.deal_dir, dirs)
        
        finish = time.time()
        cost = finish-start         

        r_str = ' 本次操作：'+str(total)+' 个文件夹, 用时'+str(cost)+' 秒 \n'
        results.append(r_str)
        print(r_str)
        self.log_result(results)
                 
    def deal_dir(self, dr):
        if not isdir(join(self.s_dir,dr)):
            return {dr:'跳过文件,原因非目录！'}
            
        dr = join(self.s_dir, dr, self.pl_dir)
        #print('正在处理文件夹：'+dr)
        #files = [f for f in os.listdir(dr) if isfile(join(dr,f)) and f.endswith('.pdf')]
        files = os.listdir(dr)
        
        copies=[]   
        aim_dir = self.scan_files(dr, files, copies)
            
        if len(aim_dir)==0:
            return {dr:'装箱清单未生成或文件名含不可识别的字符，故跳过文件夹'}
            
        if len(copies)==0:
            return {dr:'没有待处理文件，故跳过'}
                     
        self.copy_file(dr,aim_dir,copies)
        print(' 文件夹:'+dr+'处理完成，共计拷贝'+str(len(copies))+'个文件')
        
        return {dr:'文件处理完成.'}
                                  
    def scan_files(self, dr, files, copies):              
        aim_dir = ''
        for file in files:
            if not (isfile(join(dr,file)) and file.endswith('.pdf')):
                continue
            
            accord = self.parse_pdf(dr, file)
            if accord is None:
                continue
            
            if accord['dir'] is not None:
                aim_dir = accord['dir']

            if not self.check_flag(dr, accord,copies) :
                copies.append(accord)
                         
        return aim_dir

    def check_flag(self, dr, res, copies):
        for r in copies:
            if r['flag']==res['flag']:
                r_time = os.path.getmtime(join(dr,r['file']))
                a_time = os.path.getmtime(join(dr,res['file']))
                if a_time >r_time:
                    copies.remove(r)
                    copies.append(res)
                                       
                return True
        
        return False     
    
    def copy_file(self, dr, aim, copies):
        aim_path = join(self.a_dir, aim)
        source_path = join(self.s_dir, dr)
        
        if not os.path.exists(aim_path):
            try:
                os.makedirs(aim_path)
            except PermissionError as e:
                print('error:%s'%e)
                return 
               
        for r in copies:
            self.cmp_file(source_path, aim_path, r)
    
    def make_copy_log(self, source, aim,res, a_list, s_time):                
    #def make_copy_log(self, source, aim,res, a_list, s_time, a_time=None):
        over_on = datetime.datetime.now()
        ##数据库比较
        if len(a_list)==0:
            r = filelog.select(fn.Count().alias('count')).get()
            f = r.count
            file = 'F'+str(f+1)
            q = filelog.create(file=file,file_flag=res['flag'],from_dir=source,aim_dir=aim,cur_file=res['file'],cur_file_modified_on=s_time)
            if q.file==file:
                changelog.insert(file=file,m_name=res['file'],m_modified=s_time, over_on=over_on).execute()   
        else:
            file =res['flag']
            q = filelog.update(cur_file=res['file'], cur_file_modified_on=s_time).where(filelog.file_flag==file)

            if q.execute()>0:
                changelog.insert(file=file,f_name=a_list[0],f_modified=a_list[1],m_name=res['file'],m_modified=s_time, over_on=over_on).execute()    
            
        #文件比较, 文件在网络服务器上，同时搜索源目录和目标目录，改进算法仅搜索源目录，目标文件名均保存在数据库中
        '''
        if len(a_list)!=0:
            a_file = os.path.split(a_list[0])

        try:
            r = filelog.get(filelog.file_flag==res['flag'])
            
            file = r.file
            q = filelog.update(cur_file=res['file'], cur_file_modified_on=s_time).where(filelog.file==file)
            if q.execute()>0:
                if len(a_list)==0:
                    changelog.insert(file=file,m_name=res['file'],m_modified=s_time, over_on=over_on).execute()   
                else:
                    changelog.insert(file=file,f_name=a_file[1],f_modified=a_time,m_name=res['file'],m_modified=s_time, over_on=over_on).execute()          
        except filelog.DoesNotExist:
            r = filelog.select(fn.Count().alias('count')).get()
            f = r.count
            file = 'F'+str(f+1)
            q = filelog.create(file=file,file_flag=res['flag'],from_dir=source,aim_dir=aim,cur_file=res['file'],cur_file_modified_on=s_time)
            if q.file==file:
                if len(a_list)==0:
                    changelog.insert(file=file,m_name=res['file'],m_modified=s_time, over_on=over_on).execute()   
                else:
                    changelog.insert(file=file,f_name=a_file[1],f_modified=a_time,m_name=res['file'],m_modified=s_time, over_on=over_on).execute()  
        '''

    def cmp_file(self, source, aim, res): #0-目标文件不存在，1-目标文件更改日期<原文件，2-目标文件更改日期>=原文件
        #文件比较, 文件在网络服务器上，故慢
        ''' 
        s_file = join(source,res['file'])
        s_mtime = datetime.datetime.fromtimestamp(os.path.getmtime(s_file))
        file = res['flag']+'*.pdf'
        a_list = glob.glob(join(aim,file))
        if len(a_list)==0:
            #a_file = join(aim, res['file'])
            try:
                shutil.copy2(s_file, aim)
            except IOError as e:
                logger.error('IOError:%s'%e)
                return -1
            
            self.make_copy_log(source, aim, res, a_list,s_mtime)
            return 0
        
        a_file = join(aim, a_list[0])
        a_mtime = datetime.datetime.fromtimestamp(os.path.getmtime(a_file))
        if s_mtime<=a_mtime:
            return 2
        else:
            try:
                os.remove(a_file)
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise 
                            
            try:
                shutil.copy2(s_file,aim)
            except IOError as e:
                logger.error('IOError:%s'%e)
                return -1
            
            self.make_copy_log(source,aim, res, a_list,s_mtime, a_mtime)
            return 1
        '''
        #数据库比较
        s_file = join(source,res['file'])
        s_mtime = datetime.datetime.fromtimestamp(os.path.getmtime(s_file))
        a_list = []
        try:
            r = filelog.get(filelog.file_flag==res['flag'])
            a_file = r.cur_file
            a_list.append(a_file)
            a_time = r.cur_file_modified_on
            a_list.append(a_time)
            
            if s_mtime>datetime.datetime.strptime(a_time,'%Y-%m-%d %H:%M:%S.%f'):
                try:
                    os.remove(join(aim,a_file))
                except OSError as e:
                    print('IOerror:%s'%e)
                    return -1
                            
                try:
                    shutil.copy2(s_file,aim)
                except IOError as e:
                    print('IOerror:%s'%e)
                    return -1
            
                self.make_copy_log(source,aim, res, a_list,s_mtime)
                return 1
            else:
                return 2
        except filelog.DoesNotExist:
            try:
                shutil.copy2(s_file, aim)
            except IOError as e:
                print('IOError:%s'%e)
                return -1
            
            self.make_copy_log(source, aim, res, a_list,s_mtime)
            return 0
                  
    def parse_pdf(self,dr, file):
        res = {}
        pdf = join(dr,file)
        
        try:
            fi = pdf.encode(encoding='gbk',errors='strict')
            pdffile=pdf
        except UnicodeEncodeError:
            #pdffile = win32api.GetShortPathName(pdf)
            pdffile = getshortpath(pdf)
        
        try:
            re = subprocess.check_output([pdf2text_exe,'-f','1','-l','1','-cfg',cfg,'-raw',pdffile,'-'], shell=True,stderr=subprocess.STDOUT)            
        except subprocess.CalledProcessError as e:
            print('Calledprocerr: %s'%e)
            return None
                  
        re = re.decode('utf-8')

        if file.lower().find('gad')!=-1 or file.lower().find('spec')!=-1:
            res['flag']=self.get_file_flag(file, '更新')
            res['file']=file
            res['dir']=None
        elif len(re)!=0:
        #if len(re)!=0:
            ra = re.split('\r\n')
            if ra[3]=='Packing List':
                ar = ra[4][-14:]
                prj = ar[:10].replace('/','')
                arn = ra[8][5:]
                prj_name = arn
                prj_name=prj_name.replace('/','')
                prj_name=prj_name.replace('\\','')
                res['flag']=self.get_file_flag(file, '_')
                res['file']=file
                res['dir']= prj+' '+prj_name
            else:
                return None
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
        config.readfp(codecs.open('path.cfg', "r", "utf-8"))
        para  = config._sections['path']
        self.s_dir = para['source']
        self.a_dir = para['aim']
        self.pl_dir = para['pl_dir']           

if __name__ == '__main__':
    pool = ThreadPool(4)         
    app=Application()
    
    if db.get_conn():
        db.close()    
    pool.close()
    pool.join()