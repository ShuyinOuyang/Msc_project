#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Time    : 11/06/2022 11:04
# @Author  : Shuyin Ouyang
# @File    : generateSQL.py
import copy
import json
import re
import generate_policy_query
from sql_metadata import Parser

import openpyxl
import mysql.connector
from itertools import combinations
from itertools import product
import pandas as pd



# workbook = openpyxl.load_workbook('data/healthdata.xlsx')

# columns = []
excel_map = {'n':'int', 's':'varchar', 'd':'varchar'}


# generate vocabulary from workbooks
def generate_vocabulary(workbook):
    res = {}
    for name in workbook.get_sheet_names():
        current_sheet = workbook[name]
        # initialize the dic
        tab = [i.value for i in list(current_sheet.rows)[0]]
        res[name] = {s: [] for s in tab}
        for col in current_sheet.columns:
            for cell in col:
                if col.index(cell) == 0:
                    col_name = cell.value
                else:
                    if cell.value not in res[name][col_name]:
                        res[name][col_name].append(cell.value)
    return res

# value = generate_vocabulary(workbook)


# key: table name
# value: attribute name and its data type
# table_attributes = {}
def get_mst_frequent_type(dic):
    sortList = sorted(dic.items(),key=lambda x:x[1],reverse=True)
    return sortList[0][0]

def get_table_attributes(workbook):
    table_attributes = {}
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
    return table_attributes

def transfor2sql(table_attribute):
    res = ''
    for attribute in table_attribute:

        if table_attribute[attribute][1] == -1:
            if table_attribute[attribute][0] == 'varchar':
                res += '%s %s(%s),' % (str(attribute), table_attribute[attribute][0], 255)
            else:
                res+= '%s %s,' % (str(attribute), table_attribute[attribute][0])
        else:
            if table_attribute[attribute][1] <= 255:
                res += '%s %s(%s),' % (str(attribute), table_attribute[attribute][0], 255)
            else:
                res += '%s %s(%s),' % (str(attribute), table_attribute[attribute][0], table_attribute[attribute][1])
    return res

def get_SQL_create(workbook, table_attributes, structure_info):
    SQL_create_list = []
    primary_key = structure_info['primary_key']
    foreign_key = structure_info['foreign_key']
    for table in table_attributes:
        suffix = ''
        if table in foreign_key:
            for i in range(len(foreign_key[table])):
                suffix += ('FOREIGN KEY (%s) REFERENCES %s(%s),' %
                              (foreign_key[table][i][0], foreign_key[table][i][1][0], foreign_key[table][i][1][1]))
        if table in primary_key:
            suffix += ('PRIMARY KEY (%s),' % (primary_key[table]))
        table_attribute = table_attributes[table]

        attribute_detail = transfor2sql(table_attribute)
        attribute_detail = attribute_detail[:len(attribute_detail)-1]
        if suffix:
            SQL_create = 'CREATE TABLE %s (%s), %s;' % (table, attribute_detail, suffix[:-1])
        else:
            SQL_create = 'CREATE TABLE %s (%s);' % (table, attribute_detail)
        SQL_create_list.append(SQL_create)
    return SQL_create_list

# sql insert into
# sql_insert_template = 'insert into table (attributes) values (attribute_values)'


def get_SQL_insert(workbook):
    SQL_insert_list = []
    for name in workbook.get_sheet_names():
        current_sheet = workbook[name]
        # initialize the dic
        tab = [i.value for i in list(current_sheet.rows)[0]]
        count = 0
        for row in current_sheet.rows:
            if count == 0:
                count += 1
                continue
            row_tab = []
            row_values = []
            for cell in row:
                # index of cell in row
                i = row.index(cell)
                if cell.value:
                    row_tab.append(tab[i])
                    if cell.data_type == 'n':
                        row_values.append(cell.value)
                    else:
                        row_values.append('\'%s\'' % (cell.value))
            attribute_part = '(%s)' % (','.join(str(x) for x in row_tab))
            value_part = '(%s)' % (','.join(str(x) for x in row_values))
            sql_insert_template = 'insert into %s %s values %s;' %(name, attribute_part, value_part)
            SQL_insert_list.append(sql_insert_template)
    return SQL_insert_list


# sql select

# sql_select_template = 'select * from * where *'
#
# complex_sql_select_template = 'select attribute* from view1* as x* join view2* on on_condition* where condition*'
# attribute*: table.attribute
# view*: table/ sql_select template
# x*: the align name of the view
# on_condition*: view1.attribute = view2.attribute
# condition*: A=a AND B=b

# select_attribute = 'patient_id'
# select_from_view = 'view' + str(view_count)

# fix the query result is patient_id
# target_query_attribute = 'patient_id'
# all_attributes = []
# all_tables = []
# target_query_attribute_tables = []
# for table in value:
#     all_tables.append(table)
#     for key in value[table].keys():
#         if key != target_query_attribute:
#             all_attributes.append((table, key))
#         else:
#             if table not in target_query_attribute_tables:
#                 target_query_attribute_tables.append(table)
#
#
# table_connection_matrix = [
#     [None,['patient_id','registered_patient'],None,None],
#     [['registered_patient','patient_id'],None,['seenBy','doctor_id'],None],
#     [None,['doctor_id','seenBy'],None, None],
#     [None, None, None, None]
# ]
#
# foreign_key_matrix = [
#     [None,['patient_id','registered_patient'],None,None],
#     [None,None,None,None],
#     [None,['doctor_id','seenBy'],None, None],
#     [None, None, None, None]
# ]

def test_reachability(A, all_tables):
    A = pd.DataFrame(A)
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
                    E.iloc[o, d] = [[[all_tables[o], E.iloc[o, d][0]], [all_tables[d], E.iloc[o, d][1]]]]

    # Floyd algorithm compute the shortest way from source to target attribute
    for mid in ilter:
        for o in ilter:
            for d in ilter:
                if D.iloc[o, mid] != 999 and D.iloc[mid, d] != 999 and D.iloc[o, d] > D.iloc[o, mid] + D.iloc[mid, d]:
                    D.iloc[o, d] = D.iloc[o, mid] + D.iloc[mid, d]
                    E.iloc[o, d] = E.iloc[o, mid] + E.iloc[mid, d]
    return E.values


