#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
Authors: tongxu01(tongxu01@baidu.com)
Date:    2017/8/30
"""
import sys

from file_monitor import Monitor


def parse_log(line):
    print line


def main(file_to_monitor):
    """
    监控日志文件
    :param file_to_monitor:
    :return:
    """
    monitor = Monitor(file_to_monitor)
    monitor.register_callback(parse_log)
    monitor.follow()


if __name__ == '__main__':
    main(sys.argv[1])
