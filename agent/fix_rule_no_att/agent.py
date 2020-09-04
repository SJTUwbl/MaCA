#! /usr/bin/env python
# -*- coding: utf-8 -*-
from pytransform import pyarmor_runtime
pyarmor_runtime()
"""
   Copyright 2018 Information Science Academy of China Electronics Technology Group Corporation

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

     http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

@author: Gao Fang
@contact: gaofang@cetc.com.cn
@software: PyCharm
@file: agent.py
@time: 2018/3/13 0013 10:51
@desc: rule based agent without attack ability
"""

from agent.fix_rule_no_att.agent_core import Agent as ag


class Agent:
    def __init__(self):
        """
        Init this agent
        """
        self.agent_core = ag()

    def set_map_info(self, size_x, size_y, detector_num, fighter_num):

        return self.agent_core.set_map_info(size_x, size_y, detector_num, fighter_num)

    def get_action(self, obs_dict, step_cnt):
        """
        get actions
        :param detector_obs_list:
        :param fighter_obs_list:
        :param joint_obs_dict:
        :param step_cnt:
        :return:
        """
        return self.agent_core.get_action(obs_dict, step_cnt)

    def get_obs_ind(self):
        return self.agent_core.get_obs_ind()