def generate_join_view(attribute, target_query_attribute,
                            target_query_attribute_tables, reachable_matrix, all_tables, all_attributes):
    # use join to create view from two tables
    # keep condition attribute as many as possible

    # Example:
    # (SELECT patient.patient_id, appointment.seenBy
    # FROM patient
    # LEFT JOIN appointment
    # ON patient.patient_id=appointment.patient_id )
    res_view = []

    for target_table in target_query_attribute_tables:
        attribute_list = []
        attribute_list.append(target_table + '.' + target_query_attribute)
        for att in all_attributes:
            if (att[0] == target_table and att[1] == target_query_attribute) or \
                    (att[0] == attribute[0] and att[1] == attribute[1]):
                attribute_list.append(att[0]+'.'+att[1]+' as %s__%s' % (att[1],att[0]))
        if all_tables.index(attribute[0]) == all_tables.index(target_table):
            sql_select_template = 'select %s from %s' % \
                                  (','.join(x for x in attribute_list),target_table)
            res_view.append(sql_select_template)
        elif len(reachable_matrix[all_tables.index(attribute[0])][all_tables.index(target_table)]) == 1:
            on_condition_list = []
            temp = reachable_matrix[all_tables.index(attribute[0])][all_tables.index(target_table)][0]
            for i in range(len(temp)):
                on_condition_list.append('.'.join(x for x in temp[i]))
            sql_select_template = 'select %s from %s join %s on %s' % \
                                  (','.join(x for x in attribute_list),
                                   target_table, attribute[0],'='.join(x for x in on_condition_list))
            res_view.append(sql_select_template)
        elif len(reachable_matrix[all_tables.index(attribute[0])][all_tables.index(target_table)]) > 1:
            join_part = []
            once_flag = True
            for temp in reachable_matrix[all_tables.index(target_table)][all_tables.index(attribute[0])]:
                table_neme = temp[1][0]
                if once_flag:
                    target_table = temp[0][0]
                    once_flag = False
                on_condition_list = []
                for i in range(len(temp)):
                    on_condition_list.append('.'.join(x for x in temp[i]))
                temp_res = 'join %s on %s' % (table_neme, '='.join(x for x in on_condition_list))
                join_part.append(temp_res)
            sql_select_template = 'select %s from %s %s' % \
                                  (','.join(x for x in attribute_list),
                                   target_table,' '.join(x for x in join_part))
            res_view.append(sql_select_template)
    return res_view

# generate el expression by el_restrictions and the objectProperties
def generate_el_template(el_restriction,reachable_matrix,all_tables,target_table,foreign_key_matrix):
    el_template_list = []
    for key in el_restriction:
        # the key table can reach the target table
        if reachable_matrix[all_tables.index(target_table)][all_tables.index(key)]:
            reach_list = reachable_matrix[all_tables.index(target_table)][all_tables.index(key)]
            el_primary_list = []
            prefix = ''
            for x in reach_list:
                el_primary = ''
                if foreign_key_matrix[all_tables.index(x[0][0])][all_tables.index(x[1][0])]:
                    objectproperty = foreign_key_matrix[all_tables.index(x[0][0])][all_tables.index(x[1][0])][1] + '_inverse'
                elif foreign_key_matrix[all_tables.index(x[1][0])][all_tables.index(x[0][0])]:
                    objectproperty = foreign_key_matrix[all_tables.index(x[1][0])][all_tables.index(x[0][0])][1]
                if key == x[0][0] and el_restriction[key]:
                    if prefix:
                        el_primary = '(%s((%s and %s) and %s some %s))' % (prefix,
                        x[0][0], ' and '.join(x for x in el_restriction[key]), objectproperty, x[1][0])
                        bracket_count = prefix.count('(')
                        el_primary += ')' * bracket_count
                        prefix = '%s (%s and %s some' % (prefix, x[0][0], objectproperty)
                    else:
                        el_primary = '((%s and %s) and %s some %s)' % (x[0][0], ' and '.join(x for x in el_restriction[key]), objectproperty, x[1][0])
                        prefix = '%s and %s some' % (x[0][0],  objectproperty)
                elif key == x[1][0] and el_restriction[key]:
                    if prefix:
                        el_primary = '(%s (%s and %s some (%s and %s)))' % (prefix, x[0][0], objectproperty, x[1][0], ' and '.join(x for x in el_restriction[key]))
                        bracket_count = prefix.count('(')
                        el_primary += ')'*bracket_count
                        prefix = '%s (%s and %s some' % (prefix, x[0][0], objectproperty)
                    else:
                        el_primary = '(%s and %s some (%s and %s))' % (
                        x[0][0], objectproperty, x[1][0], ' and '.join(x for x in el_restriction[key]))
                        prefix = '%s and %s some' % (x[0][0], objectproperty)
                else:
                    prefix = '%s and %s some' % (x[0][0], objectproperty)
                if el_primary:
                    el_primary_list.append(el_primary)
            # if ' and '.join(x for x in el_primary_list) not in el_template_list:

            el_template_list.append(' and '.join(x for x in el_primary_list))
        # the key table is  target table
        elif key == target_table:
            el_primary = '(%s and %s)' % (target_table, ' and '.join(x for x in el_restriction[key]))
            # if el_primary not in el_template_list:
            el_template_list.append(el_primary)
        # the key table cannot reach the target table
    el_template = ' and '.join(x for x in el_template_list if x)
    return el_template


