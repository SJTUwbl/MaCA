#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: Gao Fang
@contact: gaofang@cetc.com.cn
@software: PyCharm
@file: dqn.py
@time: 2018/7/25 0025 13:38
@desc: 
"""
import torch
import torch.nn as nn
import numpy as np


class NetFighter(nn.Module):
    def __init__(self, n_actions):
        super(NetFighter, self).__init__()
        self.conv1 = nn.Sequential(     # 100 * 100 * 3
            nn.Conv2d(
                in_channels=5,
                out_channels=16,
                kernel_size=5,
                stride=1,
                padding=2,
            ),
            nn.ReLU(),
            nn.MaxPool2d(2),
        )
        self.conv2 = nn.Sequential(     # 50 * 50 * 16
            nn.Conv2d(16, 32, 5, 1, 2),
            nn.ReLU(),
            nn.MaxPool2d(2),            # 25 * 25 * 32
        )
        self.info_fc = nn.Sequential(
            nn.Linear(3, 256),
            nn.Tanh(),
        )
        self.feature_fc = nn.Sequential(    # 25 * 25 * 32 + 256
            nn.Linear((25 * 25 * 32 + 256), 512),
            nn.ReLU(),
        )
        self.decision_fc = nn.Linear(512, n_actions)

    def forward(self, img, info):
        img_feature = self.conv1(img)
        img_feature = self.conv2(img_feature)
        info_feature = self.info_fc(info)
        combined = torch.cat((img_feature.view(img_feature.size(0), -1), info_feature.view(info_feature.size(0), -1)),
                             dim=1)
        feature = self.feature_fc(combined)
        action = self.decision_fc(feature)
        return action

# Deep Q Network off-policy
class RLFighter:
    def __init__(
            self,
            n_actions,
            learning_rate=0.01,
            reward_decay=0.9,
            e_greedy=0.9,
            replace_target_iter=100,
            memory_size=500,
            batch_size=32,
            e_greedy_increment=None,
            output_graph=False,
    ):
        self.n_actions = n_actions
        self.lr = learning_rate
        self.gamma = reward_decay
        self.epsilon_max = e_greedy
        self.replace_target_iter = replace_target_iter
        self.memory_size = memory_size
        self.batch_size = batch_size
        self.epsilon_increment = e_greedy_increment
        self.epsilon = 0 if e_greedy_increment is not None else self.epsilon_max
        self.s_screen_memory = []
        self.s_info_memory = []
        self.a_memory = []
        self.r_memory = []
        self.s__screen_memory = []
        self.s__info_memory = []
        self.memory_counter = 0

        self.gpu_enable = torch.cuda.is_available()

        # total learning step
        self.learn_step_counter = 0

        self.cost_his = []
        self.eval_net, self.target_net = NetFighter(self.n_actions), NetFighter(self.n_actions)
        if self.gpu_enable:
            print('GPU Available!!')
            self.eval_net = self.eval_net.cuda()
            self.target_net = self.target_net.cuda()
        self.loss_func = nn.MSELoss()
        # self.optimizer = torch.optim.Adam(self.eval_net.parameters(), lr=self.lr)
        self.optimizer = torch.optim.RMSprop(self.eval_net.parameters(), lr=self.lr)


    def store_transition(self, s, a, r, s_):
        self.s_screen_memory.append(s['screen'])
        self.s_info_memory.append(s['info'])
        self.a_memory.append(a)
        self.r_memory.append(r)
        self.s__screen_memory.append(s_['screen'])
        self.s__info_memory.append(s_['info'])
        self.memory_counter += 1

    def __clear_memory(self):
        self.s_screen_memory.clear()
        self.s_info_memory.clear()
        self.a_memory.clear()
        self.r_memory.clear()
        self.s__screen_memory.clear()
        self.s__info_memory.clear()
        self.memory_counter = 0

    def choose_action(self, img_obs, info_obs):
        img_obs = torch.unsqueeze(torch.FloatTensor(img_obs), 0)
        info_obs = torch.unsqueeze(torch.FloatTensor(info_obs), 0)
        if self.gpu_enable:
            img_obs = img_obs.cuda()
            info_obs = info_obs.cuda()
        if np.random.uniform() < self.epsilon:
            actions_value = self.eval_net(img_obs, info_obs)
            action = torch.max(actions_value, 1)[1]
            if self.gpu_enable:
                action = action.cpu()
            action = action.numpy()
        else:
            action = np.zeros(1, dtype=np.int32)
            action[0] = np.random.randint(0, self.n_actions)
        return action

    def learn(self):
        # check to replace target parameters
        if self.learn_step_counter % self.replace_target_iter == 0:
            self.target_net.load_state_dict(self.eval_net.state_dict())
            print('\ntarget_params_replaced\n')
            step_counter_str = '%09d' % self.learn_step_counter
            torch.save(self.target_net.state_dict(), 'model/simple/model_' + step_counter_str + '.pkl')
        # pre possess mem
        s_screen_mem = torch.FloatTensor(np.array(self.s_screen_memory))
        s_info_mem = torch.FloatTensor(np.array(self.s_info_memory))
        a_mem = torch.LongTensor(np.array(self.a_memory))
        r_mem = torch.FloatTensor(np.array(self.r_memory))
        r_mem = r_mem.view(self.memory_counter, 1)
        s__screen_mem = torch.FloatTensor(np.array(self.s__screen_memory))
        s__info_mem = torch.FloatTensor(np.array(self.s__info_memory))
        if self.gpu_enable:
            s_screen_mem = s_screen_mem.cuda()
            s_info_mem = s_info_mem.cuda()
            a_mem = a_mem.cuda()
            r_mem = r_mem.cuda()
            s__screen_mem = s__screen_mem.cuda()
            s__info_mem = s__info_mem.cuda()

        # sample batch memory from all memory

        # q_eval w.r.t the action in experience
        q_eval = self.eval_net(s_screen_mem, s_info_mem).gather(1, a_mem)  # shape (batch, 1)
        q_next = self.target_net(s__screen_mem, s__info_mem).detach()  # detach from graph, don't backpropagate
        q_target = r_mem + self.gamma * q_next.max(1)[0].view(self.memory_counter, 1)  # shape (batch, 1)
        loss = self.loss_func(q_eval, q_target)

        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

        self.cost_his.append(loss)

        # increasing epsilon
        self.epsilon = self.epsilon + self.epsilon_increment if self.epsilon < self.epsilon_max else self.epsilon_max
        self.learn_step_counter += 1
        self.__clear_memory()


class NetDetector(nn.Module):
    def __init__(self, n_actions):
        super(NetDetector, self).__init__()
        self.conv1 = nn.Sequential(     # 100 * 100 * 3
            nn.Conv2d(
                in_channels=3,
                out_channels=16,
                kernel_size=5,
                stride=1,
                padding=2,
            ),
            nn.ReLU(),
            nn.MaxPool2d(2),
        )
        self.conv2 = nn.Sequential(     # 50 * 50 * 16
            nn.Conv2d(16, 32, 5, 1, 2),
            nn.ReLU(),
            nn.MaxPool2d(2),            # 25 * 25 * 32
        )
        self.info_fc = nn.Sequential(
            nn.Linear(3, 256),
            nn.Tanh(),
        )
        self.feature_fc = nn.Sequential(    # 25 * 25 * 32 + 256
            nn.Linear((25 * 25 * 32 + 256), 512),
            nn.ReLU(),
        )
        self.decision_fc = nn.Linear(512, n_actions)

    def forward(self, img, info):
        img_feature = self.conv1(img)
        img_feature = self.conv2(img_feature)
        info_feature = self.info_fc(info)
        combined = torch.cat((img_feature.view(img_feature.size(0), -1), info_feature.view(info_feature.size(0), -1)),
                             dim=1)
        feature = self.feature_fc(combined)
        action = self.decision_fc(feature)
        return action

