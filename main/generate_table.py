#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Time    : 15/05/2022 20:03
# @Author  : Shuyin Ouyang
# @File    : generate_table.py

import datetime
import random

# with open('data/patient.csv', 'r') as f:
#     for line in f.readlines():
#         print(line)

def generate_date():
    start_date = datetime.date(2020, 1, 1)
    end_date = datetime.date(2020, 2, 1)

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