# generate sql select query
# def generate_sql_select_and_el(num_of_attribute, table_attributes):
#     # num_of_attribute = 3
#     # while num_of_attribute < len(all_attributes):
#     condition_list = list(combinations(all_attributes, num_of_attribute))
#     reachable_matrix = test_reachability(table_connection_matrix, all_tables)
#     for condition in condition_list:
#         # print(condition)
#         attribute_reachable = []
#         table_list = []
#         attribute_value_list = []
#         isReachable = False
#         # judge whether the target attribute table in the table_list
#         isTargetAttributeIn = False
#         for attribute in condition:
#             isPartReachable = False
#             if attribute[0] not in table_list:
#                 table_list.append(attribute[0])
#             attribute_value_list.append(value[attribute[0]][attribute[1]])
#             # if target_query_attribute is Reachable or in the same table with the condition attributes
#             for target_table in target_query_attribute_tables:
#                 if target_table in table_list:
#                     isTargetAttributeIn = True
#                 # if table_connection_matrix[all_tables.index(attribute[0])][all_tables.index(target_table)] or attribute[0] == target_table:
#                 #     isReachable = True
#                 if table_connection_matrix[all_tables.index(attribute[0])][all_tables.index(target_table)] or attribute[0] == target_table:
#                     isPartReachable = True
#             if isPartReachable:
#                 isReachable = True
#             attribute_reachable.append(isPartReachable)
#
#         # whether the attribute can be linked to target_query_attribute
#         if isReachable == False:
#             continue
#
#         # if all the attributes from one table
#         if len(table_list) == 1 and isTargetAttributeIn:
#             # sql select
#             attribute_specific_value_list = list(product(*attribute_value_list))
#             where_conditions = []
#             el_restrictions = []
#             for attribute_specific_value in attribute_specific_value_list:
#                 temp_where_condition = []
#                 temp_el_restriction = []
#                 for i in range(len(condition)):
#                     # if attribute_reachable[i]:
#                         if table_attributes[condition[i][0]][condition[i][1]][0] == 'varchar':
#                             temp_where_condition.append('%s=\'%s\'' % ('.'.join( str(s) for s in condition[i]), attribute_specific_value[i]))
#                             temp_el_restriction.append('%s value \"%s\"^^string' % (condition[i][1], attribute_specific_value[i]))
#                         else:
#                             temp_where_condition.append(
#                                 '%s=%s' % ('.'.join(str(s) for s in condition[i]), attribute_specific_value[i]))
#                             temp_el_restriction.append('%s value %s' % (condition[i][1], attribute_specific_value[i]))
#                 where_conditions.append(temp_where_condition)
#                 el_restrictions.append(temp_el_restriction)
#             # sql expression
#             for where_condition in where_conditions:
#                 sql_select_where_condition = ' AND '.join(str(x) for x in where_condition)
#                 sql_select_template = 'select %s from %s where %s' % (target_query_attribute, table_list[0], sql_select_where_condition)
#                 # print(sql_select_template)
#
#             # EL expression
#             for el_restriction in el_restrictions:
#                 restriction = ' and '.join(x[1] for x in condition)
#                 el_template = '%s and %s' % (table_list[0], ' and '.join(str(x) for x in el_restriction))
#                 # print(el_template)
#
#
#         # if all the attributes from more than one table
#         else:
#             view_dic = {}
#             view_list = []
#             for attribute in condition:
#                 # all the attribute becomes 'attribute__table' to avoid the overlap
#                 view = generate_join_view(attribute, target_query_attribute, target_query_attribute_tables, reachable_matrix,
#                                         all_tables, all_attributes)
#                 view_list.append(view)
#                 view_dic[attribute] = 'view%s' % (len(view_list)-1)
#
#             sql_view_part = []
#             view_product = list(product(view_list))
#             for n in range(len(view_product)):
#                 if view_product[n][0]:
#                     sql_view_part.append('('+view_product[n][0][0]+') as view%s' % (n))
#
#             attribute_specific_value_list = list(product(*attribute_value_list))
#             el_restrictions = []
#             where_conditions = []
#             for attribute_specific_value in attribute_specific_value_list:
#                 temp_where_condition = []
#                 temp_el_restriction = {}
#                 for table in table_list:
#                     temp_el_restriction[table] = []
#                 for i in range(len(condition)):
#                     # if attribute_reachable[i]:
#                         if table_attributes[condition[i][0]][condition[i][1]][0] == 'varchar':
#                             if condition[i][1] not in object_properties:
#                                 temp_el_restriction[condition[i][0]].append('%s value \"%s\"^^string' % (condition[i][1], attribute_specific_value[i]))
#                             else:
#                                 temp_el_restriction[condition[i][0]].append(
#                                     '%s value %s' % (condition[i][1], attribute_specific_value[i]))
#                             temp_where_condition.append(
#                                 '%s=\'%s\'' % ('.'.join([view_dic[condition[i]],condition[i][1]+"__"+condition[i][0]]), attribute_specific_value[i]))
#                         else:
#                             temp_el_restriction[condition[i][0]].append('%s value %s' % (condition[i][1], attribute_specific_value[i]))
#                             temp_where_condition.append(
#                                 '%s=%s' % ('.'.join([view_dic[condition[i]],condition[i][1]+"__"+condition[i][0]]), attribute_specific_value[i]))
#                 where_conditions.append(temp_where_condition)
#                 el_restrictions.append(temp_el_restriction)
#
#             if len(sql_view_part) == 1:
#                 for where_condition in where_conditions:
#                     sql_select_where_condition = ' AND '.join(str(x) for x in where_condition)
#                     sql_select_template = 'select %s from %s where %s' % \
#                                       ('view0.'+target_query_attribute, ' '.join(x for x in sql_view_part), sql_select_where_condition)
#                     # print(sql_select_template)
#             else:
#                 sql_join_part = []
#                 for n in range(1, len(sql_view_part)):
#                     sql_join_part.append('join %s on %s' % (sql_view_part[n], '='.join(['view0.'+target_query_attribute,'view%s.'% (n) + target_query_attribute])))
#                 for i in range(len(where_conditions)):
#                     where_condition = where_conditions[i]
#                     sql_select_where_condition = ' AND '.join(str(x) for x in where_condition)
#                     sql_select_template = 'select %s from %s %s where %s' % \
#                                           ('view0.' + target_query_attribute, sql_view_part[0], ' '.join(x for x in sql_join_part),
#                                            sql_select_where_condition)
#
#                     el_template = generate_el_template(el_restrictions[i], reachable_matrix, all_tables, 'patient',
#                                                        foreign_key_matrix)
                    # print(sql_select_template)
                    # print(el_template)

