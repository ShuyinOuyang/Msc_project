#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Time    : 28/04/2022 20:33
# @Author  : Shuyin Ouyang
# @File    : attribute_anlysis.py

import pandas as pd
import itertools as it
import mysql.connector
import argparse

# the condition number in WHERE statement
N = 3
database = 'input'
# path = './data/input.csv'
path = './data/multi_table/patient.csv'

def read_table(path):
    df = pd.read_csv(path)
    columns = [column for column in df]
    values = {}
    for column in columns:
        if column == 'patient_id':
            continue
        tmp_dict = dict(df.loc[:, column].value_counts())
        tmp_dict = sorted(tmp_dict.items(), key=lambda x: x[1], reverse=False)
        values[column] = tmp_dict
    return values


# simple condition, i.e. attribute=value
conditions = []

# one WHERE condition i.e. WHERE a='xxx'
def generate_all_SQL_with_one_constrain(path):
    values = read_table(path)
    condition_1 = []
    for key in values:
        for i in range(len(values[key])):
            condition_1.append('%s=%s' % (key, values[key][i][0]))

    SQL_1 = []
    for i in range(len(condition_1)):
        SQL_template = 'SELECT %s FROM %s WHERE %s' % ('patient_id', database, condition_1[i])
        SQL_1.append(SQL_template)
    return SQL_1

# multiple WHERE condition i.e. WHERE a='xxx' AND b='xxx' AND ...
def generate_all_SQL_with_multiple_constrain(N, path):
    values = read_table(path)
    SQL_2 = []
    attributes = list(values.keys())
    for n in range(N):
        combination = list(it.combinations(attributes, n+1))
        for comb in combination:
            arg = []
            # print(list(values[comb[i]] for i in range(len(comb))))
            for i in range(len(comb)):
                arg.append(values[comb[i]])
            product = list(it.product(*arg))
            for prod in product:
                WHERE = []
                for i in range(len(comb)):
                    condition_ = '%s=\'%s\'' % (comb[i], prod[i][0])
                    WHERE.append(condition_)
                where = ' AND '.join(i for i in WHERE)
                SQL_template = 'SELECT %s FROM %s WHERE %s' % ('patient_id', database, where)
                SQL_2.append(SQL_template)
    return SQL_2


# def generate_all_SQL_with_multiple_constrain_in_multiple_table(paths):
paths = ['./data/multi_table/patient.csv', './data/multi_table/doctor.csv']
foreign_keys = {'patient.doctor_id': 'doctor.doctor_id'}

values0 = read_table(paths[0])
values1 = read_table(paths[1])


# apply SQL to database
def SQL_database(SQLs):
    # input: SQL list
    # output: SQL with unique executed record
    SQL_unique = []
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="123456",
        auth_plugin='mysql_native_password',
        database="health"
    )


    for SQL in SQLs:
        cursor = mydb.cursor()
        try:
            cursor.execute(SQL)
        except Exception:
            print(1,SQL)
            break
        SQL_result = cursor.fetchall()
        if len(SQL_result) == 1:
            SQL_unique.append(SQL)
            # print(SQL)
    return SQL_unique

# complex conditions, i.e. age in [20,30]