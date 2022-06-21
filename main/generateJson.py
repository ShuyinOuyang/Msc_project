#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Time    : 07/06/2022 14:35
# @Author  : Shuyin Ouyang
# @File    : generateJson.py

import openpyxl
import json

workbook = openpyxl.load_workbook('data/healthdata.xlsx')
print(workbook.get_sheet_names())
dic_ontology = {'class':[], 'individual':[], 'objectProperty':[], 'dataProperty':[]}
foreign_key = {('appointment', 'seenBy'): ('doctor', 'doctor_id'), ('appointment', 'registered_patient'): ('patient', 'patient_id')}
blank_node_table = ['appointment']
# ontology data property type
excel_map = {'n':'XSD_INT', 's':'XSD_STRING', 'd':'XSD_STRING'}

table_attributes = {}
def get_mst_frequent_type(dic):
    sortList = sorted(dic.items(),key=lambda x:x[1],reverse=True)
    return sortList[0][0]

for name in workbook.get_sheet_names():
    table_name = name
    current_sheet = workbook[name]
    # initialize the dic
    tab = [i.value for i in list(current_sheet.rows)[0]]
    table_attributes[name] = {s:[] for s in tab}
    for col in current_sheet.columns:
        col_type = {}
        col_value_max_length = -1
        for cell in col:
            if col.index(cell) == 0:
                col_name = cell.value
            else:
                # count the number of type
                if cell.data_type not in col_type:
                    col_type[cell.data_type] = 1
                else:
                    col_type[cell.data_type] += 1
                if cell.data_type == "s":
                    col_value_max_length = max(len(cell.value), col_value_max_length)
        # column data type
        final_col_type = get_mst_frequent_type(col_type)
        table_attributes[name][col_name] = [excel_map[final_col_type], col_value_max_length]


for name in workbook.get_sheet_names():
    if name == 'prescription':
        continue
    dic_ontology['class'].append(name)
    current_sheet = workbook[name]
    # the columns' names
    tab = [i.value for i in list(current_sheet.rows)[0]]
    # add individuals
    row_count = 0
    for row in current_sheet.rows:
        # add individual
        if row == list(current_sheet.rows)[0]:
            continue
        for i in range(len(tab)):
            if i != 0 or (i == 0 and name in blank_node_table):
                # dataProperty, domain, range
                # domain: class
                # range: datatype
                if (name, tab[i]) not in foreign_key:
                    if [tab[i], name, table_attributes[name][tab[i]][0]] not in dic_ontology['dataProperty']:
                        # dic_ontology['dataProperty'].append(tab[i])
                        dic_ontology['dataProperty'].append({'name':tab[i], 'domain':name, 'range':table_attributes[name][tab[i]][0]})
                else:
                    if [tab[i], name, foreign_key[(name,tab[i])][0]] not in dic_ontology['objectProperty']:
                        # dic_ontology['objectProperty'].append(tab[i])
                        dic_ontology['objectProperty'].append({'name': tab[i], 'domain':name, 'range':foreign_key[(name,tab[i])][0]})
        individual = {'type': name}
        # manually change
        # if name == 'appointment':
        #     individual['type'] = 'patient'
        for cell in row:
            if row == tab:
                pass
            else:
                # blank nodes
                if name in blank_node_table:
                    individual[tab[row.index(cell)]] = str(cell.value)
                else:
                    if row.index(cell) == 0:
                        individual['name'] = cell.value
                    else:
                        individual[tab[row.index(cell)]] = str(cell.value)
            # print(cell.value,end=' ')
        if name in blank_node_table:
            individual['name'] = name + '_%s' % (row_count)
        dic_ontology['individual'].append(individual)
        row_count += 1
        # break

json_str = json.dumps(dic_ontology)
with open('ontology.json', 'w') as json_file:
    json_file.write(json_str)