# from sql select to generate main attributes
# sql_select = 'select view0.patient_id from (select patient.patient_id,appointment.seenBy as seenBy__appointment from patient join appointment on appointment.registered_patient=patient.patient_id) as view0 join (select patient.patient_id,doctor.workInClinic as workInClinic__doctor from patient join appointment on patient.patient_id=appointment.registered_patient join doctor on appointment.seenBy=doctor.doctor_id) as view1 on view0.patient_id=view1.patient_id join (select patient.patient_id,doctor.hasSex as hasSex__doctor from patient join appointment on patient.patient_id=appointment.registered_patient join doctor on appointment.seenBy=doctor.doctor_id) as view2 on view0.patient_id=view2.patient_id where view0.seenBy__appointment=\'doctor_3\' AND view1.workInClinic__doctor=\'gp2\' AND view2.hasSex__doctor=\'M\''
# el_expression = '(patient and registered_patient_inverse some (appointment and seenBy value doctor_3)) and (patient and registered_patient_inverse some (appointment and seenBy some (doctor and workInClinic value "gp2"^^string and hasSex value "M"^^string)))'

# split the string with key words: and, some value
def main_attributes_analysis_el(el_expression):
    # use stack to store the content in ()
    content = el_expression.split(' ')
    stack = []
    info_list = []
    for word in content:
        if word[0] == '(':
            left_bracket_count = word.count('(')
            for i in range(left_bracket_count):
                stack.append('(')
            stack.append(word.replace('(', ''))
        elif word[-1] == ')':
            stack.append(word.replace(')', ''))
            right_bracket_count = word.count(')')

            for i in range(right_bracket_count):
                content_part = []
                while stack[-1] != '(':
                    content_part.append(stack.pop())
                stack.pop()
                info_list.append(' '.join(x for x in list(reversed(content_part))))
        else:
            stack.append(word)

    attribute_value = []
    for info in info_list:
        info_content = info.strip().split('and')
        table_name = info_content[0]
        for restriction in info_content:
            if 'value' in restriction:
                # attribute value
                restriction_content = restriction.split('value')
                if '^^' in restriction_content[1].strip():
                    value = restriction_content[1].strip().split('^^')[0]
                else:
                    value = restriction_content[1].strip()
                attribute_value.append([table_name, restriction_content[0].strip(), value])
    # return attribute with form: [table, attribute, value]
    return attribute_value


# split the string with key words: select, join, as, on, where, and
def main_attributes_analysis_sql(sql_select):
    attribute_value = []
    where_condition = sql_select.split('where')[1]
    main_attribute = re.findall(r'.(\w+)__(\w+)=([\'\w+]*)', where_condition)
    # return attribute with form: [table, attribute, value]
    for i in main_attribute:
        attribute_value.append([i[1],i[0],i[2]])
    return attribute_value

# translate data(.xlsx) into database
def data2database(path, structure_info):
    workbook = openpyxl.load_workbook(path)
    # vocabulary = generate_vocabulary(workbook)
    table_attributes = get_table_attributes(workbook)
    SQL_create_list = get_SQL_create(workbook, table_attributes, structure_info)
    SQL_insert_list = get_SQL_insert(workbook)
    return SQL_create_list, SQL_insert_list

# generate vocabulary of database
# vocabulary: store the table info (includes heading, attributes' types and data)
# blank_node_table: store the tables' name that don't have primary key, for further blank node ontology translation
# attribute_types: store the table info (includes tables, attributes and their corresponding ontology dataproperty type)
# foreign_key_dic: store the foreign keys
# primary_key_dic: store the primary keys
def generate_vocabulary(SQL_create_list, SQL_insert_list):
    vocabulary = {}
    blank_node_table = []
    attribute_types = {}
    foreign_key_dic = {}
    primary_key_dic ={}
    for SQL_create in SQL_create_list:
        content = re.findall(r'CREATE TABLE (.*?) [(](.*?)[)], [PRIMARYFOREIGN]', SQL_create)
        table = content[0][0]
        if 'PRIMARY KEY' not in SQL_create:
            blank_node_table.append(table)
        else:
            primary_key_content = re.findall(r'PRIMARY KEY [(](.*?)[)]', SQL_create)
            primary_key_dic[table] = primary_key_content[0]

        if 'FOREIGN KEY' in SQL_create:
            foreign_key_content = re.findall(r'FOREIGN KEY [(](.*?)[)] REFERENCES (.*?)[(](.*?)[)]', SQL_create)
            for FK in foreign_key_content:
                foreign_key_dic[(table, FK[0])] = (FK[1], FK[2])

        if table not in attribute_types:
            attribute_types[table] = {}
        if table not in vocabulary:
            vocabulary[table] = []
        table_attributes = content[0][1].split(',')
        attribute_list = []
        for x in table_attributes:
            attribute_type = x.split(' ')
            attribute_types[table][attribute_type[0]] = attribute_type[1]
            attribute_list.append((attribute_type[0],attribute_type[1]))
        vocabulary[table].append(attribute_list)

    for SQL_insert in SQL_insert_list:
        content = re.findall(r'insert into (.*?) [(](.*?)[)] values [(](.*?)[)];', SQL_insert)
        table = content[0][0]
        attributes = content[0][1].split(',')
        values = content[0][2].split(',')
        value_list = []
        for i in range(len(attributes)):
            if attribute_types[table][attributes[i]] == 'int':
                v = int(values[i])
            elif attribute_types[table][attributes[i]] == 'varchar(255)':
                v = values[i].replace("\'", '')
            value_list.append(v)
        vocabulary[table].append(value_list)

    # ontology data property type
    database_ontology_datatype_map = {'int': 'XSD_INT', 'varchar(255)': 'XSD_STRING'}
    for table in attribute_types:
        for attribute in attribute_types[table]:
            attribute_types[table][attribute] = database_ontology_datatype_map[attribute_types[table][attribute]]
    return vocabulary, blank_node_table, attribute_types, foreign_key_dic, primary_key_dic

