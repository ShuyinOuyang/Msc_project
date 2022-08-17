#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Time    : 11/06/2022 11:04
# @Author  : Shuyin Ouyang
# @File    : generateSQL.py
import copy
import json
import openpyxl
import mysql.connector
from itertools import combinations
from itertools import product
import pandas as pd

workbook = openpyxl.load_workbook('data/healthdata.xlsx')
object_properties = []
with open('ontology.json', 'r') as json_file:
    new_dict = json.load(json_file)
    for x in new_dict['objectProperty']:
        object_properties.append(x['name'])
# name, type,
columns = []
excel_map = {'n':'float', 's':'varchar', 'd':'varchar'}

# key: table name
# value: attribute name and its data type
table_attributes = {}

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

value = generate_vocabulary(workbook)

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




def transfor2sql(table_attribute):
    res = ''
    for attribute in table_attribute:
        if table_attribute[attribute][1] == -1:
            res+= '%s %s,' % (str(attribute),table_attribute[attribute][0])
        else:
            if table_attribute[attribute][1] <= 255:
                res += '%s %s(%s),' % (str(attribute), table_attribute[attribute][0],255)
            else:
                res += '%s %s(%s),' % (str(attribute), table_attribute[attribute][0], table_attribute[attribute][1])
    return res

SQL_create_list = []
for table in table_attributes:
    table_attribute = table_attributes[table]

    attribute_detail = transfor2sql(table_attribute)
    attribute_detail = attribute_detail[:len(attribute_detail)-1]

    SQL_create = 'CREATE TABLE %s (%s);' % (table, attribute_detail)
    SQL_create_list.append(SQL_create)

# sql insert into
sql_insert_template = 'insert into table (attributes) values (attribute_values)'
SQL_insert_list = []
for name in workbook.get_sheet_names():
    current_sheet = workbook[name]
    # initialize the dic
    tab = [i.value for i in list(current_sheet.rows)[0]]
    for row in current_sheet.rows:
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
                # print(cell.value)
        attribute_part = '(%s)' % (','.join(str(x) for x in row_tab))
        value_part = '(%s)' % (','.join(str(x) for x in row_values))
        sql_insert_template = 'insert into %s %s values %s;' %(name, attribute_part, value_part)
        SQL_insert_list.append(sql_insert_template)
        # print(sql_insert_template)


# sql select

sql_select_template = 'select * from * where *'

complex_sql_select_template = 'select attribute* from view1* as x* left join view2* on on_condition* where condition*'
# attribute*: table.attribute
# view*: table/ sql_select template
# x*: the align name of the view
# on_condition*: view1.attribute = view2.attribute
# condition*: A=a AND B=b

# select_attribute = 'patient_id'
# select_from_view = 'view' + str(view_count)

# fix the query result is patient_id
target_query_attribute = 'patient_id'
all_attributes = []
all_tables = []
target_query_attribute_tables = []
for table in value:
    all_tables.append(table)
    for key in value[table].keys():
        if key != target_query_attribute:
            all_attributes.append((table, key))
        else:
            if table not in target_query_attribute_tables:
                target_query_attribute_tables.append(table)


table_connection_matrix = [
    [None,['patient_id','registered_patient'],None,None],
    [['registered_patient','patient_id'],None,['seenBy','doctor_id'],None],
    [None,['doctor_id','seenBy'],None, None],
    [None, None, None, None]
]

foreign_key_matrix = [
    [None,['patient_id','registered_patient'],None,None],
    [None,None,None,None],
    [None,['doctor_id','seenBy'],None, None],
    [None, None, None, None]
]

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


num_of_attribute = 2
# while num_of_attribute < len(all_attributes):
condition_list = list(combinations(all_attributes, num_of_attribute))

reachable_matrix = test_reachability(table_connection_matrix, all_tables)

def generate_left_join_view(attribute, target_query_attribute,
                            target_query_attribute_tables, reachable_matrix, all_tables, all_attributes):
    # use left join to create view from two tables
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

        if len(reachable_matrix[all_tables.index(attribute[0])][all_tables.index(target_table)]) == 1:
            on_condition_list = []
            temp = reachable_matrix[all_tables.index(attribute[0])][all_tables.index(target_table)][0]
            for i in range(len(temp)):
                on_condition_list.append('.'.join(x for x in temp[i]))
            sql_select_template = 'select %s from %s left join %s on %s' % \
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


