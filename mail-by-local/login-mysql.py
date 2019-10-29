#!/usr/bin/python
# -*- coding: UTF-8 -*-

import pymysql
import logging

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')


def connectDB(host, port, user, passwd):
    data = ''
    flag = 0
    try:
        conn = pymysql.connect(host=host, port=3306,
                               user='root', passwd=passwd)
        cursor = conn.cursor()
        cursor.execute('SELECT VERSION()')
        data = cursor.fetchone()
        print(data)
    except:
        pass
    if data != '':
        flag = 1
    return flag


def txt2list(filename):
    info_arr = []
    with open(filename, 'r') as f:
        for line in f:
            tmp = line.replace('\n', '').split(',')
            info_arr.append(tmp)
    return info_arr


def write_to_txt(file, data):
    with open(file, 'w') as f:
        for line in data:
            f.write(line+'\n')


if __name__ == "__main__":
    data = txt2list('passwd.txt')
    new_data = []
    for line in data:
        new_line = []
        flag = 0
        #txt = input("请输入：")
        host = line[0]
        port = line[1]
        user = line[2]
        passwd = line[3]
        # print log
        # logging.info(host)
        # logging.info(port)
        # logging.info(user)
        # logging.info(passwd)

        flag = str(connectDB(host, port, user, passwd))
        new_line = [host, port, user, passwd, flag]
        logging.info(new_line)

        str_line = ','.join(new_line)
        new_data.append(str_line)
    write_to_txt('result.txt', new_data)