# translate database into ontology
# write the ontology set up config into json file
def database2ontology(SQL_create_list, SQL_insert_list):
    # ontology dictionary
    # the basic elements in ontology is class, objectiveProperty, dataProperty and individuals
    dic_ontology = {'class': [], 'individual': [], 'objectProperty': [], 'dataProperty': []}
    vocabulary, blank_node_table, table_attributes, foreign_key, primary_key = \
        generate_vocabulary(SQL_create_list, SQL_insert_list)
    for table_name in vocabulary:
        # setting of class
        dic_ontology['class'].append(table_name)
        table = vocabulary[table_name]
        # the heading of the table
        tab = [i[0] for i in table[0]]
        # the first element is the heading of the table
        # setting of dataproperty and objectproperty
        for i in range(len(tab)):
            # judge whether attribute belongs to dataProperty or objectProperty
            # by foreign key
            if (table_name, tab[i]) not in foreign_key:
                if {'name': tab[i], 'domain': table_name, 'range': table_attributes[table_name][tab[i]]} \
                        not in dic_ontology['dataProperty']:
                    dic_ontology['dataProperty'].append(
                        {'name': tab[i], 'domain': table_name, 'range': table_attributes[table_name][tab[i]]})
            else:
                if {'name': tab[i], 'domain': table_name, 'range': foreign_key[(table_name, tab[i])][0]} \
                        not in dic_ontology['objectProperty']:
                    dic_ontology['objectProperty'].append(
                        {'name': tab[i], 'domain': table_name, 'range': foreign_key[(table_name, tab[i])][0]})
        # individuals
        row_count = 0
        for record in table[1:]:
            individual = {'type': table_name}
            for i in range(len(record)):
                if table_name in blank_node_table:
                    individual[tab[i]] = str(record[i])
                else:
                    if tab[i] == primary_key[table_name]:
                        individual['name'] = str(record[i])
                    else:
                        if ' 00:00:00' not in str(record[i]):
                            individual[tab[i]] = str(record[i])
                        else:
                            individual[tab[i]] = str(record[i]).replace(' 00:00:00','')
            if table_name in blank_node_table:
                individual['name'] = table_name + '_%s' % (row_count)
            row_count += 1
            # the setting of individual
            dic_ontology['individual'].append(individual)
    # save the ontology json file
    json_str = json.dumps(dic_ontology)
    with open('ontology.json', 'w') as json_file:
        json_file.write(json_str)

# translate sql select statement into EL expression
def sql2el(sql_select, vocabulary, foreign_key_dic, table_attributes):
    # support join, select, where, as, on, from
    parser = Parser(sql_select)
    sql_select_dic = parser.columns_dict
    select_list = []
    where_list = []
    join_list = []
    condition = []
    if 'where' in sql_select_dic:
        where_list = sql_select_dic['where']
    if 'select' in sql_select_dic:
        select_list = sql_select_dic['select']
    if 'join' in sql_select_dic:
        join_list = sql_select_dic['join']

    if where_list:
        for attribute in where_list:
            if '.' in attribute:
                attribute_content = attribute.split('.')
                view = attribute_content[0]
                view_attribute = attribute_content[1]
            else:
                view = parser.tables[0]
                view_attribute = attribute

            # get alias of column
            alias_dic = {value: key for key, value in parser.columns_aliases.items()}

            if alias_dic and attribute in alias_dic:
                attribute_ = alias_dic[attribute]
            else:
                attribute_ = view_attribute
            # match the value of the view_attribute
            value = re.findall(r'%s=(.*?)[\n AND]' % (attribute_), sql_select)
            if not value:
                value = re.findall(r'%s=(.*)$' % (attribute_), sql_select)

            if '\'' in value[0]:
                value[0] = value[0].replace('\'', '')
            condition.append((view, view_attribute, value[0]))

    # generate foreign key matrix
    # generate table connection matrix
    all_tables = list(vocabulary.keys())
    foreign_key_matrix = [[None for _ in range(len(all_tables))] for _ in range(len(all_tables))]
    table_connection_matrix = [[None for _ in range(len(all_tables))] for _ in range(len(all_tables))]
    for FK in foreign_key_dic:
        foreign_key_matrix[all_tables.index(foreign_key_dic[FK][0])][all_tables.index(FK[0])] = \
            [foreign_key_dic[FK][1], FK[1]]
        table_connection_matrix[all_tables.index(FK[0])][all_tables.index(foreign_key_dic[FK][0])] = \
            [FK[1], foreign_key_dic[FK][1]]
        table_connection_matrix[all_tables.index(foreign_key_dic[FK][0])][all_tables.index(FK[0])] = \
            [foreign_key_dic[FK][1], FK[1]]
    # return foreign_key_matrix, table_connection_matrix

    # condition 2 ontology
    el_expression = condition2el(vocabulary, condition, table_connection_matrix,
                                 foreign_key_matrix, all_tables, table_attributes)

    # print('__________________')
    # _ = condition2el(vocabulary, [('baby', 'dataOfBirth', '11/11/2019'), ('guardian','job','soldier')], table_connection_matrix,
    #                              foreign_key_matrix, all_tables, table_attributes)

    return el_expression

