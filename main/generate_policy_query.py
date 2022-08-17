#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Time    : 04/07/2022 22:29
# @Author  : Shuyin Ouyang
# @File    : generate_policy_query.py


def test_case1():
    # one policy and one query
    # subsumed
    # simple sql query
    # from one table
    policy = ['select patient_id from patient where hasSex=\'M\'']
    query = 'select patient_id from patient where hasSex=\'M\' AND hasAge=21'
    return policy, query

def test_case2():
    # one policy and one query
    # not subsumed
    # simple sql query
    # from one table
    policy = ['select patient_id from patient where hasSex=\'M\'']
    query = 'select patient_id from patient where hasAge=21'
    return policy, query

def test_case3():
    # one policy and one query
    # subsumed
    # complex sql query
    # from more than one table
    policy = ['select patient_id from patient where hasSex=\'M\'']
    query = 'select view1.patient_id from (select patient.patient_id,patient.hasSex,doctor.workInClinic as workInClinic__doctor from patient join appointment on patient.patient_id=appointment.registered_patient join doctor on appointment.seenBy=doctor.doctor_id) as view1 where view1.hasSex=\'M\' AND view1.workInClinic__doctor=\'gp2\''
    return policy, query

def test_case4():
    # one policy and one query
    # not subsumed
    # complex sql query
    # from more than one table
    policy = ['select patient_id from patient where hasSex=\'M\'']
    query = 'select view1.patient_id from (select patient.patient_id,patient.hasAge, doctor.workInClinic as workInClinic__doctor from patient join appointment on patient.patient_id=appointment.registered_patient join doctor on appointment.seenBy=doctor.doctor_id) as view1 where view1.hasAge=64 AND view1.workInClinic__doctor=\'gp1\''
    return policy, query

def test_case5():
    # multiple policies and one query
    # subsumed
    # complex sql query
    # from one table
    policy = ['select patient_id from patient where hasSex=\'M\'',
              'select view0.patient_id from (select patient.patient_id,appointment.seenBy as seenBy__appointment from patient join appointment on appointment.registered_patient=patient.patient_id) as view0 where view0.seenBy__appointment=\'doctor_3\'']
    query = 'select view1.patient_id from (select patient.patient_id,patient.hasSex,doctor.workInClinic as workInClinic__doctor from patient join appointment on patient.patient_id=appointment.registered_patient join doctor on appointment.seenBy=doctor.doctor_id) as view1 where view1.hasSex=\'M\' AND view1.workInClinic__doctor=\'gp2\''
    return policy, query

def test_case6():
    # multiple policies and one query
    # not subsumed
    # complex sql query
    # from one table
    policy = ['select patient_id from patient where hasSex=\'M\'',
              'select view0.patient_id from (select patient.patient_id,appointment.seenBy as seenBy__appointment from patient join appointment on appointment.registered_patient=patient.patient_id) as view0 where view0.seenBy__appointment=\'doctor_3\'']
    query = 'select view1.patient_id from (select patient.patient_id,patient.hasAge,doctor.workInClinic as workInClinic__doctor from patient join appointment on patient.patient_id=appointment.registered_patient join doctor on appointment.seenBy=doctor.doctor_id) as view1 where view1.hasAge=64 AND view1.workInClinic__doctor=\'gp1\''
    return policy, query


# royal_baby dataset

def test_case_royal_baby1():
    # one policy and one query
    # subsumed
    # simple sql query
    # from one table
    policy = ['select patient_id from baby where dataOfBirth=\'2019-06-09\'']
    query = 'select patient_id from baby where dataOfBirth=\'2019-06-09\' AND initial_weight=3670'
    return policy, query

def test_case_royal_baby2():
    # one policy and one query
    # not subsumed
    # simple sql query
    # from one table
    policy = ['select patient_id from baby where dataOfBirth=\'2019-06-09\'']
    query = 'select patient_id from baby where hasGuardian=\'guardian249\''
    return policy, query

def test_case_royal_baby3():
    # one policy and one query
    # subsumed
    # complex sql query
    # from more than one table
    policy = ['select patient_id from baby where dataOfBirth=\'2019-06-09\'']
    query = 'select view1.patient_id from (select baby.patient_id,baby.dataOfBirth,guardian.job as job__guardian from baby join guardian on guardian.guardian_id=baby.hasGuardian) as view1 where view1.dataOfBirth=\'2019-06-09\' AND view1.job__guardian=\'soldier\''
    return policy, query


def test_case_royal_baby4():
    # one policy and one query
    # not subsumed
    # complex sql query
    # from more than one table
    policy = ['select patient_id from baby where dataOfBirth=\'2019-06-09\'']
    query = 'select view1.patient_id from (select baby.patient_id,baby.sex,guardian.job as job__guardian from baby join guardian on guardian.guardian_id=baby.hasGuardian) as view1 where view1.sex=\'F\' AND view1.job__guardian=\'barber\''
    return policy, query

def test_case_royal_baby5():
    # multiple policies and one query
    # subsumed
    # complex sql query
    # from one table
    policy = ['select patient_id from baby where dataOfBirth=\'2019-06-09\'',
              'select view0.patient_id from (select baby.patient_id,guardian.job as job__guardian from baby join guardian on guardian.guardian_id=baby.hasGuardian) as view0 where view0.job__guardian=\'soldier\'']
    query = 'select view1.patient_id from (select baby.patient_id,baby.sex,guardian.job as job__guardian from baby join guardian on guardian.guardian_id=baby.hasGuardian) as view1 join (select baby.patient_id,hospital.hospital_type as hospital_type__hospital from baby join hospital on hospital.hospital_name=baby.inHospital) as view2 on view1.patient_id=view2.patient_id where view1.sex=\'F\' AND view1.job__guardian=\'soldier\' AND view2.hospital_type__hospital=\'private\''
    return policy, query

