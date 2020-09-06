#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: Xunyun Liu
@contact: xunyunliu@gmail.com
@software: PyCharm
@file: agent.py
@time:
@desc: rule based agent
"""

from agent.base_agent import BaseAgent

import copy
import random
import utility as ut
import numpy as np

DETECTOR_NUM = 0
FIGHTER_NUM = 10
COURSE_NUM = 16
ATTACK_IND_NUM = (DETECTOR_NUM + FIGHTER_NUM) * 2 + 1  # long missile attack + short missile attack + no attack
ACTION_NUM = COURSE_NUM * ATTACK_IND_NUM
LONG_MISSILE_RANGE = 120
SHORT_MISSILE_RANGE = 50
SQUARE_SIZE = 50


class Agent(BaseAgent):
    def __init__(self):
        """
        Init this agent
        :param size_x: battlefield horizontal size
        :param size_y: battlefield vertical size
        :param detector_num: detector quantity of this side
        :param fighter_num: fighter quantity of this side
        """
        BaseAgent.__init__(self)
        self.obs_ind = 'airc_homo_rule'
        self.last_random_action_set = {}
        self.to_explore_set = {}
        self.explore_destination_set = {}
        self.rule_set = 'attack'

        # if not os.path.exists('model/simple/model.pkl'):
        #     print('Error: agent simple model data not exist!')
        #     exit(1)
        # self.fighter_model = dqn.RLFighter(ACTION_NUM)

    def set_map_info(self, size_x, size_y, detector_num, fighter_num):
        self.size_x = size_x
        self.size_y = size_y
        self.detector_num = detector_num
        self.fighter_num = fighter_num

        # some eligibility checks
        if self.detector_num != 0:
            print('Error: agents using airc_homo_rule can only be used in a homogeneous environment!')
            exit(1)
        if self.size_x % SQUARE_SIZE != 0 or self.size_y % SQUARE_SIZE != 0:
            print('Error, the map size is not a multiple of SQUARE_SIZE')
            exit(1)

        # initialise data structures for map exploration
        self.to_explore_set = set(range((size_x // SQUARE_SIZE) * (size_y // SQUARE_SIZE)))
        # initialise last_random_action_set
        for i in range(self.fighter_num):
            # it doesn't matter what the initial value is as it will be overwritten in the first round
            self.last_random_action_set[i] = [0, 1, 0, 0]

    def __reset(self):
        pass

    def get_action(self, obs_dict, step_cnt):
        """
        get actions
        :param detector_obs_list:
        :param fighter_obs_list:
        :param joint_obs_dict:
        :param step_cnt:
        :return:
        """
        # initialise the explore_destination_set based on the birthplace of the agent
        if step_cnt == 1:
            for i in range(self.fighter_num):
                self.explore_destination_set[i] = (self.size_x - obs_dict[i]['pos_x'], obs_dict[i]['pos_y'])
        detector_action = []
        fighter_action = []
        # loop over the fighter list to generate actions
        for index in range(self.fighter_num):
            # [0, 1, 0, 0] is just a placeholder
            tentative_action = np.array([0, 1, 0, 0], dtype=np.int32)
            if obs_dict[index]['alive']:
                try:
                    if self.rule_set == 'random':
                        tentative_action = self.choose_action_random(index, step_cnt)
                    elif self.rule_set == 'random_attack':
                        tentative_action = self.choose_action_random_attack(obs_dict, index, step_cnt)
                    elif self.rule_set == 'explore':
                        tentative_action = self.choose_action_explore(obs_dict, index)
                    elif self.rule_set == 'attack':
                        tentative_action = self.choose_action_attack(obs_dict, index)
                    elif self.rule_set == 'still':
                        tentative_action = self.choose_action_still(step_cnt)
                except AttributeError:
                    print("agent is missing a rule_set attribute. Now flying towards right as default.")
                # action formation
                # true_action[0] = int(360 / COURSE_NUM * int(tmp_action[0] / ATTACK_IND_NUM))
                # true_action[3] = int(tmp_action[0] % ATTACK_IND_NUM)
            # radar and interference logic

            tentative_action[1] = step_cnt % 10 + 1
            tentative_action[2] = step_cnt % 10 + 1
            tmp_action = {}
            tmp_action['course'] = tentative_action[0]
            tmp_action['r_iswork'] = True
            tmp_action['r_fre_point'] = 2
            tmp_action['j_iswork'] = True
            tmp_action['j_fre_point'] = 2
            if tentative_action[3] > self.fighter_num:
                tmp_action['hit_target'] = tentative_action[3] - self.fighter_num
                tmp_action['missile_type'] = 2
            else:
                tmp_action['hit_target'] = tentative_action[3]
                tmp_action['missile_type'] = 1
            fighter_action.append(copy.deepcopy(tmp_action))
        # fighter_action = np.array(fighter_action)
        return detector_action, fighter_action

    # the logic of engagement with enemies
    def engage_enemy(self, tmp_action, obs_dict, index):
        # default -- no attack allowed
        tmp_action[3] = 0
        if 'target_list' in obs_dict[index]:
            # flying towards the nearest enemy
            tmp_action[0] = obs_dict[index]['target_list'][0]['angle']
            target_id = obs_dict[index]['target_list'][0]['id']
            target_distance = obs_dict[index]['target_list'][0]['distance']
            # check if the nearest enemy has been attacked
            strike_list = obs_dict['strike_list']
            strike_target_id_set = set(ele['target_id'] for ele in strike_list)
            if target_id in strike_target_id_set:
                return tmp_action
            # perform attack while having enough ammunition
            if obs_dict[index]['s_missile_left'] + obs_dict[index]['l_missile_left'] == 0:
                return tmp_action
            elif target_distance <= SHORT_MISSILE_RANGE:
                if obs_dict[index]['s_missile_left'] > 0:
                    tmp_action[3] = target_id + 10
                else:
                    tmp_action[3] = target_id
            elif SHORT_MISSILE_RANGE < target_distance <= LONG_MISSILE_RANGE:
                if obs_dict[index]['l_missile_left'] > 0:
                    tmp_action[3] = target_id
        return tmp_action

    def choose_action_random(self, index, step_cnt):
        if step_cnt % 20 == 1:
            self.last_random_action_set[index][0] = random.randint(0, 359)
        return self.last_random_action_set[index]

    def choose_action_random_attack(self, obs_dict, index, step_cnt):
        random_action = self.choose_action_random(index, step_cnt)
        return self.engage_enemy(random_action, obs_dict, index)

    def choose_action_explore(self, obs_dict, index):
        # maintain the data structure for map exploration
        area_x = int(obs_dict[index]['pos_x'] / SQUARE_SIZE)
        area_y = int(obs_dict[index]['pos_y'] / SQUARE_SIZE)
        explored_index = area_x * (self.size_y / SQUARE_SIZE) + area_y
        if explored_index >= (self.size_x / SQUARE_SIZE) * (self.size_y / SQUARE_SIZE):
            print('explored_index out of range!')
            explored_index = (self.size_x / SQUARE_SIZE) * (self.size_y / SQUARE_SIZE) - 1
        if explored_index in self.to_explore_set:
            self.to_explore_set.remove(explored_index)
            if len(self.to_explore_set) == 0:
                self.to_explore_set = set(range(round((self.size_x / SQUARE_SIZE) * (self.size_y / SQUARE_SIZE))))
        # if agent has a destination to explore
        if index in self.explore_destination_set:
            # delete the destination when getting close enough
            if ut.distance(obs_dict[index]['pos_x'], obs_dict[index]['pos_y'], self.explore_destination_set[index][0],
                           self.explore_destination_set[index][1]) <= 5:
                # print('trying to delete the key')
                del self.explore_destination_set[index]
                # print('delete succesfully')

        # if the agent has no destination, randomly select a destination from the to_explore_set
        if index not in self.explore_destination_set:
            if len(self.to_explore_set) == 0:
                print('Error! to_explore_set is empty')
            selected_ele = random.sample(self.to_explore_set, 1)
            # print('selected_ele: ', selected_ele)
            ele_index_x = int(selected_ele[0] / (self.size_y / SQUARE_SIZE))
            # print('ele_index_x: ', ele_index_x)
            ele_index_y = int(selected_ele[0] % (self.size_y / SQUARE_SIZE))
            # print('ele_index_y', ele_index_y)
            ele_pos_x = int(ele_index_x * SQUARE_SIZE + SQUARE_SIZE / 2)
            ele_pos_y = int(ele_index_y * SQUARE_SIZE + SQUARE_SIZE / 2)
            # print('ele_pos_x: ', ele_pos_x, 'ele_pos_y', ele_pos_y)
            self.explore_destination_set[index] = (ele_pos_x, ele_pos_y)
            # print('self.explore_destination_set[index]: ', self.explore_destination_set[index])
            # print('angle: ',
            #      ut.angle(obs_dict[index]['pos_x'], obs_dict[index]['pos_y'], self.explore_destination_set[index][0],
            #               self.explore_destination_set[index][1]))

        # navigating towards the explore destination
        return [ut.angle(obs_dict[index]['pos_x'], obs_dict[index]['pos_y'], self.explore_destination_set[index][0],
                         self.explore_destination_set[index][1]), 1, 0, 0]

    def choose_action_attack(self, obs_dict, index):
        return self.engage_enemy(self.choose_action_explore(obs_dict, index), obs_dict, index)

    @staticmethod
    def choose_action_still(step_cnt):
        if 1 <= step_cnt % 40 <= 10:
            return [0, 1, 0, 0]
        elif 11 <= step_cnt % 40 <= 20:
            return [90, 1, 0, 0]
        elif 21 <= step_cnt % 40 <= 30:
            return [180, 1, 0, 0]
        else:
            return [270, 1, 0, 0]