def condition2el(vocabulary, condition, table_connection_matrix, foreign_key_matrix, all_tables, table_attributes):
    # fix the query result is patient_id
    target_query_attribute = 'patient_id'
    target_query_attribute_tables = []
    all_attributes = []
    object_properties = []
    # get ontology's objectProperty
    with open('ontology.json', 'r') as json_file:
        new_dict = json.load(json_file)
        for x in new_dict['objectProperty']:
            object_properties.append(x['name'])
    reachable_matrix = test_reachability(table_connection_matrix, all_tables)
    for table in vocabulary:
        for attr in vocabulary[table][0]:
            if attr[0] != target_query_attribute:
                all_attributes.append((table, attr[0]))
            else:
                if table not in target_query_attribute_tables:
                    target_query_attribute_tables.append(table)
    attribute_reachable = []
    table_list = []
    isReachable = False
    # judge whether the target attribute table in the table_list
    isTargetAttributeIn = False
    for attribute in condition:
        isPartReachable = False
        if attribute[0] not in table_list:
            table_list.append(attribute[0])
        # if target_query_attribute is Reachable or in the same table with the condition attributes
        for target_table in target_query_attribute_tables:
            if target_table in table_list:
                isTargetAttributeIn = True
            if attribute[0] not in table_attributes:
                print('there is no table \'%s\' ' % (attribute[0]))
                return
            if table_connection_matrix[all_tables.index(attribute[0])][all_tables.index(target_table)] or attribute[
                0] == target_table:
                isPartReachable = True
        if isPartReachable:
            isReachable = True
        attribute_reachable.append(isPartReachable)

    # whether the attribute can be linked to target_query_attribute
    if isReachable == False:
        print('some attribute cannot be linked to target_query_attribute')
        return

    # if all the attributes from one table
    if len(table_list) == 1 and isTargetAttributeIn:
        # sql select
        where_condition = []
        el_restriction = []
        for i in range(len(condition)):
            # judge whether the attribute is in the table
            if condition[i][1] not in table_attributes[condition[i][0]]:
                print('there is no attribute \'%s\' in table \'%s\' ' % (condition[i][1], condition[i][0]))
                return
            # if attribute_reachable[i]:
            if table_attributes[condition[i][0]][condition[i][1]] == 'XSD_STRING':
                if condition[i][1] not in object_properties:
                    el_restriction.append(
                        '%s value \"%s\"^^string' % (condition[i][1], condition[i][2]))
                else:
                    el_restriction.append(
                        '%s value %s' % (condition[i][1], condition[i][2]))
                where_condition.append(
                    '%s=\'%s\'' % ('.'.join(str(s) for s in condition[i][:2]), condition[i][2]))
                # el_restriction.append(
                #     '%s value \"%s\"^^string' % (condition[i][1], condition[i][2]))
            else:
                where_condition.append(
                    '%s=%s' % ('.'.join(str(s) for s in condition[i][:2]), condition[i][2]))
                el_restriction.append('%s value %s' % (condition[i][1], condition[i][2]))
        # sql expression
        # sql_select_where_condition = ' AND '.join(str(x) for x in where_condition)
        # sql_select_template = 'select %s from %s where %s' % (
        # target_query_attribute, table_list[0], sql_select_where_condition)
        # print(sql_select_template)
        # EL expression
        restriction = ' and '.join(x[1] for x in condition)
        el_template = '%s and %s' % (table_list[0], ' and '.join(str(x) for x in el_restriction))
        # print(el_template)
    # TODO modify this part
    # if all the attributes from more than one table
    else:
        view_list = []
        view_dic = {}
        for attribute in condition:
            # all the attribute becomes 'attribute__table' to avoid the overlap
            view = generate_join_view(attribute, target_query_attribute, target_query_attribute_tables, reachable_matrix,
                                    all_tables, all_attributes)
            view_list.append(view)
            # print(view)
            view_dic[attribute] = 'view%s' % (len(view_list)-1)

        sql_view_part = []
        view_product = list(product(view_list))
        for n in range(len(view_product)):
            if view_product[n][0]:
                sql_view_part.append('('+view_product[n][0][0]+') as view%s' % (n))

        el_restriction = {}
        where_condition = []
        for table in table_list:
            el_restriction[table] = []
        for i in range(len(condition)):
            # if attribute_reachable[i]:
                if table_attributes[condition[i][0]][condition[i][1]] == 'XSD_STRING':
                    if condition[i][1] not in object_properties:
                        el_restriction[condition[i][0]].append('%s value \"%s\"^^string' % (condition[i][1], condition[i][2]))
                    else:
                        el_restriction[condition[i][0]].append(
                            '%s value %s' % (condition[i][1], condition[i][2]))
                    where_condition.append(
                        '%s=\'%s\'' % ('.'.join([view_dic[condition[i]],condition[i][1]+"__"+condition[i][0]]), condition[i][2]))
                else:
                    el_restriction[condition[i][0]].append('%s value %s' % (condition[i][1], condition[i][2]))
                    where_condition.append(
                        '%s=%s' % ('.'.join([view_dic[condition[i]],condition[i][1]+"__"+condition[i][0]]), condition[i][2]))

        if len(sql_view_part) == 1:
            sql_select_where_condition = ' AND '.join(str(x) for x in where_condition)
            sql_select_template = 'select %s from %s where %s' % \
                              ('view0.'+target_query_attribute, ' '.join(x for x in sql_view_part), sql_select_where_condition)
            # print(sql_select_template)
        else:
            sql_join_part = []
            for n in range(1, len(sql_view_part)):
                sql_join_part.append('join %s on %s' % (sql_view_part[n], '='.join(['view0.'+target_query_attribute,'view%s.'% (n) + target_query_attribute])))
            sql_select_where_condition = ' AND '.join(str(x) for x in where_condition)
            sql_select_template = 'select %s from %s %s where %s' % \
                                  ('view0.' + target_query_attribute, sql_view_part[0], ' '.join(x for x in sql_join_part),
                                   sql_select_where_condition)
            # print(sql_select_template)

        el_template = generate_el_template(el_restriction, reachable_matrix, all_tables, all_tables[0], foreign_key_matrix)

    return el_template

