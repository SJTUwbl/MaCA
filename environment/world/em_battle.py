import copy
import random
import numpy as np
import world.config as config
from render.render_pic import Render
import configuration.reward as reward
import world.strike_calc as strike_calc
import world.position_calc as position_calc
import world.detection_calc as detection_calc


class BattleField:
    def __init__(self, size_x, size_y, o_detector_list, o_fighter_list, e_detector_list, e_fighter_list, max_step=5000, render=False, render_interval=1, random_pos=False, log=False, random_seed=-1):
        '''
        环境类初始化
        :param size_x: 横向尺寸
        :param size_y: 纵向尺寸
        :param o_detector_list: 势力1预警机配置
        :param o_fighter_list: 势力1战机配置
        :param e_detector_list: 势力2预警机配置
        :param e_fighter_list: 势力2战机配置
        :param max_step:最大step，0：无限制
        :param render:显示控制
        :param render_interval:render显示间隔
        :param random_pos:初始位置配置(False: 势力1在左，势力2在右；True:上下左右随机初始位置，双方相对)
        :param log: 日志开启指示，False：无日志，其他值：日志文件夹名称
        :param random_seed: 随机数种子值，-1：重新生成，其他：种子值
        '''

        self.battlefield_size_x = size_x
        self.battlefield_size_y = size_y
        self.e_detector_num     = len(e_detector_list)
        self.e_fighter_num      = len(e_fighter_list)
        self.o_detector_num     = len(o_detector_list)
        self.o_fighter_num      = len(o_fighter_list)
        self.step_count         = 0
        self.max_step           = max_step
        self.done               = False
        self.render_flag        = render
        self.render_interval    = render_interval
        self.random_seed        = random_seed
        self.random_pos         = random_pos
        self.log                = log
        self.render_obj         = Render(self.battlefield_size_x, self.battlefield_size_y)
        self.log_obj            = None
        if random_seed != -1:
            random.seed(random_seed)
        self.random_obj         = random


        self.e_detector_property_list = e_detector_list
        self.e_detector_reward = [0] * self.e_detector_num
        self.e_detector_status_list = []
        self.e_fighter_property_list = e_fighter_list
        self.e_fighter_reward = [0] * self.e_fighter_num
        self.e_fighter_status_list = []
        self.e_passive_detection_enemy_list = []
        self.e_strike_list = []
        self.e_game_reward = 0

        self.o_detector_property_list = o_detector_list
        self.o_detector_reward = [0] * self.o_detector_num
        self.o_detector_status_list = []
        self.o_fighter_property_list = o_fighter_list
        self.o_fighter_reward = [0] * self.o_fighter_num
        self.o_fighter_status_list = []
        self.o_passive_detection_enemy_list = []
        self.o_strike_list = []
        self.o_game_reward = 0

        self.side1_detector_action = []
        self.side1_fighter_action  = []
        self.side2_detector_action = []
        self.side2_fighter_action  = []

        pos_x, pos_y, o_course, e_course = position_calc.pos_generate(self.o_detector_num, self.o_fighter_num, self.e_detector_num, self.e_fighter_num, \
            self.battlefield_size_x, self.battlefield_size_y, self.random_obj, self.random_pos)

        for index in range(self.o_detector_num + self.o_fighter_num):
            status = {}
            status['id'] = index + 1
            status['alive'] = True
            status['pos_x'] = pos_x[index]
            status['pos_y'] = pos_y[index]
            status['course'] = o_course
            status['radar_enable'] = True
            status['radar_fp'] = 1
            status['radar_visible_list'] = []
            status['passive_location_ind'] = False
            status['detection_count_list'] = [0 for i in range(self.e_fighter_num)]
            if index >= self.o_detector_num:
                status['radar_enable'] = False
                status['l_missile_left'] = config.get_l_missile_num()
                status['s_missile_left'] = config.get_s_missile_num()
                status['j_enable'] = False
                status['j_fp'] = 0
                status['j_receive_list'] = []
                self.o_fighter_status_list.append(status.copy())
            else:
                self.o_detector_status_list.append(status.copy())
        for index in range(self.e_detector_num + self.e_fighter_num):
            status = {}
            status['id'] = index + 1
            status['alive'] = True
            status['pos_x'] = pos_x[index+self.o_detector_num+self.o_fighter_num]
            status['pos_y'] = pos_y[index+self.o_detector_num+self.o_fighter_num]
            status['course'] = e_course
            status['radar_enable'] = True
            status['radar_fp'] = 1
            status['radar_visible_list'] = []
            status['passive_location_ind'] = False
            status['detection_count_list'] = [0 for i in range(self.o_fighter_num)]
            if index >= self.e_detector_num:
                status['radar_enable'] = False
                status['l_missile_left'] = config.get_l_missile_num()
                status['s_missile_left'] = config.get_s_missile_num()
                status['j_enable'] = False
                status['j_fp'] = 0
                status['j_receive_list'] = []
                self.e_fighter_status_list.append(status.copy())
            else:
                self.e_detector_status_list.append(status.copy())

        for index in range(self.e_detector_num + self.e_fighter_num):
            action = {}
            action['course'] = e_course
            action['r_iswork'] = True
            action['r_fre_point'] = 1
            if index >= self.e_detector_num:
                action['r_iswork'] = False
                action['j_iswork'] = False
                action['j_fre_point'] = 0
                action['hit_target'] = 0
                action['missile_type'] = 0
                self.side2_fighter_action.append(action.copy())
            else:
                self.side2_detector_action.append(action.copy())
        for index in range(self.o_detector_num + self.o_fighter_num):
            action = {}
            action['course'] = o_course
            action['r_iswork'] = True
            action['r_fre_point'] = 1
            if index >= self.o_detector_num:
                action['r_iswork'] = False
                action['j_iswork'] = False
                action['j_fre_point'] = 0
                action['hit_target'] = 0
                action['missile_type'] = 0
                self.side1_fighter_action.append(action.copy())
            else:
                self.side1_detector_action.append(action.copy())

    def get_alive_status(self, o_detector_status_list, o_fighter_status_list, e_detector_status_list, e_fighter_status_list):
        
        side1_detector_alive_num = 0
        side1_fighter_alive_num  = 0
        side1_l_missile_left     = 0
        side1_s_missile_left     = 0

        side2_detector_alive_num = 0
        side2_fighter_alive_num  = 0
        side2_l_missile_left     = 0
        side2_s_missile_left     = 0

        for item in o_detector_status_list:
            if item['alive']:
                side1_detector_alive_num += 1
        for item in o_fighter_status_list:
            if item['alive']:
                side1_fighter_alive_num += 1
                side1_l_missile_left += item['l_missile_left']
                side1_s_missile_left += item['s_missile_left']
        for item in e_detector_status_list:
            if item['alive']:
                side2_detector_alive_num += 1
        for item in e_fighter_status_list:
            if item['alive']:
                side2_fighter_alive_num += 1
                side2_l_missile_left += item['l_missile_left']
                side2_s_missile_left += item['s_missile_left']

        return side1_detector_alive_num, side1_fighter_alive_num, side1_l_missile_left, side1_s_missile_left, \
        side2_detector_alive_num, side2_fighter_alive_num, side2_l_missile_left, side2_s_missile_left

    def get_done(self):
        '''
        获取当前done
        :return: done: True, False
        '''
        return self.done

    def get_obs_raw(self):
        '''
        获取当前obs
        :return:obs
        detector data obs:{'id':编号, 'alive': 存活, 'pos_x': 横坐标, 'pos_y': 纵坐标, 'course': 航向, 'r_iswork': 雷达开关, 'r_fre_point': 频点,
              'r_visible_list': 雷达可见敌人}
        fighter data obs:{'id':编号, 'alive': 存活, 'pos_x': 横坐标, 'pos_y': 纵坐标, 'course': 航向, 'r_iswork': 雷达开关, 'r_fre_point': 频点,
              'r_visible_list': 雷达可见敌人, 'j_iswork': 干扰机开关, 'j_fre_point': 干扰机频点, 'j_recv_list': 干扰机发现信号源, 'l_missile_left': 远程导弹余量, 's_missile_left': 中程导弹余量}
        '''
        side1_detector_obs_list = []
        side1_fighter_obs_list  = []
        side2_detector_obs_list = []
        side2_fighter_obs_list  = []

        dict_key_list = ['id', 'alive', 'pos_x', 'pos_y', 'course', 'r_iswork', 'r_fre_point', 'r_visible_list']
        list_key_list = ['id', 'alive', 'pos_x', 'pos_y', 'course', 'radar_enable', 'radar_fp', 'radar_visible_list']
        for index in range(self.o_detector_num):
            side1_detector_obs_dict = {}
            for key_index in range(len(dict_key_list)):
                side1_detector_obs_dict[dict_key_list[key_index]] = self.o_detector_status_list[index][list_key_list[key_index]]  
            side1_detector_obs_dict['last_reward'] = self.o_detector_reward[index]
            side1_detector_obs_dict['last_action'] = self.side1_detector_action[index]
            side1_detector_obs_list.append(side1_detector_obs_dict.copy())
            
        for index in range(self.e_detector_num):
            side2_detector_obs_dict = {}
            for key_index in range(len(dict_key_list)):
                side2_detector_obs_dict[dict_key_list[key_index]] = self.e_detector_status_list[index][list_key_list[key_index]]
            side2_detector_obs_dict['last_reward'] = self.e_detector_reward[index]
            side2_detector_obs_dict['last_action'] = self.side2_detector_action[index]
            side2_detector_obs_list.append(side2_detector_obs_dict.copy())

        dict_key_list += ['j_iswork', 'j_fre_point', 'j_recv_list', 'l_missile_left', 's_missile_left']
        list_key_list += ['j_enable', 'j_fp',     'j_receive_list', 'l_missile_left', 's_missile_left']
        for index in range(self.o_fighter_num):
            side1_fighter_obs_dict = {}
            for key_index in range(len(dict_key_list)):
                side1_fighter_obs_dict[dict_key_list[key_index]] = self.o_fighter_status_list[index][list_key_list[key_index]]
            side1_fighter_obs_dict['striking_list'] = []
            side1_fighter_obs_dict['striking_dict_list'] = []
            for item in self.o_strike_list:
                if item['attacker_id'] == self.o_fighter_status_list[index]['id']:
                    side1_fighter_obs_dict['striking_list'].append(item['target_id'])
                    striking_dict = {}
                    striking_dict['target_id'] = item['target_id']
                    if item['target_id'] > self.e_detector_num:
                        striking_dict['pos_x'] = self.e_fighter_status_list[item['target_id']-self.e_detector_num-1]['pos_x']
                        striking_dict['pos_y'] = self.e_fighter_status_list[item['target_id']-self.e_detector_num-1]['pos_y']
                        striking_dict['type']  = 1
                    else:
                        striking_dict['pos_x'] = self.e_detector_status_list[item['target_id']-1]['pos_x']
                        striking_dict['pos_y'] = self.e_detector_status_list[item['target_id']-1]['pos_y']
                        striking_dict['type']  = 0
                    side1_fighter_obs_dict['striking_dict_list'].append(striking_dict.copy())
            
            side1_fighter_obs_dict['last_reward'] = self.o_fighter_reward[index]
            side1_fighter_obs_dict['last_action'] = self.side1_fighter_action[index]
            side1_fighter_obs_list.append(side1_fighter_obs_dict.copy())

        for index in range(self.e_fighter_num):
            side2_fighter_obs_dict = {}
            for key_index in range(len(dict_key_list)):
                side2_fighter_obs_dict[dict_key_list[key_index]] = self.e_fighter_status_list[index][list_key_list[key_index]]
            side2_fighter_obs_dict['striking_list'] = []
            side2_fighter_obs_dict['striking_dict_list'] = []
            for item in self.e_strike_list:
                if item['attacker_id'] == self.e_fighter_status_list[index]['id']:
                    side2_fighter_obs_dict['striking_list'].append(item['target_id'])
                    striking_dict = {}
                    striking_dict['target_id'] = item['target_id']
                    if item['target_id'] > self.o_detector_num:
                        striking_dict['pos_x'] = self.o_fighter_status_list[item['target_id']-self.o_detector_num-1]['pos_x']
                        striking_dict['pos_y'] = self.o_fighter_status_list[item['target_id']-self.o_detector_num-1]['pos_y']
                        striking_dict['type']  = 1
                    else:
                        striking_dict['pos_x'] = self.o_detector_status_list[item['target_id']-1]['pos_x']
                        striking_dict['pos_y'] = self.o_detector_status_list[item['target_id']-1]['pos_y']
                        striking_dict['type']  = 0
                    side2_fighter_obs_dict['striking_dict_list'].append(striking_dict.copy())
            side2_fighter_obs_dict['last_reward'] = self.e_fighter_reward[index]
            side2_fighter_obs_dict['last_action'] = self.side2_fighter_action[index]
            side2_fighter_obs_list.append(side2_fighter_obs_dict.copy())

        side1_joint_obs_list = {}
        side1_joint_obs_list['strike_list'] = self.o_strike_list
        side1_joint_obs_list['passive_detection_enemy_list'] = []
        side2_joint_obs_list = {}
        side2_joint_obs_list['strike_list'] = self.e_strike_list
        side2_joint_obs_list['passive_detection_enemy_list'] = []

        return (side1_detector_obs_list, side1_fighter_obs_list, side1_joint_obs_list, side2_detector_obs_list, side2_fighter_obs_list, side2_joint_obs_list)

    def get_reward(self):
        # TODO: uncomplete
        return self.get_reward_list()
   
    def get_reward_list(self):
        '''
        获取当前reward
        :return:o_detector_reward：o方预警机动作回报，o_fighter_reward：o方战机动作回报，o_game_reward，o方输赢回报
                e_detector_reward：e方预警机动作回报，e_fighter_reward：e方战机动作回报，e_game_reward，e方输赢回报
        '''
        return self.o_detector_reward, self.o_fighter_reward, self.o_game_reward, \
        self.e_detector_reward, self.e_fighter_reward, self.e_game_reward
   
    def reset(self):
        self.step_count = 0
        self.done = False
        self.e_detector_reward = [0] * self.e_detector_num
        self.e_detector_status_list.clear()
        self.e_fighter_reward = [0] * self.e_fighter_num
        self.e_fighter_status_list.clear()
        self.e_passive_detection_enemy_list.clear()
        self.e_strike_list.clear()
        self.e_game_reward = 0

        self.o_detector_reward = [0] * self.o_detector_num
        self.o_detector_status_list.clear()
        self.o_fighter_reward = [0] * self.o_fighter_num
        self.o_fighter_status_list.clear()
        self.o_passive_detection_enemy_list.clear()
        self.o_strike_list.clear()
        self.o_game_reward = 0

        self.side1_detector_action.clear()
        self.side1_fighter_action.clear()
        self.side2_detector_action.clear()
        self.side2_fighter_action.clear()

        pos_x, pos_y, o_course, e_course = position_calc.pos_generate(self.e_detector_num, self.e_fighter_num, self.o_detector_num, self.o_fighter_num, \
            self.battlefield_size_x, self.battlefield_size_y, self.random_obj, False)
        
        for index in range(self.o_detector_num + self.o_fighter_num):
            status = {}
            status['id'] = index + 1
            status['alive'] = True
            status['pos_x'] = pos_x[index]
            status['pos_y'] = pos_y[index]
            status['course'] = o_course
            status['radar_enable'] = True
            status['radar_fp'] = 1
            status['radar_visible_list'] = []
            status['passive_location_ind'] = False
            status['detection_count_list'] = [0 for i in range(self.e_fighter_num)]
            if index >= self.o_detector_num:
                status['radar_enable'] = False
                status['l_missile_left'] = config.get_l_missile_num()
                status['s_missile_left'] = config.get_s_missile_num()
                status['j_enable'] = False
                status['j_fp'] = 0
                status['j_receive_list'] = []
                self.o_fighter_status_list.append(status.copy())
            else:
                self.o_detector_status_list.append(status.copy())

        for index in range(self.e_detector_num + self.e_fighter_num):
            status = {}
            status['id'] = index + 1
            status['alive'] = True
            status['pos_x'] = pos_x[index+self.o_detector_num+self.o_fighter_num]
            status['pos_y'] = pos_y[index+self.o_detector_num+self.o_fighter_num]
            status['course'] = e_course
            status['radar_enable'] = True
            status['radar_fp'] = 1
            status['radar_visible_list'] = []
            status['passive_location_ind'] = False
            status['detection_count_list'] = [0 for i in range(self.o_fighter_num)]
            if index >= self.e_detector_num:
                status['radar_enable'] = False
                status['l_missile_left'] = config.get_l_missile_num()
                status['s_missile_left'] = config.get_s_missile_num()
                status['j_enable'] = False
                status['j_fp'] = 0
                status['j_receive_list'] = []
                self.e_fighter_status_list.append(status.copy())
            else:
                self.e_detector_status_list.append(status.copy())

        for index in range(self.e_detector_num + self.e_fighter_num):
            action = {}
            action['course'] = e_course
            action['r_iswork'] = True
            action['r_fre_point'] = 1
            if index >= self.e_detector_num:
                action['r_iswork'] = False
                action['j_iswork'] = False
                action['j_fre_point'] = 0
                action['hit_target'] = 0
                action['missile_type'] = 0
                self.side2_fighter_action.append(action.copy())
            else:
                self.side2_detector_action.append(action.copy())
        for index in range(self.o_detector_num + self.o_fighter_num):
            action = {}
            action['course'] = o_course
            action['r_iswork'] = True
            action['r_fre_point'] = 1
            if index >= self.o_detector_num:
                action['r_iswork'] = False
                action['j_iswork'] = False
                action['j_fre_point'] = 0
                action['hit_target'] = 0
                action['missile_type'] = 0
                self.side1_fighter_action.append(action.copy())
            else:
                self.side1_detector_action.append(action.copy())
        # self.env.reset()
   
    def set_surrender(self, side):
        '''
        投降
        :param side: 0: side1, 1:side2, 2: both
        :return:
        '''
        self.done = True
        if side == 0:
            self.o_game_reward = reward.get_reward_totally_lose()
            self.e_game_reward = reward.get_reward_totally_win()
        if side == 1:
            self.o_game_reward = reward.get_reward_totally_win()
            self.e_game_reward = reward.get_reward_totally_lose()
        if side == 2:
            self.o_game_reward = reward.get_reward_draw()
            self.e_game_reward = reward.get_reward_draw()

    def show(self):
        obs_data = self.get_obs_raw()
        self.render_obj.dis_update(self.done, self.step_count, obs_data[0], obs_data[1], obs_data[3], obs_data[4], self.o_detector_reward, self.o_fighter_reward, self.e_detector_reward, self.e_fighter_reward, self.o_game_reward, self.e_game_reward)

    def step(self, side1_detector_action, side1_fighter_action, side2_detector_action, side2_fighter_action):
        '''
        接收动作信息执行step，可支持array和list两种形式动作
        :param side1_detector_action:
        :param side1_fighter_action:
        :param side2_detector_action:
        :param side2_fighter_action:
        :return:
        '''
        self.side1_detector_action = copy.deepcopy(side1_detector_action)
        self.side1_fighter_action  = copy.deepcopy(side1_fighter_action)
        self.side2_detector_action = copy.deepcopy(side2_detector_action)
        self.side2_fighter_action  = copy.deepcopy(side2_fighter_action)
        self.step_count += 1
        
        # self.env.step(side1_detector_action, side1_fighter_action, side2_detector_action, side2_fighter_action)

        # generate detector and fighter context
        e_detector_context_list = []
        o_detector_context_list = []
        e_fighter_context_list = []
        o_fighter_context_list = []
        for index in range(self.e_detector_num):
            self_context = {}
            self_context.update(self.e_detector_property_list[index])
            self_context.update(self.e_detector_status_list[index])
            e_detector_context_list.append(self_context.copy())
        for index in range(self.o_detector_num):
            self_context = {}
            self_context.update(self.o_detector_property_list[index])
            self_context.update(self.o_detector_status_list[index])
            o_detector_context_list.append(self_context.copy())
        for index in range(self.e_fighter_num):
            self_context = {}
            self_context.update(self.e_fighter_property_list[index])
            self_context.update(self.e_fighter_status_list[index])
            e_fighter_context_list.append(self_context.copy())
        for index in range(self.o_fighter_num):
            self_context = {}
            self_context.update(self.o_fighter_property_list[index])
            self_context.update(self.o_fighter_status_list[index])
            o_fighter_context_list.append(self_context.copy())

        # update strike list
        for index in range(self.o_fighter_num):
            print(side1_fighter_action[index])
            if self.o_fighter_status_list[index]['alive'] and side1_fighter_action[index]['hit_target']:
                target_id = side1_fighter_action[index]['hit_target']
                missile_type = side1_fighter_action[index]['missile_type']
                enemy_status = None
                enemy_index = 0
                if missile_type == config.get_s_missile_type():
                    if self.o_fighter_status_list[index]['s_missile_left'] <= 0:
                        continue
                    self.o_fighter_status_list[index]['s_missile_left'] -= 1
                if missile_type == config.get_l_missile_type():
                    if self.o_fighter_status_list[index]['l_missile_left'] <= 0:
                        continue
                    self.o_fighter_status_list[index]['l_missile_left'] -= 1
                if target_id > self.e_detector_num + self.e_fighter_num:
                    target_id -= self.e_detector_num + self.e_fighter_num
                if target_id > self.e_detector_num:
                    enemy_status = self.e_fighter_status_list
                    enemy_index = target_id - self.e_detector_num - 1
                else:
                    enemy_status = self.e_detector_status_list
                    enemy_index = target_id - 1
                valid = strike_calc.strike_act_validation_and_initiation(missile_type, o_fighter_context_list[index], o_detector_context_list,
                                                                         enemy_status[enemy_index], self.o_strike_list)
                if valid:
                    self.o_fighter_reward[index] += reward.get_reward_strike_act_valid()
                else:
                    self.o_fighter_reward[index] += reward.get_reward_strike_act_invalid()
        for index in range(self.e_fighter_num):
            if self.e_fighter_status_list[index]['alive'] and side2_fighter_action[index]['hit_target']:
                target_id = side2_fighter_action[index]['hit_target']
                missile_type = side2_fighter_action[index]['missile_type']
                enemy_status = None
                enemy_index = 0
                if missile_type == config.get_s_missile_type():
                    if self.e_fighter_status_list[index]['s_missile_left'] <= 0:
                        continue
                    self.e_fighter_status_list[index]['s_missile_left'] -= 1
                if missile_type == config.get_l_missile_type():
                    if self.e_fighter_status_list[index]['l_missile_left'] <= 0:
                        continue
                    self.e_fighter_status_list[index]['l_missile_left'] -= 1
                if target_id > self.o_detector_num + self.o_fighter_num:
                    target_id -= self.o_detector_num + self.o_fighter_num
                if target_id > self.o_detector_num:
                    enemy_status = self.o_fighter_status_list
                    enemy_index = target_id - self.o_detector_num - 1
                else:
                    enemy_status = self.o_detector_status_list
                    enemy_index = target_id - 1
                valid = strike_calc.strike_act_validation_and_initiation(missile_type, e_fighter_context_list[index], e_detector_context_list,
                                                                         enemy_status[enemy_index], self.e_strike_list)
                if valid:
                    self.e_fighter_reward[index] += reward.get_reward_strike_act_valid()
                else:
                    self.e_fighter_reward[index] += reward.get_reward_strike_act_invalid()

        # strike judge, update the status list, the strike list and the reward
        for item in reversed(self.o_strike_list):
            fighter_index = item['attacker_id'] - self.o_detector_num - 1
            fighter_radar_visible_list = self.o_fighter_status_list[fighter_index]['radar_visible_list']
            
            target_index = item['target_id'] - self.e_detector_num - 1 if item['target_id'] > self.e_detector_num \
                                                                       else item['target_id'] - 1
            strike_result = strike_calc.strike_judge(item, fighter_radar_visible_list, self.random_obj)
            if strike_result == 1:
                # hit success
                if item['target_id'] > self.e_detector_num:
                    # missile hit a fighter
                    self.o_fighter_reward[fighter_index] += reward.get_reward_strike_fighter_success()
                    self.e_fighter_status_list[target_index]['alive'] = False
                    self.e_fighter_reward[target_index] += reward.get_reward_fighter_destroyed()
                else:
                    # missile hit a detector
                    self.o_fighter_reward[fighter_index] += reward.get_reward_strike_detector_success()
                    self.e_detector_status_list[target_index]['alive'] = False
                    self.e_detector_reward[target_index] += reward.get_reward_detector_destroyed()
                self.o_strike_list.remove(item) 
            if strike_result == -1:
                self.o_strike_list.remove(item)
                # hit failed
                if item['target_id'] > self.e_detector_num:
                    self.o_fighter_reward[fighter_index] += reward.get_reward_strike_fighter_fail()
                else:
                    self.o_fighter_reward[fighter_index] += reward.get_reward_strike_detector_fail()     
        for item in reversed(self.e_strike_list):
            fighter_index = item['attacker_id'] - self.e_detector_num - 1
            fighter_radar_visible_list = self.e_fighter_status_list[fighter_index]['radar_visible_list']
            target_index = item['target_id'] - self.o_detector_num - 1 if item['target_id'] > self.o_detector_num \
                                                               else item['target_id'] - 1
            strike_result = strike_calc.strike_judge(item, fighter_radar_visible_list, self.random_obj)
            if strike_result == 1:
                # hit success
                if item['target_id'] > self.o_detector_num:
                    # missile hit a fighter
                    self.e_fighter_reward[fighter_index] += reward.get_reward_strike_fighter_success()
                    self.o_fighter_status_list[target_index]['alive'] = False
                    self.o_fighter_reward[target_index] += reward.get_reward_fighter_destroyed()
                else:
                    #missile hit a detector
                    self.e_fighter_reward[fighter_index] += reward.get_reward_strike_detector_success()
                    self.o_detector_status_list[target_index]['alive'] = False
                    self.o_detector_reward[target_index] += reward.get_reward_detector_destroyed()
                self.e_strike_list.remove(item)
            if strike_result == -1:
                self.e_strike_list.remove(item)
                # hit failed
                if item['target_id'] > self.o_detector_num:
                    self.e_fighter_reward[fighter_index] += reward.get_reward_strike_fighter_fail()
                else:
                    self.e_fighter_reward[fighter_index] += reward.get_reward_strike_detector_fail()
                
        # update position and jammer
        for index in range(self.e_detector_num):
            if self.e_detector_status_list[index]['alive']:
                prev_pos_x = self.e_detector_status_list[index]['pos_x']
                prev_pos_y = self.e_detector_status_list[index]['pos_y']
                course     = side2_detector_action[index]['course']
                speed      = self.e_detector_property_list[index]['speed']
                self.e_detector_status_list[index]['pos_x'], self.e_detector_status_list[index]['pos_y'] = \
                position_calc.pos_update(prev_pos_x, prev_pos_y, course, speed, self.battlefield_size_x, self.battlefield_size_y)
                self.e_detector_status_list[index]['course'] = course
                self.e_detector_status_list[index]['radar_enable'] = side2_detector_action[index]['r_iswork']
                self.e_detector_status_list[index]['radar_fp'] = side2_detector_action[index]['r_fre_point']
        for index in range(self.e_fighter_num):
            if self.e_fighter_status_list[index]['alive']:
                prev_pos_x = self.e_fighter_status_list[index]['pos_x']
                prev_pos_y = self.e_fighter_status_list[index]['pos_y']
                course     = side2_fighter_action[index]['course']
                speed      = self.e_fighter_property_list[index]['speed']
                self.e_fighter_status_list[index]['pos_x'], self.e_fighter_status_list[index]['pos_y'] = \
                position_calc.pos_update(prev_pos_x, prev_pos_y, course, speed, self.battlefield_size_x, self.battlefield_size_y)
                self.e_fighter_status_list[index]['course'] = course
                self.e_fighter_status_list[index]['radar_enable'] = side2_fighter_action[index]['r_iswork']
                self.e_fighter_status_list[index]['radar_fp'] = side2_fighter_action[index]['r_fre_point']
                self.e_fighter_status_list[index]['j_enable'] = side2_fighter_action[index]['j_iswork']
                self.e_fighter_status_list[index]['j_fp'] = side2_fighter_action[index]['j_fre_point']
                self.e_fighter_status_list[index]['radar_fp'] = side2_fighter_action[index]['r_fre_point']
                self.e_fighter_status_list[index]['radar_fp'] = side2_fighter_action[index]['r_fre_point']
                self.e_fighter_status_list[index]['radar_fp'] = side2_fighter_action[index]['r_fre_point']
                self.e_fighter_status_list[index]['radar_fp'] = side2_fighter_action[index]['r_fre_point']
        for index in range(self.o_detector_num):
            if self.o_detector_status_list[index]['alive']:
                prev_pos_x = self.o_detector_status_list[index]['pos_x']
                prev_pos_y = self.o_detector_status_list[index]['pos_y']
                course     = side1_detector_action[index]['course']
                speed      = self.o_detector_property_list[index]['speed']
                self.o_detector_status_list[index]['pos_x'], self.o_detector_status_list[index]['pos_y'] = \
                position_calc.pos_update(prev_pos_x, prev_pos_y, course, speed, self.battlefield_size_x, self.battlefield_size_y)
                self.o_detector_status_list[index]['course'] = course
                self.o_detector_status_list[index]['radar_enable'] = side1_detector_action[index]['r_iswork']
                self.o_detector_status_list[index]['radar_fp'] = side1_detector_action[index]['r_fre_point']
        for index in range(self.o_fighter_num):
            if self.o_fighter_status_list[index]['alive']:
                prev_pos_x = self.o_fighter_status_list[index]['pos_x']
                prev_pos_y = self.o_fighter_status_list[index]['pos_y']
                course     = side1_fighter_action[index]['course']
                speed      = self.o_fighter_property_list[index]['speed']
                self.o_fighter_status_list[index]['pos_x'], self.o_fighter_status_list[index]['pos_y'] = \
                position_calc.pos_update(prev_pos_x, prev_pos_y, course, speed, self.battlefield_size_x, self.battlefield_size_y)
                self.o_fighter_status_list[index]['course'] = side1_fighter_action[index]['course']
                self.o_fighter_status_list[index]['radar_enable'] = side1_fighter_action[index]['r_iswork']
                self.o_fighter_status_list[index]['radar_fp'] = side1_fighter_action[index]['r_fre_point']
                self.o_fighter_status_list[index]['j_enable'] = side1_fighter_action[index]['j_iswork']
                self.o_fighter_status_list[index]['j_fp'] = side1_fighter_action[index]['j_fre_point']
                self.o_fighter_status_list[index]['radar_fp'] = side1_fighter_action[index]['r_fre_point']
                self.o_fighter_status_list[index]['radar_fp'] = side1_fighter_action[index]['r_fre_point']
                self.o_fighter_status_list[index]['radar_fp'] = side1_fighter_action[index]['r_fre_point']
                self.o_fighter_status_list[index]['radar_fp'] = side1_fighter_action[index]['r_fre_point']

        # update radar visible list and reward list
        for index in range(self.e_detector_num):
            if self.e_detector_status_list[index]['alive']:
                new_detector_num, new_fighter_num = detection_calc.radar_visible_calc(e_detector_context_list[index],
                                                                                      o_detector_context_list,
                                                                                      o_fighter_context_list)
                self.e_detector_reward[index] += reward.get_reward_radar_detector_detector()*new_detector_num + \
                                                 reward.get_reward_radar_detector_fighter() *new_fighter_num
        for index in range(self.e_fighter_num):
            if self.e_fighter_status_list[index]['alive']:
                new_detector_num, new_fighter_num = detection_calc.radar_visible_calc(e_fighter_context_list[index],
                                                                                      o_detector_context_list,
                                                                                      o_fighter_context_list)
                self.e_fighter_reward[index] += reward.get_reward_radar_fighter_detector()*new_detector_num + \
                                                reward.get_reward_radar_fighter_fighter()*new_fighter_num
        for index in range(self.o_detector_num):
            if self.o_detector_status_list[index]['alive']:
                new_detector_num, new_fighter_num = detection_calc.radar_visible_calc(o_detector_context_list[index], 
                                                                                      e_detector_context_list,
                                                                                      e_fighter_context_list)
                self.o_detector_reward[index] += reward.get_reward_radar_detector_detector()*new_detector_num + \
                                                 reward.get_reward_radar_detector_fighter() *new_fighter_num
        for index in range(self.o_fighter_num):
            if self.o_fighter_status_list[index]['alive']:
                new_detector_num, new_fighter_num = detection_calc.radar_visible_calc(o_fighter_context_list[index],
                                                                                      e_detector_context_list,
                                                                                      e_fighter_context_list)
                self.o_fighter_reward[index] += reward.get_reward_radar_fighter_detector()*new_detector_num + \
                                                reward.get_reward_radar_fighter_fighter()*new_fighter_num

        # 判断是否仍旧存活，并更新奖励
        for index in range(self.o_detector_num):
            if self.o_detector_status_list[index]['alive']:
                self.o_detector_reward[index] += reward.get_reward_keep_alive_step()
        for index in range(self.o_fighter_num):
            if self.o_fighter_status_list[index]['alive']:
                self.o_fighter_reward[index] += reward.get_reward_keep_alive_step()
        for index in range(self.e_detector_num):
            if self.e_detector_status_list[index]['alive']:
                self.e_detector_reward[index] += reward.get_reward_keep_alive_step()
        for index in range(self.e_fighter_num):
            if self.e_fighter_status_list[index]['alive']:
                self.e_fighter_reward[index] += reward.get_reward_keep_alive_step()

        
        # 判断是否回合结束
        if self.render_flag:
            if not self.step_count % self.render_interval:
                self.show()
        side1_detector_alive_num, side1_fighter_alive_num, side1_l_missile_left, side1_s_missile_left, side2_detector_alive_num, side2_fighter_alive_num, side2_l_missile_left, side2_s_missile_left = \
        self.get_alive_status(self.o_detector_status_list, self.o_fighter_status_list, self.e_detector_status_list, self.e_fighter_status_list)
        # 完胜
        if side1_detector_alive_num == 0 and side1_fighter_alive_num == 0:
            self.done = True
            self.e_game_reward = reward.get_reward_totally_win()
            self.o_game_reward = reward.get_reward_totally_lose()
        if side2_detector_alive_num == 0 and side2_fighter_alive_num == 0:
            self.done = True
            self.o_game_reward = reward.get_reward_totally_win()
            self.e_game_reward = reward.get_reward_totally_lose()
        # 导弹余量为0，作战单元多者获胜
        if side1_l_missile_left == 0 and side1_s_missile_left == 0 and \
           side2_l_missile_left == 0 and side2_s_missile_left == 0:
            self.done = True
            if side1_fighter_alive_num > side2_fighter_alive_num:
                self.o_game_reward = reward.get_reward_win()
                self.e_game_reward = reward.get_reward_lose()
            elif side1_fighter_alive_num < side2_fighter_alive_num:
                self.e_game_reward = reward.get_reward_win()
                self.o_game_reward = reward.get_reward_lose()
            else:
                self.o_game_reward = reward.get_reward_draw()
                self.e_game_reward = reward.get_reward_draw()
        # 达到最大step,剩余作战单元数量多的获胜
        if self.step_count >= self.max_step:
            self.done = True
            if side1_fighter_alive_num > side2_fighter_alive_num:
                self.o_game_reward = reward.get_reward_win()
                self.e_game_reward = reward.get_reward_lose()
            elif side1_fighter_alive_num < side2_fighter_alive_num:
                self.e_game_reward = reward.get_reward_win()
                self.o_game_reward = reward.get_reward_lose()
            else:
                self.o_game_reward = reward.get_reward_draw()
                self.e_game_reward = reward.get_reward_draw()

        return True
