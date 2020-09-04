#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: Gao Fang
@contact: gaofang@cetc.com.cn
@software: PyCharm
@file: base_agent.py
@time: 2018/3/22 0022 14:13
@desc: base class of agent
"""


class BaseAgent:
    def __init__(self):
        """
        init
        """
        self.obs_ind = 'raw'
        self.size_x = 0
        self.size_y = 0
        self.detector_num = 0
        self.fighter_num = 0

    def get_obs_ind(self):
        """
        get obs info
        :return: obs const class path.
        """
        return self.obs_ind