def condition2sql_select(vocabulary, condition, table_connection_matrix, foreign_key_matrix, all_tables, table_attributes):
    # fix the query result is patient_id
    target_query_attribute = 'patient_id'
    target_query_attribute_tables = []
    all_attributes = []
    object_properties = []
    # get ontology's objectProperty
    with open('ontology.json', 'r') as json_file:
        new_dict = json.load(json_file)
        for x in new_dict['objectProperty']:
            object_properties.append(x['name'])
    reachable_matrix = test_reachability(table_connection_matrix, all_tables)
    for table in vocabulary:
        for attr in vocabulary[table][0]:
            if attr[0] != target_query_attribute:
                all_attributes.append((table, attr[0]))
            else:
                if table not in target_query_attribute_tables:
                    target_query_attribute_tables.append(table)
    attribute_reachable = []
    table_list = []
    isReachable = False
    # judge whether the target attribute table in the table_list
    isTargetAttributeIn = False
    for attribute in condition:
        isPartReachable = False
        if attribute[0] not in table_list:
            table_list.append(attribute[0])
        # if target_query_attribute is Reachable or in the same table with the condition attributes
        for target_table in target_query_attribute_tables:
            if target_table in table_list:
                isTargetAttributeIn = True
            if attribute[0] not in table_attributes:
                print('there is no table \'%s\' ' % (attribute[0]))
                return
            if table_connection_matrix[all_tables.index(attribute[0])][all_tables.index(target_table)] or attribute[
                0] == target_table:
                isPartReachable = True
        if isPartReachable:
            isReachable = True
        attribute_reachable.append(isPartReachable)

    # whether the attribute can be linked to target_query_attribute
    if isReachable == False:
        print('some attribute cannot be linked to target_query_attribute')
        return

    # if all the attributes from one table
    if len(table_list) == 1 and isTargetAttributeIn:
        # sql select
        where_condition = []
        el_restriction = []
        for i in range(len(condition)):
            # judge whether the attribute is in the table
            if condition[i][1] not in table_attributes[condition[i][0]]:
                print('there is no attribute \'%s\' in table \'%s\' ' % (condition[i][1], condition[i][0]))
                return
            # if attribute_reachable[i]:
            if table_attributes[condition[i][0]][condition[i][1]] == 'XSD_STRING':
                if condition[i][1] not in object_properties:
                    el_restriction.append(
                        '%s value \"%s\"^^string' % (condition[i][1], condition[i][2]))
                else:
                    el_restriction.append(
                        '%s value %s' % (condition[i][1], condition[i][2]))
                where_condition.append(
                    '%s=\'%s\'' % ('.'.join(str(s) for s in condition[i][:2]), condition[i][2]))
                # el_restriction.append(
                #     '%s value \"%s\"^^string' % (condition[i][1], condition[i][2]))
            else:
                where_condition.append(
                    '%s=%s' % ('.'.join(str(s) for s in condition[i][:2]), condition[i][2]))
                el_restriction.append('%s value %s' % (condition[i][1], condition[i][2]))
        # sql expression
        sql_select_where_condition = ' AND '.join(str(x) for x in where_condition)
        sql_select_template = 'select %s from %s where %s' % (
        target_query_attribute, table_list[0], sql_select_where_condition)

        # EL expression
        restriction = ' and '.join(x[1] for x in condition)
        el_template = '%s and %s' % (table_list[0], ' and '.join(str(x) for x in el_restriction))
        # print(el_template)
    # TODO modify this part
    # if all the attributes from more than one table
    else:
        view_list = []
        view_dic = {}
        for attribute in condition:
            # all the attribute becomes 'attribute__table' to avoid the overlap
            view = generate_join_view(attribute, target_query_attribute, target_query_attribute_tables, reachable_matrix,
                                    all_tables, all_attributes)
            view_list.append(view)
            # print(view)
            view_dic[attribute] = 'view%s' % (len(view_list)-1)

        sql_view_part = []
        view_product = list(product(view_list))
        for n in range(len(view_product)):
            if view_product[n][0]:
                sql_view_part.append('('+view_product[n][0][0]+') as view%s' % (n))

        # el_restriction = {}
        where_condition = []
        # for table in table_list:
        #     el_restriction[table] = []
        for i in range(len(condition)):
            # if attribute_reachable[i]:
                if table_attributes[condition[i][0]][condition[i][1]] == 'XSD_STRING':
                    # if condition[i][1] not in object_properties:
                    #     el_restriction[condition[i][0]].append('%s value \"%s\"^^string' % (condition[i][1], condition[i][2]))
                    # else:
                    #     el_restriction[condition[i][0]].append(
                    #         '%s value %s' % (condition[i][1], condition[i][2]))
                    where_condition.append(
                        '%s=\'%s\'' % ('.'.join([view_dic[condition[i]],condition[i][1]+"__"+condition[i][0]]), condition[i][2]))
                else:
                    # el_restriction[condition[i][0]].append('%s value %s' % (condition[i][1], condition[i][2]))
                    where_condition.append(
                        '%s=%s' % ('.'.join([view_dic[condition[i]],condition[i][1]+"__"+condition[i][0]]), condition[i][2]))

        if len(sql_view_part) == 1:
            sql_select_where_condition = ' AND '.join(str(x) for x in where_condition)
            sql_select_template = 'select %s from %s where %s' % \
                              ('view0.'+target_query_attribute, ' '.join(x for x in sql_view_part), sql_select_where_condition)
            # print(sql_select_template)
        else:
            sql_join_part = []
            for n in range(1, len(sql_view_part)):
                sql_join_part.append('join %s on %s' % (sql_view_part[n], '='.join(['view0.'+target_query_attribute,'view%s.'% (n) + target_query_attribute])))
            sql_select_where_condition = ' AND '.join(str(x) for x in where_condition)
            sql_select_template = 'select %s from %s %s where %s' % \
                                  ('view0.' + target_query_attribute, sql_view_part[0], ' '.join(x for x in sql_join_part),
                                   sql_select_where_condition)
            # print(sql_select_template)

        # el_template = generate_el_template(el_restriction, reachable_matrix, all_tables, all_tables[0], foreign_key_matrix)

    return sql_select_template


