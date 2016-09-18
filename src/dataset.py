#coding=utf-8
'''
Created on 2016年9月7日

@author: 10256603
'''
from peewee import *

import sys, os

def cur_dir():
    #获取脚本路径
    path = sys.path[0]
    #判断为脚本文件还是py2exe编译后的文件，如果是脚本文件，则返回的是脚本的目录，
    #如果是py2exe编译后的文件，则返回的是编译后的文件路径
    if os.path.isdir(path):
        return path
    elif os.path.isfile(path):
        return os.path.dirname(path)
    
file_catalog=(
        ('PL','装箱清单'),
        ('G','GAD'),
        ('S','Spec Memo'),
    )

db = SqliteDatabase(os.path.join(cur_dir(),'file.db'))
    
class BaseModel(Model):
    class Meta:
        database=db
        
class filelog(BaseModel):
    file = CharField(max_length=64, primary_key=True, db_column='file_id')
    file_flag = CharField(max_length=255)
    aim_dir = TextField()
    from_dir = TextField()
    cur_file = TextField()
    cur_file_modified_on = DateTimeField(formats='%Y-%m-%d %H:%M:%S')
    
    class Meta:
        db_table='file_log'
        
class changelog(BaseModel):
    file = ForeignKeyField(filelog, to_field='file', on_delete='CASCADE')
    f_name = TextField(null=True)
    f_modified = DateTimeField(formats='%Y-%m-%d %H:%M:%S',null=True )
    m_name = TextField()
    m_modified = DateTimeField(formats='%Y-%m-%d %H:%M:%S')
    over_on = DateTimeField(formats='%Y-%m-%d %H:%M:%S')
    
    class Meta:
        db_table='change_log'
        
