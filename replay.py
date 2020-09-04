#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: Gao Fang
@contact: gaofang@cetc.com.cn
@software: PyCharm
@file: replay_test.py
@time: 2018/3/8 0008 17:24
@desc: load a log and replay
"""

from interface import PlayBack
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("log", type=str, help='log name')
    args = parser.parse_args()

    replay_obj = PlayBack(args.log)
    replay_obj.start()
    input("Press the <ENTER> key to continue...")