def trivial_checking(policy, mydb):
    # trivial checking against database
    res = []
    for p in policy:
        cursor = mydb.cursor()
        cursor.execute(p)
        SQL_result = cursor.fetchall()
        if SQL_result:
            print('--INFO--the policy (%s) is not trivial' % (p))
            res.append(p)
        else:
            print('--INFO--the policy (%s) is trivial' % (p))
    return res

# def query_attack(vocabulary, table_connection_matrix, foreign_key_matrix, all_tables, table_attributes):
def query_attack(vocabulary, foreign_key_dic, table_attributes, mydb):
    # generate sql select attack query
    # exhausted attack
    # from attack cases to infer policy

    # generate foreign key matrix
    # generate table connection matrix
    all_tables = list(vocabulary.keys())
    foreign_key_matrix = [[None for _ in range(len(all_tables))] for _ in range(len(all_tables))]
    table_connection_matrix = [[None for _ in range(len(all_tables))] for _ in range(len(all_tables))]
    for FK in foreign_key_dic:
        foreign_key_matrix[all_tables.index(foreign_key_dic[FK][0])][all_tables.index(FK[0])] = \
            [foreign_key_dic[FK][1], FK[1]]
        table_connection_matrix[all_tables.index(FK[0])][all_tables.index(foreign_key_dic[FK][0])] = \
            [FK[1], foreign_key_dic[FK][1]]
        table_connection_matrix[all_tables.index(foreign_key_dic[FK][0])][all_tables.index(FK[0])] = \
            [foreign_key_dic[FK][1], FK[1]]


    # attack_el_expressions = []
    attack_sql= []
    all_attributes = []
    for table in vocabulary:
        for attribute in vocabulary[table][0]:
            if not (table == 'patient' and attribute[0] == 'patient_id'):
                all_attributes.append([table, attribute[0], attribute[1]])
    # generate conditions
    # for i in range(1, len(all_attributes)+1):
    for i in range(1, 3):
        # pick i attributes from all_attributes
        condition_list = list(combinations(all_attributes, i))
        # get value
        for con in condition_list:
            attribute_value_list = []

            for att in con:
                attribute_index = vocabulary[att[0]][0].index((att[1], att[2]))
                temp_list = []
                for i in range(1, len(vocabulary[att[0]])):
                    if vocabulary[att[0]][i][attribute_index] not in temp_list:
                        temp_list.append(vocabulary[att[0]][i][attribute_index])
                attribute_value_list.append(temp_list)
            attribute_specific_value_list = list(product(*attribute_value_list))
            for i in range(len(attribute_specific_value_list)):
                condition = []
                for j in range((len(attribute_specific_value_list[i]))):
                    condition.append((con[j][0], con[j][1], attribute_specific_value_list[i][j]))
                # print(condition)
                sql_select = condition2sql_select(vocabulary, condition, table_connection_matrix, foreign_key_matrix, all_tables, table_attributes)
                if sql_select:
                    sql_select = trivial_checking([sql_select], mydb)
                    if sql_select:
                        attack_sql.append(sql_select[0])
    return attack_sql


def setup_database():
    # load dataset from file
    # test dataset1
    path = 'data/healthdata.xlsx'
    structure_info = {'primary_key': {'patient': 'patient_id', 'doctor': 'doctor_id'},
                      'foreign_key': {'appointment': [['registered_patient', ('patient', 'patient_id')],
                                                      ['seenBy', ('doctor', 'doctor_id')]]}
                      }
    return path, structure_info

def setup_database_royal_baby():
    # load dataset from file
    # test dataset1
    path = 'data/royal_baby.xlsx'
    structure_info = {'primary_key': {'baby': 'patient_id', 'guardian': 'guardian_id', 'hospital': 'hospital_name'},
                      'foreign_key': {'baby': [['hasGuardian', ('guardian', 'guardian_id')],
                                                      ['inHospital', ('hospital', 'hospital_name')]]}
                      }
    return path, structure_info

def setup_size_experiment():
    # load dataset from file
    # test dataset1
    path = 'size_experiment/10_100.xlsx'
    structure_info = {'primary_key': {'patient': 'patient_id'},
                      'foreign_key': {}
                      }
    return path, structure_info

if __name__ == "__main__":
    # TODO change dataset setup
    # TODO change test set
    # dataset, policy and query initializtion

    # path, structure_info = setup_size_experiment()
    # policy, query = generate_policy_query.test_case_size_10_100()

    # path, structure_info = setup_database()
    # policy, query = generate_policy_query.test_case3()
    path, structure_info = setup_database_royal_baby()
    policy, query = generate_policy_query.test_case_royal_baby1()

    # # setting up connection to the database
    # mydb = mysql.connector.connect(
    #     host="localhost",
    #     user="root",
    #     passwd="123456",
    #     auth_plugin='mysql_native_password',
    #     database="health"
    # )
    # # trivial checking
    # trivial_check = True
    # if trivial_check:
    #     policy = trivial_checking(policy, mydb)

    # database initialization
    SQL_create_list, SQL_insert_list = data2database(path, structure_info)
    # transfer database into ontology
    # and save the json file into ontology.json file locally
    database2ontology(SQL_create_list, SQL_insert_list)
    vocabulary, blank_node_table, table_attributes, foreign_key, primary_key = \
        generate_vocabulary(SQL_create_list, SQL_insert_list)


    policy_el = []
    query_el = ''
    if query:
        query_el = sql2el(query, vocabulary, foreign_key, table_attributes)
    for p in policy:
        p_el = sql2el(p, vocabulary, foreign_key, table_attributes)
        if p_el and p_el not in policy_el:
            policy_el.append(p_el)

    # store query and policy into json file
    policy_query = {}
    policy_query['policy'] = policy_el
    policy_query['query'] = query_el

    # store the json file into policy_query.json
    json_str = json.dumps(policy_query)
    with open('test_data/policy_query.json', 'w') as json_file:
        json_file.write(json_str)