def generate_el_template(el_restriction,reachable_matrix,all_tables,target_table,foreign_key_matrix):
    el_template_list = []
    for key in el_restriction:
        # the key table can reach the target table
        if reachable_matrix[all_tables.index(target_table)][all_tables.index(key)]:
            reach_list = reachable_matrix[all_tables.index(target_table)][all_tables.index(key)]
            el_primary_list = []
            for x in reach_list:
                if foreign_key_matrix[all_tables.index(x[0][0])][all_tables.index(x[1][0])]:
                    objectproperty = foreign_key_matrix[all_tables.index(x[0][0])][all_tables.index(x[1][0])][
                                         1] + '_inverse'
                elif foreign_key_matrix[all_tables.index(x[1][0])][all_tables.index(x[0][0])]:
                    objectproperty = foreign_key_matrix[all_tables.index(x[1][0])][all_tables.index(x[0][0])][1]
                if key == x[0][0] and el_restriction[key]:
                    el_primary = '((%s and %s) %s some %s)' % (
                    x[0][0], ' and '.join(x for x in el_restriction[key]), objectproperty, x[1][0])
                elif key == x[1][0] and el_restriction[key]:
                    el_primary = '(%s and %s some (%s and %s))' % (
                    x[0][0], objectproperty, x[1][0], ' and '.join(x for x in el_restriction[key]))
                el_primary_list.append(el_primary)
            el_template_list.append(' and '.join(x for x in el_primary_list))
        # the key table is  target table
        elif key == target_table:
            el_primary = '(%s and %s)' % (target_table, ' and '.join(x for x in el_restriction[key]))
            el_template_list.append(el_primary)
        # the key table cannot reach the target table
        else:
            pass
    el_template = ' and '.join(x for x in el_template_list)
    return el_template
    # print(el_template)