def test_case_royal_baby6():
    # multiple policies and one query
    # not subsumed
    # complex sql query
    # from one table
    policy = ['select patient_id from baby where dataOfBirth=\'2019-06-09\'',
              'select view0.patient_id from (select baby.patient_id,guardian.job as job__guardian from baby join guardian on guardian.guardian_id=baby.hasGuardian) as view0 where view0.job__guardian=\'soldier\'']
    query = 'select view1.patient_id from (select baby.patient_id,baby.sex,guardian.job as job__guardian from baby join guardian on guardian.guardian_id=baby.hasGuardian) as view1 join (select baby.patient_id,hospital.hospital_type as hospital_type__hospital from baby join hospital on hospital.hospital_name=baby.inHospital) as view2 on view1.patient_id=view2.patient_id where view1.sex=\'F\' AND view1.job__guardian=\'maid\' AND view2.hospital_type__hospital=\'private\''
    return policy, query

# size experiment

def test_case_size_10_10():
    policy = ['select patient_id from patient where attribute_1=11']
    query = 'select patient_id from patient where attribute_1=11 AND attribute_2=70'
    return policy, query

def test_case_size_10_10():
    policy = ['select patient_id from patient where attribute_1=11']
    query = 'select patient_id from patient where attribute_1=11 AND attribute_2=70'
    return policy, query

def test_case_size_10_10_2():
    policy = [
        'select patient_id from patient where attribute_1=13',
        'select patient_id from patient where attribute_8=58',
        'select patient_id from patient where attribute_6=52',
        'select patient_id from patient where attribute_5=86',
        'select patient_id from patient where attribute_10=52',
        'select patient_id from patient where attribute_10=92',
        'select patient_id from patient where attribute_3=73',
        'select patient_id from patient where attribute_6=1',
        'select patient_id from patient where attribute_8=86',
        'select patient_id from patient where attribute_2=70'
              ]
    query = 'select patient_id from patient where attribute_1=11 AND attribute_2=70'
    return policy, query


def test_case_size_100_10():
    policy = [
        'select patient_id from patient where attribute_1=7',
        'select patient_id from patient where attribute_6=46',
        'select patient_id from patient where attribute_7=63',
        'select patient_id from patient where attribute_8=21',
        'select patient_id from patient where attribute_9=71',
        'select patient_id from patient where attribute_10=88',
        'select patient_id from patient where attribute_3=76',
        'select patient_id from patient where attribute_1=50',
        'select patient_id from patient where attribute_5=70',
        'select patient_id from patient where attribute_2=47'
    ]
    query = 'select patient_id from patient where attribute_1=37 AND attribute_2=47'
    return policy, query


def test_case_size_10_100():
    policy = [
        'select patient_id from patient where attribute_5=17',
        'select patient_id from patient where attribute_3=10',
        'select patient_id from patient where attribute_6=32',
        'select patient_id from patient where attribute_17=26',
        'select patient_id from patient where attribute_20=87',
        'select patient_id from patient where attribute_46=2',
        'select patient_id from patient where attribute_47=33',
        'select patient_id from patient where attribute_39=1',
        'select patient_id from patient where attribute_37=20',
        'select patient_id from patient where attribute_1=11'
    ]
    query = 'select patient_id from patient where attribute_1=11 AND attribute_2=34'
    return policy, query

def test_case_size_100_100():
    policy = [
        'select patient_id from patient where attribute_4=100',
        'select patient_id from patient where attribute_3=52',
        'select patient_id from patient where attribute_2=61',
        'select patient_id from patient where attribute_12=76',
        'select patient_id from patient where attribute_11=10',
        'select patient_id from patient where attribute_13=24',
        'select patient_id from patient where attribute_14=99',
        'select patient_id from patient where attribute_22=14',
        'select patient_id from patient where attribute_11=7',
        'select patient_id from patient where attribute_5=59'
    ]
    query = 'select patient_id from patient where attribute_5=59 AND attribute_1=36'
    return policy, query


def test_case_size_10_1000():
    policy = [
        'select patient_id from patient where attribute_3=46'
    ]
    query = 'select patient_id from patient where attribute_3=46 AND attribute_2=57'
    return policy, query


def test_case_size_10_10000():
    policy = [
        'select patient_id from patient where attribute_6=8'
    ]
    query = 'select patient_id from patient where attribute_5=93 AND attribute_6=8'
    return policy, query

def test_case_size_100_1000():
    policy = [
        'select patient_id from patient where attribute_8=73'
    ]
    query = 'select patient_id from patient where attribute_8=73 AND attribute_9=4'
    return policy, query

def test_case_size_100_10000():
    policy = [
        'select patient_id from patient where attribute_1=76'
    ]
    query = 'select patient_id from patient where attribute_1=76 AND attribute_2=74'
    return policy, query


def test_case_size_1000_10():
    policy = [
        'select patient_id from patient where attribute_3=76'
    ]
    query = 'select patient_id from patient where attribute_3=76 AND attribute_4=7'
    return policy, query


def test_case_size_10000_10():
    policy = [
        'select patient_id from patient where attribute_1=59'
    ]
    query = 'select patient_id from patient where attribute_1=59 AND attribute_4=12'
    return policy, query