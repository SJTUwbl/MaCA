#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: Gao Fang
@contact: gaofang@cetc.com.cn
@software: PyCharm
@file: system.py
@time: 2018/4/19 0019 14:46
@desc: system config
"""


class GlobalVar:
    # attack effect delay
    attack_effect_delay = True
    # hit probability enable
    hit_prob_enable = True


def get_attack_effect_delay():
    return GlobalVar.attack_effect_delay


def get_hit_prob_enable():
    return GlobalVar.hit_prob_enable

