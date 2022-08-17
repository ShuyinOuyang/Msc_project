#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Time    : 01/08/2022 00:01
# @Author  : Shuyin Ouyang
# @File    : draw.py

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.pyplot import MultipleLocator


# time cost of ontology learning from different col/row of database
# 10 100 1000 10000
# 10
# 100
# 1000
# 10000
ontology_learning = [
    [854, 1045, 3238, 110908],
    [1548, 7022, 76901, 1878924],
    [46641],
    [6158279]
]

# time cost of subsumption checking from different col/row of database
# 10 100 1000 10000
# 10
# 100
# 1000
# 10000
subsumption_checking = [
    [1107, 1416, 1986, 7046],
    [1508, 4094, 28506, 475943],
    [20031],
    [3096027]
]

# 1~10
# 10_10
# 100_10
# 10_100
# 100_100
subsumption_checking_policy_size = [
    [1107, 1192, 1386, 1227, 1264, 1229, 1359, 1280, 1279, 1426],
    [1508, 2376, 2099, 2210,2503, 2648, 2852, 3000, 3328, 3566],
    [1416, 1430, 1454, 1430, 1528, 1507, 1571, 1570, 1585, 1711],
    [4094, 5093, 6728, 8451, 10074, 11914, 14265, 15525, 16392, 18713]
]


# plot1: subsumption checking w.r.t. policy size
def subsumption_checking_policy_size_():
    x = [i for i in range(1,11)]
    plt.plot(x, subsumption_checking_policy_size[0], label='row:10, col:10', marker='o', markerfacecolor='white')
    plt.plot(x, subsumption_checking_policy_size[1], label='row:100, col:10', marker='o', markerfacecolor='white')
    plt.plot(x, subsumption_checking_policy_size[2], label='row:10, col:100', marker='o', markerfacecolor='white')
    plt.plot(x, subsumption_checking_policy_size[3], label='row:100, col:100', marker='o', markerfacecolor='white')
    plt.ylabel('Total time cost of subsumption checking (ms)')
    plt.xlabel('The number of policies')
    my_x_ticks = np.arange(1, 10.5, 1)
    plt.xticks(my_x_ticks)

    plt.legend()
    # plt.legend(handles=[l1,l2,l3,l4], labels=['10_10','100_10', '10_100', '100_100'], loc='best')
    plt.show()

def subsumption_checking_policy_size_avg():
    x = [i for i in range(1,11)]
    plt.plot(x, [subsumption_checking_policy_size[0][i]/(i+1) for i in range(10)], label='row:10, col:10', marker='o', markerfacecolor='white')
    plt.plot(x, [subsumption_checking_policy_size[1][i]/(i+1) for i in range(10)], label='row:100, col:10', marker='o', markerfacecolor='white')
    plt.plot(x, [subsumption_checking_policy_size[2][i]/(i+1) for i in range(10)], label='row:10, col:100', marker='o', markerfacecolor='white')
    plt.plot(x, [subsumption_checking_policy_size[3][i]/(i+1) for i in range(10)], label='row:100, col:100', marker='o', markerfacecolor='white')
    plt.ylabel('Average time cost of subsumption checking (ms)')
    plt.xlabel('The number of policies')
    my_x_ticks = np.arange(1, 10.5, 1)
    plt.xticks(my_x_ticks)

    plt.legend()
    # plt.legend(handles=[l1,l2,l3,l4], labels=['10_10','100_10', '10_100', '100_100'], loc='best')
    plt.show()

# plot2: ontology learning w.r.t. col size
def ontology_learning_col_size():
    x = [pow(10,i) for i in range(1, 5)]
    plt.plot(x, ontology_learning[0], label='row:10', marker='o', markerfacecolor='white')
    plt.plot(x, ontology_learning[1], label='row:100', marker='o', markerfacecolor='white')
    plt.ylabel('Time cost of ontology learning (ms)')
    plt.xlabel('The size of table column')
    plt.xscale('log')
    plt.yscale('log')
    plt.legend()
    plt.show()

# plot3: ontology learning w.r.t. row size
def ontology_learning_row_size():
    x = [pow(10, i) for i in range(1, 5)]
    plt.plot(x, [i[0] for i in ontology_learning], label='col:10', marker='o', markerfacecolor='white')
    # plt.plot(x, subsumption_checking[1], label='row:100', marker='o', markerfacecolor='white')
    plt.ylabel('Time cost of ontology learning (ms)')
    plt.xlabel('The size of table row')
    plt.xscale('log')
    plt.yscale('log')
    plt.legend()
    # plt.title('Time cost of ontology learning under different sizes of table column.')
    plt.show()


# plot4: subsumption checking w.r.t. col size
def subsumption_checking_col_size():
    x = [pow(10, i) for i in range(1, 5)]
    plt.plot(x, subsumption_checking[0], label='row:10', marker='o', markerfacecolor='white')
    plt.plot(x, subsumption_checking[1], label='row:100', marker='o', markerfacecolor='white')
    plt.ylabel('Time cost of subsumption checkingg (ms)')
    plt.xlabel('The size of table column')
    plt.xscale('log')
    plt.yscale('log')
    plt.legend()
    plt.show()

# plot5: subsumption checking w.r.t. row size
def subsumption_checking_row_size():
    x = [pow(10, i) for i in range(1, 5)]
    plt.plot(x, [i[0] for i in subsumption_checking], label='col:10', marker='o', markerfacecolor='white')
    # plt.plot(x, subsumption_checking[1], label='row:100', marker='o', markerfacecolor='white')
    plt.ylabel('Time cost of subsumption checking (ms)')
    plt.xlabel('The size of table row')
    plt.xscale('log')
    plt.yscale('log')
    plt.legend()
    # plt.title('Time cost of ontology learning under different sizes of table column.')
    plt.show()