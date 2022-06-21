#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Time    : 28/04/2022 00:53
# @Author  : Shuyin Ouyang
# @File    : demo.py

import mysql.connector
import pandas as pd
import copy
# mydb=mysql.connector.connect(
#     host="localhost",
#     user="root",
#     passwd="123456",
#     auth_plugin='mysql_native_password',
#     database="health"
# )
# SQL = f"""SELECT
# 	*
# FROM
# 	`input`
# WHERE
# 	age = 51
# 	AND flu_vaccine = '2020-03'
# 	AND imd = 100
# 	"""
# cursor = mydb.cursor()
# cursor.execute(SQL)
# SQL_result = cursor.fetchall()
#
# print(SQL_result)

a = [[0,0,1],
     [0,0,1],
     [1,1,0]]
all_tables = ['patient', 'appointment', 'doctor', 'prescription']

table_connection_matrix = [
    [None,['patient_id','patient_id'],None,None],
    [['patient_id','patient_id'],None,['seenBy','doctor_id'],None],
    [None,['doctor_id','seenBy'],None, None],
    [None, None, None, None]
]

a = pd.DataFrame(a)
table_connection_matrix = pd.DataFrame(table_connection_matrix)
def method(A):
    D = copy.deepcopy(A)
    E = copy.deepcopy(A)
    ilter = [i for i in range(len(A))]
    for o in ilter:
        for d in ilter:
            if d == o:
                D.iloc[o, d] = 0
                E.iloc[o, d] = []
            else:
                if D.iloc[o, d] == None:
                    E.iloc[o, d] = []
            if D.iloc[o, d] == None:
                D.iloc[o, d] = 999
            else:
                D.iloc[o, d] = 1
                if E.iloc[o, d]:
                    E.iloc[o, d] = [[[all_tables[o], E.iloc[o, d][0]],[all_tables[d], E.iloc[o, d][1]]]]
    # D初始化完毕

    # 使用Floyd算法计算SP

    for mid in ilter:
        for o in ilter:
            for d in ilter:
                if D.iloc[o, mid] != 999 and D.iloc[mid, d] != 999 and D.iloc[o, d] > D.iloc[o, mid] + D.iloc[mid, d]:
                    D.iloc[o, d] = D.iloc[o, mid] + D.iloc[mid, d]
                    E.iloc[o, d] = E.iloc[o, mid] + E.iloc[mid, d]
    return E.values