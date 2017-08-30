#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
参数:
1. 要发送到目标机器的文件,如果没有则
Authors: tongxu01(tongxu01@baidu.com)
Date:    2017/8/14
"""
import argparse
import os

import logging
import paramiko
import sys

# logging.basicConfig(level=logging.DEBUG, format='[%(levelname)s] [%(funcName)s] %(message)s')
import time

hosts = {
    "host": ["username", "passwd"],
}

config = {
    "default_workspace": "competent",
    "success": "[\033[1;32;49mSUCCESS\033[0m]",
    "notice": "[\033[1;35;49mNOTICE\033[0m]",
    "warning": "[\033[1;33;49mWARNING\033[0m]",
    "error": "[\033[1;31;49mERROR\033[0m]",
}

hdr = logging.StreamHandler()
hdr.setFormatter(logging.Formatter('%(message)s'))
logger = logging.getLogger('')
logger.setLevel(logging.INFO)
logger.addHandler(hdr)

parser = argparse.ArgumentParser(description='This helps you execute shell command or script on '
                                             'given hosts instead your fussy manual operation')
parser.add_argument('--file', '-f',
                    action='store',
                    default=None,
                    help='provide your file to send to given hosts.'
                         'if no file to send, ignore')
parser.add_argument('--remote_dir', '-d',
                    action='store',
                    help='provide where your file to send on given hosts. '
                         'default remote dir is : ' + config["default_workspace"])
parser.add_argument('--command', '-c',
                    help='provide your command to execute on given hosts.'
                         'if no command to execute, ignore')
parser.add_argument('-o', '--output',
                    help='output to file')
parser.add_argument('--noblock',
                    action="store_true",
                    help="wait until remote command result has been returned")


def parse_args():
    args = parser.parse_args()

    local_dir = None
    file_name = None

    local_file = args.file
    if local_file:
        if os.path.isfile(local_file):
            dir_items = os.path.split(local_file)
            local_dir, file_name = dir_items[0] if dir_items[0] else '.', dir_items[1]

        else:
            logger.info(config["error"] + ' invalid file:\033[1;31;49m %s \033[0m, please check '
                                          'your given path or if the file exists ' % local_file)
            sys.exit()

    remote_dir = args.remote_dir if args.remote_dir else '~/competent'
    command = args.command
    output = args.output

    if not local_file and not command:
        # todo
        logger.info(config["warning"] + ' Are you kidding? nothing to do?')
        sys.exit()
    noblock = args.noblock
    logger.info(config["success"] + ' prepare args')

    if not command and output:
        logger.info(config["warning"] + ' Are you kidding? where are your command?')
        sys.exit()

    return {
        "local_dir": local_dir,
        "remote_dir": remote_dir,
        "file_name": file_name,
        "command": command,
        "output": output,
        "noblock": noblock
    }


def prepare_remote_dir(sftp, remote_dir):
    try:
        sftp.listdir(remote_dir)
    except IOError:
        logger.info(config["warning"] + ' no such dir you provided, make one for you')
        sftp.mkdir(remote_dir)


def list_remote_dir(sftp, remote_dir):
    files = sftp.listdir(remote_dir)
    if not files:
        logger.info(config["notice"] + ' nothing in your target remote dir')
    else:
        logger.info(config["notice"] + ' here is what in your target remote dir:')
        for file_ in files:
            logger.info('\t\t \033[1;36;49m %s \033[0m' % file_)


def make_sure(v_dict):
    logger.info(config["notice"] + ' Your target hosts:')
    for host in hosts:
        logger.info('\t\t \033[1;33;49m %s \033[0m' % host)

    if v_dict["file_name"]:
        logger.info(config["notice"] + ' Your file to send:')
        logger.info('\t\t \033[1;33;49m %s \033[0m' % os.path.join(v_dict["local_dir"],
                                                                   v_dict["file_name"]))
        logger.info(config["notice"] + ' Where your file will be sent:')
        logger.info('\t\t \033[1;33;49m %s \033[0m' % v_dict["remote_dir"])

    if v_dict["command"]:
        logger.info(config["notice"] + ' Your command to execute:')
        logger.info('\t\t \033[1;33;49m %s \033[0m' % v_dict["command"])

        logger.info(
            config["notice"] + ' if no block : \033[1;33;49m %s \033[0m' % (
                'no block' if v_dict["noblock"] else 'block'))

    _input = raw_input('\033[1;36;49m Are you sure all above? (y/n) \033[0m')
    if _input != 'y':
        sys.exit()


def convert_to_full_path(file_path, host):
    return file_path if not file_path.startswith('~') else '/home/' + hosts[host][0] + '/' + config[
        "default_workspace"]


def login_remote_hosts(v_dict):
    session = paramiko.SSHClient()
    session.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    for host in hosts:
        logger.info('******************* \033[1;36;49m %s \033[0m *******************' % host)
        session.connect(hostname=host, port=22, username=hosts[host][0],
                        password=hosts[host][1])

        if v_dict["file_name"]:

            local_file = os.path.join(v_dict["local_dir"], v_dict["file_name"])
            remote_dir = convert_to_full_path(v_dict["remote_dir"], host)
            remote_file = os.path.join(remote_dir, v_dict["file_name"])

            sftp = session.open_sftp()
            prepare_remote_dir(sftp=sftp, remote_dir=remote_dir)
            # print sftp.listdir(remote_dir)
            # print sftp.listdir_attr(remote_dir)
            # print sftp.stat(remote_dir)
            # print sftp.lstat(remote_dir)
            # print sftp.normalize(remote_dir)
            if sftp.put(localpath=local_file, remotepath=remote_file):
                logger.info(config["success"] + ' your file has been sent')
            list_remote_dir(sftp=sftp, remote_dir=remote_dir)

        if v_dict["command"]:
            stdin, stdout, stderr = session.exec_command(command=v_dict["command"])

            if not v_dict["noblock"]:
                out = stdout.read()
                logger.info(config["success"] + ' execute command end')
                if v_dict["output"]:
                    output_file = open(v_dict["output"], 'a')
                    output_file.write(out)
                    output_file.close()
                    logger.info(config["notice"] + ' result has been output to file'
                                                   ' \033[1;33;49m %s \033[0m' % v_dict["output"])
                else:
                    print out
            else:
                logger.info(config["success"] + ' command is executing')
                time.sleep(2)

    session.close()


def main():
    logger.info('#####################################################################')
    logger.info('#      ______                              __                __     #')
    logger.info('#     / ____/___  ____ ___  ____   ___  __/ /_ ___   __   __/ /_    #')
    logger.info('#    / /   / __ \/ __ `__ \/ __ \/` _ \/_  __/` _ \/ __ \/_  __/    #')
    logger.info('#   / /___/ /_/ / / / / / / /_/ /  ___/ / /_/  ___/ / / / / /_      #')
    logger.info('#   \____/\____/_/ /_/ /_/ .___/\____/  \__/\____/_/ /_/  \__/      #')
    logger.info('#                       /_/                                         #')
    logger.info('#                                                                   #')
    logger.info('#####################################################################')

    v_dict = parse_args()
    make_sure(v_dict)
    login_remote_hosts(v_dict)


if __name__ == '__main__':
    main()
