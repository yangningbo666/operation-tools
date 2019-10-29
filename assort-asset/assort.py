#!/usr/bin/python
# -*- coding: UTF-8 -*-
 
import time
import os
import re
import xlrd
import xlwt
import csv
import logging


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')


def csv_load(filename):
    csvfile = open(filename, encoding = 'utf-8-sig')
    data = csv.reader(csvfile)
    dataset = []
    for line in data:
        dataset.append(line)
    csvfile.close()
    return dataset

def xlrd_load(filename, sheetname):
    dataset = []
    workbook = xlrd.open_workbook(filename)
    sheet = workbook.sheet_by_name(sheetname)
    dataset = [['' for _ in range(sheet.ncols)] for _ in range(sheet.nrows)]
    for i in range(sheet.nrows):
        for j in range(sheet.ncols):
            dataset[i][j] = sheet.cell(i,j).value
    return dataset

def xlwt_write(filename, sheetname, dataset):
    workbook = xlwt.Workbook(encoding='utf-8')
    worksheet = workbook.add_sheet(sheetname)
    for i in range(len(dataset)):
        for j in range(len(dataset[0])):
            worksheet.write(i,j, dataset[i][j])
    workbook.save(filename)

def get_sortinfo(service, dataset):
    sort_info = ''
    for line in dataset:
        if line[0] == service:
            sort_info = line[1]
            break
    return sort_info


def main():
    dataset = []
    lost_area = []
    b_ipset = set()
    date = time.strftime("%Y-%m-%d", time.localtime()) 
    host_file = "vmserver-" + date + ".csv"
    info_file = "info.xlsx"
    b_ip_file = "b-ip.xlsx"
    result_file = "result.xls"
    if os.path.exists(host_file):
        host_data = csv_load(host_file)
        logging.info(host_data[0])
    else:
        logging.error(host_file+" CAN FIND !!!")
        return False
    if os.path.exists(info_file):
        service_data = xlrd_load(info_file, 'service')
        area_data = xlrd_load(info_file, 'area')
        china_area = [line[0] for line in area_data[1:] if line[0] != ''] 
        russia_area = [line[1] for line in area_data[1:] if line[1] != '']
        sin_area = [line[2] for line in area_data[1:] if line[2] != '']
        logging.info(service_data[0])
        logging.info(china_area)
        logging.info(russia_area)
        logging.info(sin_area)
    else:
        logging.error(info_file+" CAN FIND !!!")
        return False
    for line in host_data:
        new_line = []
        if line[3] == "INUSE" and line[10] not in ["vmall", "test" , '']:
            if line[9] in china_area+russia_area+sin_area:
                if line[9] in china_area:
                    area_tmp = "中国"
                    sortinfo_tmp = get_sortinfo(line[10], service_data)
                    if sortinfo_tmp == '':
                        logging.error(line[10] + "CAN NOT FIND!")
                elif line[9] in russia_area:
                    area_tmp = "俄罗斯"
                    sortinfo_tmp = get_sortinfo(line[10], service_data)
                    if sortinfo_tmp == '':
                        logging.error(line[10] + "CAN NOT FIND!")
                elif line[9] in sin_area:
                    area_tmp = "新加坡"
                    sortinfo_tmp = get_sortinfo(line[10], service_data)
                    if sortinfo_tmp == '':
                        logging.error(line[10] + "CAN NOT FIND!")
                else:
                    pass
                new_line.append(line[2])
                new_line.append(area_tmp)
                new_line.append(sortinfo_tmp)
                new_line.append(line[10])
                dataset.append(new_line)
                b_ipset.add(re.findall(r'\d+?\.\d+?\.', line[2])[0] + '*.*')
                b_iplist = list(b_ipset)
            else:
                lost_area.append(line[9])
    xlwt_write(result_file, "Sheet1", dataset)
    b_ip_data = xlrd_load(b_ip_file, 'Sheet1')
    tmp_iplist = [tmp[0] for tmp in b_ip_data]
    for ip in b_iplist:
        if ip not in tmp_iplist:
            b_ip_data.append([ip, "未知"])
    xlwt_write("tmp-b-ip.xls", "Sheet1", b_ip_data)

    

if __name__ == "__main__":
    main()