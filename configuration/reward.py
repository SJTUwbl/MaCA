#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: Gao Fang
@contact: gaofang@cetc.com.cn
@software: PyCharm
@file: reward.py
@time: 2018/4/19 0019 14:39
@desc: reward config
"""


class GlobalVar:
    # reward
    # detector radar see a detector
    reward_radar_detector_detector = 20
    # detector radar see a fighter
    reward_radar_detector_fighter = 10
    # fighter radar see a detector
    reward_radar_fighter_detector = 20
    # fighter radar see a fighter
    reward_radar_fighter_fighter = 10

    # Missile hit a detector
    reward_strike_detector_success = 100
    # Missile miss a detector
    reward_strike_detector_fail = 0
    # Missile hit a fighter
    reward_strike_fighter_success = 100
    # Missile miss a fighter
    reward_strike_fighter_fail = 0

    # A detector been destroyed
    reward_detector_destroyed = -100
    # A fighter been destroyed
    reward_fighter_destroyed = -100

    # A valid attack action
    reward_strike_act_valid = 10
    # An invalid attack action
    reward_strike_act_invalid = -10

    # Keep alive in a step
    reward_keep_alive_step = 0

    # Round reward：totally win
    reward_totally_win = 200
    # Round reward：totally lose
    reward_totally_lose = -200
    # Round reward：win
    reward_win = 100
    # Round reward：lose
    reward_lose = -100
    # Round reward：draw
    reward_draw = 0


def get_reward_radar_detector_detector():
    return GlobalVar.reward_radar_detector_detector


def get_reward_radar_detector_fighter():
    return GlobalVar.reward_radar_detector_fighter


def get_reward_radar_fighter_detector():
    return GlobalVar.reward_radar_fighter_detector


def get_reward_radar_fighter_fighter():
    return GlobalVar.reward_radar_fighter_fighter


def get_reward_strike_detector_success():
    return GlobalVar.reward_strike_detector_success


def get_reward_strike_detector_fail():
    return GlobalVar.reward_strike_detector_fail


def get_reward_strike_fighter_success():
    return GlobalVar.reward_strike_fighter_success


def get_reward_strike_fighter_fail():
    return GlobalVar.reward_strike_fighter_fail


def get_reward_detector_destroyed():
    return GlobalVar.reward_detector_destroyed


def get_reward_fighter_destroyed():
    return GlobalVar.reward_fighter_destroyed


def get_reward_strike_act_valid():
    return GlobalVar.reward_strike_act_valid


def get_reward_strike_act_invalid():
    return GlobalVar.reward_strike_act_invalid


def get_reward_keep_alive_step():
    return GlobalVar.reward_keep_alive_step


def get_reward_win():
    return GlobalVar.reward_win


def get_reward_lose():
    return GlobalVar.reward_lose


def get_reward_totally_win():
    return GlobalVar.reward_totally_win


def get_reward_totally_lose():
    return GlobalVar.reward_totally_lose


def get_reward_draw():
    return GlobalVar.reward_draw
