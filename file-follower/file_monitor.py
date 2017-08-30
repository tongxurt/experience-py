#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
Authors: tongxu01(tongxu01@baidu.com)
Date:    2017/8/20
"""

import os
import sys
import time
from subprocess import PIPE
from subprocess import Popen

"""
Python-Tail - Unix tail follow implementation in Python. 
python-tail can be used to monitor changes to a file.
"""


def check_file_validity(file_):
    """ Check whether the a given file exists, readable and is a file """
    if not os.access(file_, os.F_OK):
        raise MonitorError("File '%s' does not exist" % file_)
    if not os.access(file_, os.R_OK):
        raise MonitorError("File '%s' not readable" % file_)
    if os.path.isdir(file_):
        raise MonitorError("File '%s' is a directory" % file_)


class Monitor(object):
    """ Represents a tail command. """

    def __init__(self, tailed_file):
        """ Initiate a Tail instance.
            Check for file validity, assigns callback function to standard out.

            Arguments:
                tailed_file - File to be followed. """

        check_file_validity(tailed_file)
        self.tailed_file = tailed_file
        self.callback = sys.stdout.write

    def follow(self):
        """Do a tail follow
        If file was deleted and recreated , go on following
        """
        command = 'tail -F %s' % self.tailed_file
        popen = Popen(command, stdout=PIPE, stderr=PIPE, shell=True)
        while True:
            line = popen.stdout.readline()
            self.callback(line)

    def follow_single_file(self, s=1):
        """ Do a tail follow. If a callback function is registered it is called with every new line.
        Else printed to standard out.

        If file was deleted, stop following.

        Arguments:
            s - Number of seconds to wait between each iteration; Defaults to 1. """

        with open(self.tailed_file) as file_:
            # Go to the end of file
            file_.seek(0, 2)
            while True:
                curr_position = file_.tell()
                line = file_.readline()
                if not line:
                    file_.seek(curr_position)
                    time.sleep(s)
                else:
                    self.callback(line)

    def register_callback(self, func):
        """ Overrides default callback function to provided function. """
        self.callback = func


class MonitorError(Exception):
    def __init__(self, msg):
        self.message = msg

    def __str__(self):
        return self.message
