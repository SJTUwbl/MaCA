#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: Gao Fang
@contact: gaofang@cetc.com.cn
@software: PyCharm
@file: config_gen.py
@time: 2019/2/26 0026 15:17
@desc: 
"""

import json

if __name__ == "__main__":
    config_dict = {}
    map_name = '1000_1000_fighter10v10'
    round_num = 6   # 必须为偶数
    max_step = 1500
    agent_list = ['fix_rule', 'fix_rule_no_att', 'simple']
    config_dict.update({'map_name': map_name})
    config_dict.update({'round_num': round_num})
    config_dict.update({'max_step': max_step})
    config_dict.update({'agent_list': agent_list})
    with open('tournament/config.ini', 'w') as f:
        json.dump(config_dict, f)
