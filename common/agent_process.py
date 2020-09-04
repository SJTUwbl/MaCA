#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: Gao Fang
@contact: gaofang@cetc.com.cn
@software: PyCharm
@file: fight.py
@time: 2019/3/12 0009 16:41
@desc: agent sub proc
"""
import importlib
import time
from multiprocessing import Process, Queue

AGENT_INIT_TIMEOUT = 60
AGENT_RESP_TIMEOUT = 60


class AgentProc(Process):
    '''
    agent子进程
    '''
    def __init__(self, agent_name, size_x, size_y, detector_num, fighter_num, recv_queue, send_queue):
        super().__init__()
        self.agent_name = agent_name
        self.size_x = size_x
        self.size_y = size_y
        self.detector_num = detector_num
        self.fighter_num = fighter_num
        self.recv_queue = recv_queue
        self.send_queue = send_queue
        self.agent = None
        self.obs_construct = None
        self.obs_ind = 'raw'

    def run(self):
        agent_import_path = 'agent.' + self.agent_name + '.agent'
        agent_module = importlib.import_module(agent_import_path)
        self.agent = agent_module.Agent()
        self.agent.set_map_info(self.size_x, self.size_y, self.detector_num,self.fighter_num)
        self.obs_ind = self.agent.get_obs_ind()
        if self.obs_ind != 'raw':
            obs_path = 'obs_construct.' + self.obs_ind + '.construct'
            obs_module = importlib.import_module(obs_path)
            self.obs_construct = obs_module.ObsConstruct(self.size_x, self.size_y, self.detector_num,self.fighter_num)
        # time.sleep(5)
        self.send_queue.put('Init OK')
        self.__decision_proc()

    def __decision_proc(self):
        while True:
            obs_data = self.recv_queue.get()
            obs_raw_dict = obs_data['obs_raw_dict']
            step_cnt = obs_data['step_cnt']
            if self.obs_ind == 'raw':
                obs_dict = obs_raw_dict
            else:
                obs_dict = self.obs_construct.obs_construct(obs_raw_dict)
            detector_action, fighter_action = self.agent.get_action(obs_dict, step_cnt)
            action_dict = {'detector_action': detector_action, 'fighter_action': fighter_action}
            self.send_queue.put(action_dict)


class AgentCtrl:
    '''
    agent子进程维护
    '''
    def __init__(self, agent_name, size_x, size_y, detector_num, fighter_num):
        self.agent_name = agent_name
        self.size_x = size_x
        self.size_y = size_y
        self.detector_num = detector_num
        self.fighter_num = fighter_num
        self.send_q = None
        self.recv_q = None
        self.agent = None

    def agent_init(self):
        self.send_q = Queue(1)
        self.recv_q = Queue(1)
        self.agent = AgentProc(self.agent_name, self.size_x, self.size_y, self.detector_num, self.fighter_num,
                               self.send_q, self.recv_q)
        self.agent.start()
        try:
            agent_msg = self.recv_q.get(True, AGENT_INIT_TIMEOUT)
        except:
            self.terminate()
            return False
        else:
            return True

    def terminate(self):
        if self.agent:
            if self.agent.is_alive():
                self.agent.terminate()
        self.agent = None
        if self.send_q:
            self.send_q.close()
        self.send_q = None
        if self.recv_q:
            self.recv_q.close()
        self.recv_q = None

    def get_action(self, obs_raw_dict, step_cnt):
        '''
        获得动作
        :param obs_raw_dict: raw obs
        :param step_cnt: step计数，从1开始
        :return: action: 动作信息
        :return: result: 0, 正常; 1, 崩溃; 2, 超时
        '''
        action = []
        result = 0
        self.send_q.put({'obs_raw_dict': obs_raw_dict, 'step_cnt': step_cnt})
        try:
            action = self.recv_q.get(True, AGENT_RESP_TIMEOUT)
        except:
            if not self.agent.is_alive():
                # 子进程不存在，崩溃
                result = 1
            else:
                # 子进程存在，卡死
                result = 2
            self.__agent_restart()
        return action, result

    def __agent_restart(self):
        '''
        重启agent。由于重启代表之前成功启动过，所以此处认为重启也会成功。但若重启不成功将导致程序卡死。若后续出现此类问题应重点排查此处。
        :return:
        '''
        self.terminate()
        self.send_q = Queue(1)
        self.recv_q = Queue(1)
        self.agent = AgentProc(self.agent_name, self.size_x, self.size_y, self.detector_num, self.fighter_num,
                               self.send_q, self.recv_q)
        self.agent.start()
        self.recv_q.get()
