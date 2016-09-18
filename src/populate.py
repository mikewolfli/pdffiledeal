#!/usr/bin/env python
#coding:utf-8
"""
  Author:   --<>
  Purpose: 
  Created: 2016/3/29
"""

from dataset import *
import random, string

def createRandomStrings(l,n):
    """create list of l random strings, each of length n"""
    names = []
    for i in range(l):
        val = ''.join(random.choice(string.ascii_lowercase) for x in range(n))
        names.append(val)
    return names

def createData(rows=20, cols=5):
    """Creare random dict for test data"""

    data = {}
    names = createRandomStrings(rows,16)
    colnames = createRandomStrings(cols,5)
    for n in names:
        data[n]={}
        data[n]['label'] = n
    for c in range(0,cols):
        colname=colnames[c]
        vals = [round(random.normalvariate(100,50),2) for i in range(0,len(names))]
        vals = sorted(vals)
        i=0
        for n in names:
            data[n][colname] = vals[i]
            i+=1
    return data

def init_database():
    db.connect()
    db.create_tables([filelog,changelog])
    #mbom_db.create_tables([struct_group_code, struct_gc_rel,])
    #nstd_mat_fin.get(nstd_mat_fin.mat_no=='330172045')
    #nstd_mat_fin.delete_instance(nstd_mat_table)
    

def close_database():
    db.close()
    
if __name__ == '__main__':
    init_database()
    close_database()