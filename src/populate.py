#!/usr/bin/env python
#coding:utf-8
"""
  Author:   --<>
  Purpose: 
  Created: 2016/3/29
"""

from dataset import *
import random, string

def init_database():
    db.connect()
    db.create_tables([filelog,changelog,counter])
    counter.create(counter_id='c1', current_counter=1,step=1,pre_char='F')
    #mbom_db.create_tables([struct_group_code, struct_gc_rel,])
    #nstd_mat_fin.get(nstd_mat_fin.mat_no=='330172045')
    #nstd_mat_fin.delete_instance(nstd_mat_table)
    

def close_database():
    db.close()
    
if __name__ == '__main__':
    init_database()
    close_database()