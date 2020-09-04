#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: Gao Fang
@contact: gaofang@cetc.com.cn
@software: PyCharm
@file: fight.py
@time: 2018/3/9 0009 16:41
@desc: execution battle between two agents
"""
import argparse
import os
import time
from interface import Environment
from common.agent_process import AgentCtrl


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--map", type=str, default="1000_1000_2_10_vs_2_10", help='map name, only name, not file path')
    parser.add_argument("--agent1", type=str, default="fix_rule", help='agent 1 name, only name, not path')
    parser.add_argument("--agent2", type=str, default="fix_rule", help='agent 2 name, only name, not path')
    parser.add_argument("--round", type=int, default=1, help='play rounds')
    parser.add_argument("--fps", type=float, default=0, help='display fps')
    parser.add_argument("--max_step", type=int, default=5000, help='max step in a round')
    parser.add_argument("--random_pos", action="store_true", help='if the initial positions are random or fix')
    parser.add_argument("--log", action="store_true", help='saving log')
    parser.add_argument("--log_path", type=str, default="default_log", help='log folder name')
    args = parser.parse_args()

    print('Map:', args.map)
    print('Side1 agent:', args.agent1)
    print('Side2 agent:', args.agent2)
    print('Round number:', args.round)

    side1_win_times = 0
    side2_win_times = 0
    draw_times = 0

    # file path constructing
    map_path = 'maps/' + args.map + '.map'
    agent1_path = 'agent/' + args.agent1 + '/agent.py'
    agent2_path = 'agent/' + args.agent2 + '/agent.py'

    if not os.path.exists(map_path):
        print('Error: map file not exist!')
        exit(-1)
    if not os.path.exists(agent1_path):
        print('Error: agent1 file not exist!')
        exit(-1)
    if not os.path.exists(agent2_path):
        print('Error: agent2 file not exist!')
        exit(-1)
    # delay calc
    if args.fps == 0:
        step_delay = 0
    else:
        step_delay = 1 / args.fps

    # environment initiation
    if args.log:
        if args.log_path == 'default_log':
            log_flag = args.agent1 + '_vs_' + args.agent2
        else:
            log_flag = args.log_path
    else:
        log_flag = False
    env = Environment(map_path, 'raw', 'raw', max_step=args.max_step, render=True,
                      random_pos=args.random_pos, log=log_flag)
    # get map info
    size_x, size_y = env.get_map_size()
    side1_detector_num, side1_fighter_num, side2_detector_num, side2_fighter_num = env.get_unit_num()

    # create agent
    agent1 = AgentCtrl(args.agent1, size_x, size_y, side1_detector_num, side1_fighter_num)
    agent2 = AgentCtrl(args.agent2, size_x, size_y, side2_detector_num, side2_fighter_num)
    if not agent1.agent_init():
        print('ERROR: Agent1 init failed!')
        agent1.terminate()
        agent2.terminate()
        exit(-1)
    else:
        print('Agent1 init success!')
    if not agent2.agent_init():
        print('ERROR: Agent2 init failed!')
        agent1.terminate()
        agent2.terminate()
        exit(-1)
    else:
        print('Agent2 init success!')

    # execution
    step_cnt = 0
    round_cnt = 0
    agent1_crash_list = []
    agent2_crash_list = []
    agent1_timeout_list = []
    agent2_timeout_list = []
    # input("Press the <ENTER> key to continue...")
    for x in range(args.round):
        side1_total_reward = 0
        side2_total_reward = 0
        if x != 0:
            env.reset()
        step_cnt = 0
        round_cnt += 1
        while True:
            time.sleep(step_delay)
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
                print('agent1 crashed!')
            elif agent1_result == 2:
                agent1_timeout_list.append(round_cnt)
                print('agent1 timeout!')
            agent2_action, agent2_result = agent2.get_action(side2_obs_dict, step_cnt)
            if agent2_result == 0:
                side2_detector_action = agent2_action['detector_action']
                side2_fighter_action = agent2_action['fighter_action']
            elif agent2_result == 1:
                agent2_crash_list.append(round_cnt)
                print('agent2 crashed!')
            elif agent2_result == 2:
                agent2_timeout_list.append(round_cnt)
                print('agent2 timeout!')

            # execution
            if agent1_result == 0 and agent2_result == 0:
                env.step(side1_detector_action, side1_fighter_action, side2_detector_action, side2_fighter_action)
            elif agent1_result != 0 and agent2_result != 0:
                env.set_surrender(2)
            elif agent1_result != 0:
                env.set_surrender(0)
            else:
                env.set_surrender(1)
            # obs
            side1_obs_raw, side2_obs_raw = env.get_obs_raw()
            side1_detector_obs_raw_list = side1_obs_raw['detector_obs_list']
            side1_fighter_obs_raw_list = side1_obs_raw['fighter_obs_list']
            side1_joint_obs_raw_dict = side1_obs_raw['joint_obs_dict']
            side2_detector_obs_raw_list = side2_obs_raw['detector_obs_list']
            side2_fighter_obs_raw_list = side2_obs_raw['fighter_obs_list']
            side2_joint_obs_raw_dict = side2_obs_raw['joint_obs_dict']
            # reward
            o_detector_reward, o_fighter_reward, o_game_reward, e_detector_reward, e_fighter_reward, e_game_reward = env.get_reward()

            side1_step_reward = 0
            side2_step_reward = 0
            for y in range(side1_detector_num):
                side1_step_reward += o_detector_reward[y]
            for y in range(side1_fighter_num):
                side1_step_reward += o_fighter_reward[y]
            for y in range(side2_detector_num):
                side2_step_reward += e_detector_reward[y]
            for y in range(side2_fighter_num):
                side2_step_reward += e_fighter_reward[y]
            side1_total_reward += side1_step_reward
            side2_total_reward += side2_step_reward
            # print('Round %d, Step %d:' % (round_cnt, step_cnt))
            # print('Side 1 reward: %d, Side 2 reward: %d' % (side1_step_reward, side2_step_reward))
            if env.get_done():
                print('Round %d done at step %d!' % (round_cnt, step_cnt))
                if o_game_reward > e_game_reward:
                    print('Side 1 WIN!!!')
                    side1_win_times += 1
                elif o_game_reward < e_game_reward:
                    print('Side 2 WIN!!!')
                    side2_win_times += 1
                else:
                    print('DRAW!!!')
                    draw_times += 1
                print('Side 1 total step reward: %d, Side 2 total step reward: %d' % (side1_total_reward, side2_total_reward))
                print('Side 1 round reward: %d, Side 2 round reward: %d' % (o_game_reward, e_game_reward))
                side1_detector_alive_num = 0
                side1_fighter_alive_num = 0
                side2_detector_alive_num = 0
                side2_fighter_alive_num = 0
                for y in range(side1_detector_num):
                    if side1_detector_obs_raw_list[y]['alive']:
                        side1_detector_alive_num += 1
                for y in range(side1_fighter_num):
                    if side1_fighter_obs_raw_list[y]['alive']:
                        side1_fighter_alive_num += 1
                for y in range(side2_detector_num):
                    if side2_detector_obs_raw_list[y]['alive']:
                        side2_detector_alive_num += 1
                for y in range(side2_fighter_num):
                    if side2_fighter_obs_raw_list[y]['alive']:
                        side2_fighter_alive_num += 1
                print('Side 1 alive detector: %d, Side 1 alive fighter: %d, Side 2 alive detector: %d, Side 2 alive fighter: %d' % (side1_detector_alive_num, side1_fighter_alive_num, side2_detector_alive_num, side2_fighter_alive_num))
                time.sleep(2)
                break
    agent1.terminate()
    agent2.terminate()
    print('FIGHT RESULT:')
    print('Total rounds: %d. Side1 win: %d. Side2 win: %d. Draw: %d' % (round_cnt, side1_win_times, side2_win_times, draw_times))
    print('Side 1 win rate: %.1f%%, Side 2 win rate: %.1f%%.' % (side1_win_times/round_cnt*100, side2_win_times/round_cnt*100))
    if len(agent1_crash_list) != 0:
        print('Side 1 crashed %d times:' % len(agent1_crash_list))
        print(agent1_crash_list)
    if len(agent2_crash_list) != 0:
        print('Side 2 crashed %d times:' % len(agent2_crash_list))
        print(agent2_crash_list)
    if len(agent1_timeout_list) != 0:
        print('Side 1 timeout %d times:' % len(agent1_timeout_list))
        print(agent1_timeout_list)
    if len(agent2_timeout_list) != 0:
        print('Side 2 timeout %d times:' % len(agent2_timeout_list))
        print(agent2_timeout_list)
    input("Press the <ENTER> key to continue...")