def generate_sql_select_and_el(num_of_attribute, table_attributes):
    # num_of_attribute = 3
    # while num_of_attribute < len(all_attributes):
    condition_list = list(combinations(all_attributes, num_of_attribute))
    reachable_matrix = test_reachability(table_connection_matrix, all_tables)
    for condition in condition_list:
        attribute_reachable = []
        table_list = []
        attribute_value_list = []
        isReachable = False
        # judge whether the target attribute table in the table_list
        isTargetAttributeIn = False
        for attribute in condition:
            isPartReachable = False
            if attribute[0] not in table_list:
                table_list.append(attribute[0])
            attribute_value_list.append(value[attribute[0]][attribute[1]])
            # if target_query_attribute is Reachable or in the same table with the condition attributes
            for target_table in target_query_attribute_tables:
                if target_table in table_list:
                    isTargetAttributeIn = True
                # if table_connection_matrix[all_tables.index(attribute[0])][all_tables.index(target_table)] or attribute[0] == target_table:
                #     isReachable = True
                if table_connection_matrix[all_tables.index(attribute[0])][all_tables.index(target_table)] or attribute[0] == target_table:
                    isPartReachable = True
            if isPartReachable:
                isReachable = True
            attribute_reachable.append(isPartReachable)

        # whether the attribute can be linked to target_query_attribute
        if isReachable == False:
            continue

        # if all the attributes from one table
        if len(table_list) == 1 and isTargetAttributeIn:
            # sql select
            attribute_specific_value_list = list(product(*attribute_value_list))
            where_conditions = []
            el_restrictions = []
            for attribute_specific_value in attribute_specific_value_list:
                temp_where_condition = []
                temp_el_restriction = []
                for i in range(len(condition)):
                    # if attribute_reachable[i]:
                        if table_attributes[condition[i][0]][condition[i][1]][0] == 'varchar':
                            temp_where_condition.append('%s=\'%s\'' % ('.'.join( str(s) for s in condition[i]), attribute_specific_value[i]))
                            temp_el_restriction.append('%s value \"%s\"^^string' % (condition[i][1], attribute_specific_value[i]))
                        else:
                            temp_where_condition.append(
                                '%s=%s' % ('.'.join(str(s) for s in condition[i]), attribute_specific_value[i]))
                            temp_el_restriction.append('%s value %s' % (condition[i][1], attribute_specific_value[i]))
                where_conditions.append(temp_where_condition)
                el_restrictions.append(temp_el_restriction)
            # sql expression
            for i in  range(len(where_conditions)):
                sql_select_where_condition = ' AND '.join(str(x) for x in where_conditions[i])
                sql_select_template = 'select %s from %s where %s' % (target_query_attribute, table_list[0], sql_select_where_condition)

                # restriction = ' and '.join(x[1] for x in condition)
                el_template = '%s and %s' % (table_list[0], ' and '.join(str(x) for x in el_restrictions[i]))
                print(sql_select_template)
                print(el_template)


        # if all the attributes from more than one table
        else:
            view_dic = {}
            view_list = []
            for attribute in condition:
                # all the attribute becomes 'attribute__table' to avoid the overlap
                view = generate_join_view(attribute, target_query_attribute, target_query_attribute_tables, reachable_matrix,
                                        all_tables, all_attributes)
                view_list.append(view)
                view_dic[attribute] = 'view%s' % (len(view_list)-1)

            sql_view_part = []
            view_product = list(product(view_list))
            for n in range(len(view_product)):
                if view_product[n][0]:
                    sql_view_part.append('('+view_product[n][0][0]+') as view%s' % (n))

            attribute_specific_value_list = list(product(*attribute_value_list))
            el_restrictions = []
            where_conditions = []
            for attribute_specific_value in attribute_specific_value_list:
                temp_where_condition = []
                temp_el_restriction = {}
                for table in table_list:
                    temp_el_restriction[table] = []
                for i in range(len(condition)):
                    # if attribute_reachable[i]:
                        if table_attributes[condition[i][0]][condition[i][1]][0] == 'varchar':
                            if condition[i][1] not in object_properties:
                                temp_el_restriction[condition[i][0]].append('%s value \"%s\"^^string' % (condition[i][1], attribute_specific_value[i]))
                            else:
                                temp_el_restriction[condition[i][0]].append(
                                    '%s value %s' % (condition[i][1], attribute_specific_value[i]))
                            temp_where_condition.append(
                                '%s=\'%s\'' % ('.'.join([view_dic[condition[i]],condition[i][1]+"__"+condition[i][0]]), attribute_specific_value[i]))
                        else:
                            temp_el_restriction[condition[i][0]].append('%s value %s' % (condition[i][1], attribute_specific_value[i]))
                            temp_where_condition.append(
                                '%s=%s' % ('.'.join([view_dic[condition[i]],condition[i][1]+"__"+condition[i][0]]), attribute_specific_value[i]))
                where_conditions.append(temp_where_condition)
                el_restrictions.append(temp_el_restriction)

            if len(sql_view_part) == 1:
                for i in range(len(where_conditions)):
                    sql_select_where_condition = ' AND '.join(str(x) for x in where_conditions[i])
                    sql_select_template = 'select %s from %s where %s' % \
                                      ('view0.'+target_query_attribute, ' '.join(x for x in sql_view_part), sql_select_where_condition)
                    el_template = generate_el_template(el_restrictions[i], reachable_matrix, all_tables, 'patient',
                                                       foreign_key_matrix)
                    print(sql_select_template)
                    print(el_template)
            else:
                sql_join_part = []
                for n in range(1, len(sql_view_part)):
                    sql_join_part.append('join %s on %s' % (sql_view_part[n], '='.join(['view0.'+target_query_attribute,'view%s.'% (n) + target_query_attribute])))
                for i in range(len(where_conditions)):
                    where_condition = where_conditions[i]
                    sql_select_where_condition = ' AND '.join(str(x) for x in where_condition)
                    sql_select_template = 'select %s from %s %s where %s' % \
                                          ('view0.' + target_query_attribute, sql_view_part[0], ' '.join(x for x in sql_join_part),
                                           sql_select_where_condition)

                    el_template = generate_el_template(el_restrictions[i], reachable_matrix, all_tables, 'patient',
                                                       foreign_key_matrix)
                    print(sql_select_template)
                    print(el_template)