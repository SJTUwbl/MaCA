#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: Gao Fang
@contact: gaofang@cetc.com.cn
@software: PyCharm
@file: tournament.py
@time: 2019/2/26 0026 9:13
@desc: 
"""

import importlib
import os
import time
import json
import numpy as np
import pandas as pd
from interface import Environment
from common.agent_process import AgentCtrl

SCORE_WIN = 3
SCORE_DRAW = 1
SCORE_LOSS = 0


def run(agent1_name, agent2_name, map_name, round_num, max_step, random_pos=False):
    '''

    :param agent1_name: 红方名称
    :param agent2_name: 蓝方名称
    :param map_name: 地图名称
    :param round_num: 对战局数
    :param max_step: 单局最大step
    :param random_pos: 随机起始位置
    :return: agent1_win_times, agent2_win_times, draw_times, agent1_crash_times, agent2_crash_times, agent1_timeout_times, agent2_timeout_times, agent1_launch_failure_times, agent2_launch_failure_times
    '''
    side1_win_times = 0
    side2_win_times = 0
    draw_times = 0
    log_flag = agent1_name + '_vs_' + agent2_name
    agent1_launch_failed = False
    agent2_launch_failed = False
    round_cnt = 0
    agent1_crash_list = []
    agent2_crash_list = []
    agent1_timeout_list = []
    agent2_timeout_list = []

    # file path constructing
    map_path = 'maps/' + map_name + '.map'
    agent1_path = 'agent/' + agent1_name + '/agent.py'
    agent2_path = 'agent/' + agent2_name + '/agent.py'

    if not os.path.exists(map_path):
        print('Error: map file not exist!')
        exit(-1)
    if not os.path.exists(agent1_path):
        print('Error: agent1 file not exist!')
        exit(-1)
    if not os.path.exists(agent2_path):
        print('Error: agent2 file not exist!')
        exit(-1)
    # make env
    env = Environment(map_path, 'raw', 'raw', max_step=max_step, render=True, random_pos=random_pos, log=log_flag)
    # get map info
    size_x, size_y = env.get_map_size()
    side1_detector_num, side1_fighter_num, side2_detector_num, side2_fighter_num = env.get_unit_num()
    # create agent
    agent1 = AgentCtrl(agent1_name, size_x, size_y, side1_detector_num, side1_fighter_num)
    agent2 = AgentCtrl(agent2_name, size_x, size_y, side2_detector_num, side2_fighter_num)
    if not agent1.agent_init():
        print('ERROR: Agent1 ' + agent1_name + ' init failed!')
        agent1.terminate()
        agent2.terminate()
        agent1_launch_failed = True
    if not agent2.agent_init():
        print('ERROR: Agent2 ' + agent2_name + ' init failed!')
        agent1.terminate()
        agent2.terminate()
        agent2_launch_failed = True
    # 若此处一方启动失败，则认为该方全败，启动失败计round_num次，若双方启动失败，则认为双方平局round_num次，其他与前述相同。
    if agent1_launch_failed and agent2_launch_failed:
        return 0, 0, round_num, 0, 0, 0, 0, round_num, round_num
    elif agent1_launch_failed:
        return 0, round_num, 0, 0, 0, 0, 0, round_num, 0
    elif agent2_launch_failed:
        return round_num, 0, 0, 0, 0, 0, 0, 0, round_num
    # execution
    # input("Press the <ENTER> key to continue...")
    for x in range(round_num):
        if x != 0:
            env.reset()
        step_cnt = 0
        round_cnt += 1
        while True:
            step_cnt += 1
            # get obs
            side1_obs_dict, side2_obs_dict = env.get_obs()
            # get action
            agent1_action, agent1_result = agent1.get_action(side1_obs_dict, step_cnt)
            if agent1_result == 0:
                side1_detector_action = agent1_action['detector_action']
                side1_fighter_action = agent1_action['fighter_action']
            elif agent1_result == 1:
                agent1_crash_list.append(round_cnt)
            elif agent1_result == 2:
                agent1_timeout_list.append(round_cnt)
            agent2_action, agent2_result = agent2.get_action(side2_obs_dict, step_cnt)
            if agent2_result == 0:
                side2_detector_action = agent2_action['detector_action']
                side2_fighter_action = agent2_action['fighter_action']
            elif agent2_result == 1:
                agent2_crash_list.append(round_cnt)
            elif agent2_result == 2:
                agent2_timeout_list.append(round_cnt)
            # execution
            if agent1_result == 0 and agent2_result == 0:
                env.step(side1_detector_action, side1_fighter_action, side2_detector_action, side2_fighter_action)
            elif agent1_result != 0 and agent2_result != 0:
                env.set_surrender(2)
            elif agent1_result != 0:
                env.set_surrender(0)
            else:
                env.set_surrender(1)
            # get done
            if env.get_done():
                # reward
                o_detector_reward, o_fighter_reward, o_game_reward, e_detector_reward, e_fighter_reward, e_game_reward = env.get_reward()
                if o_game_reward > e_game_reward:
                    side1_win_times += 1
                elif o_game_reward < e_game_reward:
                    side2_win_times += 1
                else:
                    draw_times += 1
                break
    agent1.terminate()
    agent2.terminate()
    return side1_win_times, side2_win_times, draw_times, len(agent1_crash_list), len(agent2_crash_list), len(agent1_timeout_list), len(agent2_timeout_list),0, 0


if __name__ == "__main__":
    map_name = ''
    round_num = 0
    max_step = 0
    agent_list = []
    summary_table = []
    # load config
    with open('tournament/config.ini', 'r') as f:
        config_dict = json.load(f)
        map_name = config_dict['map_name']
        round_num = config_dict['round_num']
        max_step = config_dict['max_step']
        agent_list = config_dict['agent_list']

    print('map_name: %s' % map_name)
    print('round_num: %d' % round_num)
    print('max_step: %d' % max_step)
    print('agent_list: ')
    print(agent_list)

    if round_num % 2 != 0:
        print('Error: round_num must be even number')
        exit(-1)

    win_rounds_per_agent = [0] * len(agent_list)
    draw_rounds_per_agent = [0] * len(agent_list)
    total_rounds_per_agent = [0] * len(agent_list)
    crash_rounds_per_agent = [0] * len(agent_list)
    timeout_rounds_per_agent = [0] * len(agent_list)
    launch_failed_rounds_per_agent = [0] * len(agent_list)
    win_rounds_against_each_other = np.zeros((len(agent_list), len(agent_list)), dtype='int32')
    draw_rounds_against_each_other = np.zeros((len(agent_list), len(agent_list)), dtype='int32')
    crash_rounds_against_each_other = np.zeros((len(agent_list), len(agent_list)), dtype='int32')
    timeout_rounds_against_each_other = np.zeros((len(agent_list), len(agent_list)), dtype='int32')
    launch_failed_rounds_against_each_other = np.zeros((len(agent_list), len(agent_list)), dtype='int32')

    for x in range(len(agent_list)):
        for y in range(len(agent_list)):
            if y == x:
                continue
            agent1 = agent_list[x]
            agent2 = agent_list[y]
            print(agent1 + ' vs ' + agent2)
            agent1_win_rounds, agent2_win_rounds, draw_rounds, agent1_crash_rounds, agent2_crash_rounds, agent1_timeout_rounds, agent2_timeout_rounds, agent1_launch_failure_rounds, agent2_launch_failure_rounds = run(agent1, agent2, map_name, int(round_num / 2), max_step)
            # record
            total_rounds = agent1_win_rounds + agent2_win_rounds + draw_rounds
            win_rounds_per_agent[x] += agent1_win_rounds
            win_rounds_per_agent[y] += agent2_win_rounds
            draw_rounds_per_agent[x] += draw_rounds
            draw_rounds_per_agent[y] += draw_rounds
            total_rounds_per_agent[x] += total_rounds
            total_rounds_per_agent[y] += total_rounds
            crash_rounds_per_agent[x] += agent1_crash_rounds
            crash_rounds_per_agent[y] += agent2_crash_rounds
            timeout_rounds_per_agent[x] += agent1_timeout_rounds
            timeout_rounds_per_agent[y] += agent1_timeout_rounds
            launch_failed_rounds_per_agent[x] += agent1_launch_failure_rounds
            launch_failed_rounds_per_agent[y] += agent2_launch_failure_rounds
            win_rounds_against_each_other[x][y] += agent1_win_rounds
            win_rounds_against_each_other[y][x] += agent2_win_rounds
            draw_rounds_against_each_other[x][y] += draw_rounds
            draw_rounds_against_each_other[y][x] += draw_rounds
            crash_rounds_against_each_other[x][y] += agent1_crash_rounds
            crash_rounds_against_each_other[y][x] += agent2_crash_rounds
            timeout_rounds_against_each_other[x][y] += agent1_timeout_rounds
            timeout_rounds_against_each_other[y][x] += agent2_timeout_rounds
            launch_failed_rounds_against_each_other[x][y] += agent1_launch_failure_rounds
            launch_failed_rounds_against_each_other[y][x] += agent2_launch_failure_rounds

            # write file
            # win detail
            win_detail_table = pd.DataFrame(win_rounds_against_each_other)
            win_detail_table.columns = agent_list
            win_detail_table.index = agent_list
            win_detail_table.to_html('tournament/result/win_detail.html')
            # draw detail
            draw_detail_table = pd.DataFrame(draw_rounds_against_each_other)
            draw_detail_table.columns = agent_list
            draw_detail_table.index = agent_list
            draw_detail_table.to_html('tournament/result/draw_detail.html')
            # crash detail
            crash_detail_table = pd.DataFrame(crash_rounds_against_each_other)
            crash_detail_table.columns = agent_list
            crash_detail_table.index = agent_list
            crash_detail_table.to_html('tournament/result/crash_detail.html')
            # timeout detail
            timeout_detail_table = pd.DataFrame(timeout_rounds_against_each_other)
            timeout_detail_table.columns = agent_list
            timeout_detail_table.index = agent_list
            timeout_detail_table.to_html('tournament/result/timeout_detail.html')
            # launch failure detail
            launch_failure_detail_table = pd.DataFrame(launch_failed_rounds_against_each_other)
            launch_failure_detail_table.columns = agent_list
            launch_failure_detail_table.index = agent_list
            launch_failure_detail_table.to_html('tournament/result/launch_failure_detail.html')
            # summary
            summary_table = pd.DataFrame(columns=['agent', 'score', 'win_rate', 'total_rounds', 'win_rounds', 'draw_rounds', 'loss_rounds', 'crash_rounds', 'timeout_rounds', 'launch_failure_rounds'])
            for z in range(len(agent_list)):
                if total_rounds_per_agent[z] == 0:
                    win_rate = 0
                else:
                    win_rate = win_rounds_per_agent[z] / total_rounds_per_agent[z]
                score = SCORE_WIN * win_rounds_per_agent[z] + SCORE_DRAW * draw_rounds_per_agent[z] + SCORE_LOSS * (total_rounds_per_agent[z] - win_rounds_per_agent[z] - draw_rounds_per_agent[z])
                summary_table = summary_table.append(pd.DataFrame({'agent': [agent_list[z]],
                                                                   'score': [score],
                                                                   'win_rate': [win_rate],
                                                                   'total_rounds': [total_rounds_per_agent[z]],
                                                                   'win_rounds': [win_rounds_per_agent[z]],
                                                                   'draw_rounds': [draw_rounds_per_agent[z]],
                                                                   'loss_rounds': [total_rounds_per_agent[z] - win_rounds_per_agent[z] - draw_rounds_per_agent[z]],
                                                                   'crash_rounds': [crash_rounds_per_agent[z]],
                                                                   'timeout_rounds': [timeout_rounds_per_agent[z]],
                                                                   'launch_failure_rounds': [launch_failed_rounds_per_agent[z]]}))
            summary_table = summary_table.sort_values(by='score', ascending=False)
            summary_table.to_html('tournament/result/summary.html', index=False)
    print('tournament completed!, result:')
    print(summary_table)