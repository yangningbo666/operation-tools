#!/usr/bin/python
# -*- coding: UTF-8 -*-

import pandas as pd
import time
import csv
import logging


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')

date = time.strftime("%Y%m", time.localtime())
EASY_PASSWORD = date + "_EasyPassword" + ".csv"
HOST_QUERY = date + "_HostQueryList" + ".csv"
REDIS = date + "_Redis" + ".txt"
MAIL_QUERY = date + "_MailQureyList" + ".csv"
HOST_TYPE = "Mysql"
KEYWORD = "root"
USER_INDEX = 4
HOST_TYPE_INDEX = 6
SUMMARY_TABLE = date + "_SummaryTable" + ".csv"


# final_result = IP, type, 用户名, 密码, 业务责任人, 业务责任人邮箱, 申请人, 使用人
final_result = []


def read_from_csv(filename):
    info_arr = []
    csv_lines = csv.reader(open(filename, 'r', encoding="UTF-8"))
    for line in csv_lines:
        info_arr.append(line)
    logging.info(filename+"--finish read!")
    return info_arr


def read_from_txt(filename):
    info_arr = []
    with open(filename, 'r') as f:
        lines = f.readlines()
        for line in lines:
            if "=" not in line:
                info_arr.append(line.split(":")[0])
    info_arr = list(set(info_arr))
    logging.info(filename+"--finish read!")
    return info_arr


def list2csv(filename, name, data):
    '''
    name : ['code', 'url' , 'title', 'server', 'type', 'x_power_by', 'location']
    data : n*n
    '''
    # data = [[row[i] for row in data] for i in range(len(data[0]))]
    writerCSV=pd.DataFrame(data=data, columns= name)
    writerCSV.to_csv(filename, encoding="utf_8_sig", index=None)
    logging.info(filename+"--finish write!")

def preprocess_easy_password(data, host_type, keyword):
    new_data = []
    for line in data:
        if line[HOST_TYPE_INDEX] == host_type and keyword not in line[USER_INDEX]:
            continue
        new_data.append(line)
    logging.info("Delate line that are not ROOT user in Mysql type！")
    return new_data
    
def person2mail(persons, mail_query):
    mail_list = ""
    person_list = persons.split(",")
    for person in person_list:
        mail_index = mail_query[mail_query[0] == person].index.tolist()
        if mail_index == []:
            logging.error(person, "--DO NOT HAVE EMAIL,please add it in " + MAIL_QUERY+",and redo this process!")
            #print("NO MAIL----", person)
            continue
        else:
            mail_index = mail_index[0]
        mail_list = mail_list + mail_query[1][mail_index]+ ";"
    return mail_list
'''
['\ufeff通信IP', '主机IP', '主机名称', '群组名称', '用户名', '弱口令', '类型', '时间', '状态', '主机时间']
['\ufeffIP', '密码', '创建人', '部门', '业务', '业务责任人', '系统', 'CPU核心数', '内存大小（G）', '硬盘（G）', '使用人', '标签', '创建时
间', '失效时间'],
'''

if __name__ == '__main__':
    easy_password = pd.DataFrame(preprocess_easy_password(read_from_csv(EASY_PASSWORD)[1:], HOST_TYPE, KEYWORD))
    redis = read_from_txt(REDIS)
    host_query = pd.DataFrame(read_from_csv(HOST_QUERY)[1:])
    mail_query = pd.DataFrame(read_from_csv(MAIL_QUERY)[1:])
    name = ["IP", "type", "用户名", "密码", "业务责任人", "申请人", "使用人", "业务责任人邮箱"]

    # final_result = ["IP", "type", "用户名", "密码", "业务责任人", "业务责任人邮箱", "申请人", "使用人"]
    for i in range(len(easy_password)):
        tmp = ['' for _ in range(8)] 
        tmp[0] = easy_password[0][i]
        tmp[1] = easy_password[6][i]
        tmp[2] = easy_password[4][i]
        tmp[3] = easy_password[5][i]
        host_index = 0
        host_index = host_query[host_query[0] == easy_password[0][i]].index.tolist()
        if host_index == []:
            # print("NO HOST------",easy_password[0][i])
            host_index = ''
            final_result.append(tmp)
            continue
        else:
            host_index=host_index[0]
        tmp[4] = host_query[5][host_index]
        tmp[5] = host_query[2][host_index]
        tmp[6] = host_query[10][host_index]
        tmp[7] = person2mail(host_query[5][host_index], mail_query)
        final_result.append(tmp)
    logging.info(HOST_QUERY+"--finish!")
    for i in range(len(redis)):
        tmp = ['' for _ in range(8)] 
        host_index = 0
        host_index = host_query[host_query[0] == redis[i]].index.tolist()
        tmp[0] = redis[i]
        tmp[1] = "Redis"
        if host_index == []:
            # print("NO HOST------",easy_password[0][i])
            host_index = ''
            final_result.append(tmp)
            continue
        else:
            host_index=host_index[0]
        # tmp[1] = easy_password[6][i]
        # tmp[2] = easy_password[4][i]
        # tmp[3] = easy_password[5][i]
        tmp[4] = host_query[5][host_index]
        tmp[5] = host_query[2][host_index]
        tmp[6] = host_query[10][host_index]
        tmp[7] = person2mail(host_query[5][host_index], mail_query)
        final_result.append(tmp)
    logging.info(REDIS+"--finish!")
    list2csv(SUMMARY_TABLE, name, final_result)
    logging.info(SUMMARY_TABLE+"--created!")
