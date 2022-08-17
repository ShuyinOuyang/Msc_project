#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Time    : 15/05/2022 20:03
# @Author  : Shuyin Ouyang
# @File    : generate_table.py

import datetime
import random
import openpyxl
import hashlib
import string
# with open('data/patient.csv', 'r') as f:
#     for line in f.readlines():
#         print(line)

def generate_date():
    start_date = datetime.date(2019, 1, 1)
    end_date = datetime.date(2020, 1, 1)

    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    random_number_of_days = random.randrange(days_between_dates)
    random_date = start_date + datetime.timedelta(days=random_number_of_days)
    return random_date

def generate_patient_table(N):
    total_num = N
    diseases = ['Chickenpox', 'Cold', 'Giardiasis', 'Flu', 'Malaria', 'Measles']
    doctor_ids = ['doctor' + str(i) for i in range(10)]
    with open('data/multi_table/patient.csv', 'a') as f:
        for i in range(N):
            random_date = generate_date()
            random_date = random_date.strftime('%m/%d/%Y')
            doctor_id = random.choice(doctor_ids)
            disease = random.choice(diseases)
            content = ','.join([str(i), disease, random_date,str(random.choice(range(1,70))),str(random.choice(['M','F'])), doctor_id])
            f.write(content+'\n')

def generate_1(N):
    # workbook = openpyxl.load_workbook('data/royal_baby.xlsx')
    with open('data/demo.csv', 'a') as f:
        for i in range(N):
            random_date = generate_date()
            random_date = random_date.strftime('%d/%m/%Y')
            content = ','.join([str('baby_%s' % str(i)),
                                random_date,
                                str(random.choice(['M','F'])),
                                str(int(round(random.uniform(1.5, 3.8),3)*1000)),
                                str('guardian%s' % str(random.randint(0,750))),
                                str('hospital_%s' % str(random.randint(0, 100)))])
            f.write(content+'\n')


def generate_2(N=750):
    jobs = ['teacher', 'doctor', 'police officer', 'cook', 'firefighter', 'bus driver', 'scientist', 'post man', 'vet', 'artist', 'pilot', 'nurse', 'baker', 'builder', 'judge', 'farmer', 'waiter', 'waitress', 'butcher', 'cashier', 'astronaut', 'football player', 'car mechanic', 'flight attendant', 'musician', 'taxi driver', 'barber', 'hairdresser', 'pharmacist', 'business man', 'office worker', 'maid', 'tour guide', 'soldier', 'sailor', 'fighter pilot', 'miner', 'plumber', 'photographer', 'reporter', 'make up artist', 'director', 'computer programmer', 'architect', 'optician', 'surgeon', 'astronomer', 'professional golf player', 'detective']
    with open('data/demo.csv', 'a') as f:
        for i in range(N+1):
            content = ','.join([str('guardian%s' % str(i)),
                                str(random.choice(['M','F'])),
                                random.choice(jobs),
                                str(random.randint(24, 68))])
            f.write(content+'\n')

def generate_3(N=100):
    all_char = '0123456789QWERTYUIOPASDFGHJKLZXCVBNM'
    with open('data/demo.csv', 'a') as f:
        for i in range(N+1):
            postcode = ''
            for _ in range(6):
                postcode += random.choice(list(all_char))
            content = ','.join([str('hospital_%s' % str(i)),
                                str(random.choice(['private', 'public'])),
                                postcode])
            f.write(content+'\n')


def generate_experiment_table(n_row, n_col):
    # generate tables that different from row and column
    with open('data/demo.csv', 'a') as f:
        for i in range(n_row + 1):
            attribute_list = []
            if i == 0:
                for j in range(n_col):
                    attribute_list.append(str('attribute_%s' % str(j+1)))
                content = ','.join([str('patient_id')] + attribute_list)
            else:
                for j in range(n_col):
                    attribute_list.append(str(random.randint(0,100)))

                content = ','.join([str('patient_%s' % str(i))] + attribute_list)
            # print(content)
            f.write(content + '\n')