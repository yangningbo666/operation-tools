#coding: utf-8
import csv
import time
import pandas as pd
from mail_by_local import send_email
import logging

logger = logging.getLogger(__name__)
logger.setLevel(level = logging.INFO)
handler = logging.FileHandler("log.txt")
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

console = logging.StreamHandler()
console.setLevel(logging.INFO)

logger.addHandler(handler)
logger.addHandler(console)

date = time.strftime("%Y%m", time.localtime())
SUMMARY_TABLE = date + "_SummaryTable" + ".csv"
MAIL_ADDRESS_INDEX = 7
PERSON_INDEX = 4

'''
IP,type,用户名,密码,业务责任人,申请人,使用人,业务责任人邮箱(邮箱以；间隔，且最后一个邮箱后面也存在分号，例如：yangningbo666@gmail.com;)
'''

def read_from_csv(filename):
    '''
    IN: csv_file
    OUT: list:n*n
    '''
    info_arr = []
    csv_lines = csv.reader(open(filename, 'r'))
    for line in csv_lines:
        if line != []:
            info_arr.append(line)
    return info_arr

def get_person(data):
    person = []
    for line in data:
        if len(line[PERSON_INDEX]) > 5:
            person.append(line[PERSON_INDEX])
        else:
            print("CAN NOT FIND PERSION", line)
    # print(person)
    person = list(set(person))
    return person

def get_mail_address(data, person):
    for line in data:
        mail_list = []
        if line[PERSON_INDEX] == person:
            tmp = line[MAIL_ADDRESS_INDEX]
            if len(tmp)>5:
                mail_list = tmp[:-1]
            else:
                logger.error(person, "--DO NOT HAVE EMAIL!please add it in MAIL_QUERY and redo previous process!")
            break
    return mail_list

def get_context(data, person):
    context = []
    for line in data:
        tmp = []
        if line[PERSON_INDEX]  == person:
            tmp = line[:-1]
            context.append(tmp)
    return context

def list2csv(file, name, data):
    '''
    name : ['code', 'url' , 'title', 'server', 'type', 'x_power_by', 'location']
    data : n*n
    '''
    # data = [[row[i] for row in data] for i in range(len(data[0]))]
    writerCSV=pd.DataFrame(data=data, columns= name)
    writerCSV.to_csv(file, encoding="utf_8_sig", index=None)

if __name__ == "__main__":
    name = ["IP", "type", "用户名", "密码", "业务责任人", "申请人", "使用人"]
    smtp_host = 'localhost'
    port = 25 
    sender_address ='root'
    cc_receiver_address = "yangningbo@huawei.com"
    summary_table = read_from_csv(SUMMARY_TABLE)[1:]
    person_list = get_person(summary_table)
    i = 0
    for person in person_list:
        i = i + 1
        if i < 5:
            attach_path = ""
            attach_file = "_"+person+".csv"
            mail_list = get_mail_address(summary_table, person)
            context = get_context(summary_table, person)
            host_num = len(context)
            list2csv(attach_file, name, context)
            try:
                receiver_address = mail_list
                subject = '弱密码'+str(date)
                content = '{date},您所负责的业务名下弱密码的设备数有{host_num}台 '.format(date = date , host_num = host_num)
                send_email(smtp_host, port, sender_address, receiver_address, cc_receiver_address, subject, content, attach_path, attach_file)
                logger.info(person+"-- mail has sent!")
            except Exception as err:
                logger.error(person+err)