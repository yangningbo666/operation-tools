#!/usr/bin/python
# -*- coding: UTF-8 -*-

import subprocess
import socket
import datetime
import os
import ctypes
import platform

NO_TOMCAT = 0
NO_TOMCAT_CONF = 1
NO_TOMCAT_LOG = 2
SUCCESS = 6

file_names = []


def check_memory(path):
    i = 0
    for dirpath, _, filename in os.walk(path):
        for ii in filename:
            i += os.path.getsize(os.path.join(dirpath, ii))
    memory = i / 1024. / 1024. / 1024.
    return memory


def get_free_space(folder):
    """ Return folder/drive free space (in bytes)
    """
    if platform.system() == 'Windows':
        free_bytes = ctypes.c_ulonglong(0)
        ctypes.windll.kernel32.GetDiskFreeSpaceExW(
            ctypes.c_wchar_p(folder), None, None, ctypes.pointer(free_bytes))
        return free_bytes.value/1024/1024/1024
    else:
        st = os.statvfs(folder)
        return st.f_bavail * st.f_frsize/1024/1024/1024.


def get_nday_list(n):
    before_n_days = []
    for i in range(1, n + 1)[::-1]:
        before_n_days.append(
            str(datetime.date.today() - datetime.timedelta(days=i)))
    return before_n_days


def get_path_list():
    response_code = 0
    path_list = ['' for _ in range(3)]
    path_list_tmp = ''
    # prefix_path_index = 0
    tmp1 = subprocess.Popen(['ps -efw'], stdout=subprocess.PIPE, shell=True)
    tmp2 = subprocess.Popen(
        ['grep java'], stdin=tmp1.stdout, stdout=subprocess.PIPE, shell=True)
    tmp3 = subprocess.Popen(
        ['grep catalina.startup.Bootstrap'], stdin=tmp2.stdout, stdout=subprocess.PIPE, shell=True)
    ps_tmp = tmp3.stdout.read()
    lines = ps_tmp.split('\n')
    if len(lines) < 2:
        response_code = NO_TOMCAT
        return response_code, path_list
    for line in lines:
        if 'Dcatalina.base' in line:
            path_list_tmp = line.split()
            break
    if path_list_tmp == '':
        response_code = NO_TOMCAT_CONF
        return response_code, path_list
    for section in path_list_tmp:
        if "catalina.base" in section:
            path_list[0] = section.split('=')[-1]
        elif "catalina.home" in section:
            path_list[1] = section.split('=')[-1]
        elif "catalina.log.path" in section:
            path_list[2] = section.split('=')[-1]
        else:
            pass
    if path_list == ['' for _ in range(3)]:
        response_code = NO_TOMCAT_CONF
        return response_code, path_list
    response_code = SUCCESS
    return response_code, path_list


def get_absolute_path(path_tmp_pre, path_list):
    if path_tmp_pre[0] == '/':
            path_tmp = path_tmp_pre
    elif path_tmp_pre[0] == '$':
        if '${catalina.base}' in path_tmp_pre:
            path_tmp = path_list[0] +'/' + path_tmp_pre.split('/', 1)[-1]
        elif '${catalina.home}' in path_tmp_pre:
            path_tmp = path_list[1] +'/' + path_tmp_pre.split('/', 1)[-1]
        elif '${catalina.log.path}' in path_tmp_pre:
            path_tmp = path_list[1] +'/' + path_tmp_pre.split('/', 1)[-1]
        else:
            write_log("[EREOR] CAN'T RESOLVE --" + path_tmp_pre)
    else:
        if path_list[0] != '':
            root_path = path_list[0]
        else:
            root_path = path_list[1]
        path_tmp = root_path + '/' + path_tmp_pre
    return path_tmp

def get_log_file_path(path_list):
    '''
    get the path of every log!
    '''
    if path_list[0] != '':
        root_path = path_list[0]
    else:
        root_path = path_list[1]
    log_paths = ['' for _ in range(6)]
    if os.path.exists(root_path + '/conf/logging.properties'):
        conf_tmp1 = subprocess.Popen(
            ['cat ' + root_path + '/conf/logging.properties'], stdout=subprocess.PIPE, shell=True)
        conf_tmp2 = subprocess.Popen(
            ['grep directory'], stdin=conf_tmp1.stdout, stdout=subprocess.PIPE, shell=True)
        tmp_log_path_conf = conf_tmp2.stdout.read()
        for line in tmp_log_path_conf.split('\n'):
            path_tmp = ''
            if '1catalina' in line:
                path_tmp_pre = line.split('=')[-1].strip()
                path_tmp = get_absolute_path(path_tmp_pre, path_list)
                log_paths[0] = path_tmp
                log_paths[1] = path_tmp
            elif '2localhost' in line:
                path_tmp_pre = line.split('=')[-1].strip()
                path_tmp = get_absolute_path(path_tmp_pre, path_list)
                log_paths[2] = path_tmp
            elif '3manager' in line:
                path_tmp_pre = line.split('=')[-1].strip()
                path_tmp = get_absolute_path(path_tmp_pre, path_list)
                log_paths[3] = path_tmp
            elif '4host-manager' in line:
                path_tmp_pre = line.split('=')[-1].strip()
                path_tmp = get_absolute_path(path_tmp_pre, path_list)
                log_paths[4] = path_tmp
    else:
        for i in range(5):
            log_paths[i] = root_path + '/logs'
            
    if os.path.exists(root_path + '/conf/server.xml'):
        conf_tmp3 = subprocess.Popen(
            ['cat ' + root_path + '/conf/server.xml'], stdout=subprocess.PIPE, shell=True)
        conf_tmp4 = subprocess.Popen(
            ['grep log'], stdin=conf_tmp3.stdout, stdout=subprocess.PIPE, shell=True)
        tmp_log_path_conf = conf_tmp4.stdout.read()
        print(tmp_log_path_conf)
        for line in tmp_log_path_conf.split():
            if 'directory' in line:
                print(line)
                path_tmp_pre = line.split('=')[-1].strip('\"').strip('\'')
                path_tmp = get_absolute_path(path_tmp_pre, path_list)
                log_paths[5] = path_tmp
                break
    else:
        log_paths[5] = root_path + '/logs'
    return log_paths


def cp_file(src_path, dir_path):
    hostname = socket.gethostname()
    ip = socket.gethostbyname(hostname)
    ip = ip.replace('.', '-')
    cmd = ['cp', src_path, dir_path]
    subprocess.Popen(cmd, stdout=subprocess.PIPE)


def write_to_txt(filename, data):
    with open(filename, 'w') as f:
        for line in data:
            f.write(line + '\n')


def write_log(content):
    with open("/tmp/get-logs-soc.txt", 'a') as f:
        f.write(content)
        f.write('\n')
        print(content)


if __name__ == "__main__":
    write_log("[INFO] BEGIN!!!!!!")
    # get base path of tomcat or catalina and copy files except temp and logs
    response, path_list = get_path_list()
    write_log('[INFO]responese code:{response}'.format(response=response))
    if response == 6:
        write_log('[INFO] catalina base path:{path}'.format(path=path_list[0]))
        write_log('[INFO] catalina home path:{path}'.format(path=path_list[1]))
        write_log('[INFO] catalina log path:{path}'.format(path=path_list[2]))
        if path_list[0] != '':
            root_path = path_list[0]
        else:
            root_path = path_list[1]
        free_space = get_free_space('/tmp')
        file_size = check_memory(root_path)
        if free_space > file_size:
            write_log("[INFO] free space: {free_space} \n[INFO] files_size:{file_size}".format(free_space=free_space, file_size=file_size))
            file_path = '/tmp/tomcat_proof'
            if not os.path.exists(file_path):
                os.makedirs(file_path)
            for i in os.listdir(root_path):
                if i != 'logs' and i != 'temp':
                    os.system('cp -r ' + root_path + '/'+ i + ' ' + file_path)
            # os.system('cp -r ' + root_path + '/* ' + file_path)
            # os.system('rm -rf ' + file_path + '/temp')
            # os.system('rm -rf ' + file_path + '/logs/*')
            write_log("[INFO] Finish to copy root path!")
            # get the path of each kind of log file and return the list of all logs
            log_paths = get_log_file_path(path_list)
            tmp_log_path = file_path + '/logs'
            if not os.path.exists(tmp_log_path):
                os.makedirs(tmp_log_path)
            if log_paths != ['' for _ in range(6)]:
                file_list = []
                for i in log_paths:
                    if i != '':
                        file_list = file_list + os.listdir(i)
                file_list = list(set(file_list))
                write_to_txt(tmp_log_path + '/file-list.txt', file_list)

            # get filenames of each kind of logs by date
            date_list = get_nday_list(3)
            if log_paths[0] != '':
                file_names.append(log_paths[0] + "/catalina.out")
            for date in date_list:
                # file_names.append(log_paths[1] + "/catalina." + date + '*')
                # file_names.append(log_paths[2] + "/localhost." + date + '*')
                # file_names.append(log_paths[3] + "/manager." + date + '*')
                # file_names.append(log_paths[4] + "/host-manager." + date + '*')
                # file_names.append(log_paths[5] + "/localhost_access_log." + date + '*')
                for log_path in list(set(log_paths)):
                    if log_path != '':
                        file_list = os.listdir(log_path)
                        for i in file_list:
                            if i == '':
                                break
                            if date in i:
                                file_names.append(log_path +'/'+ i)
                
            # begin copy the log files
            for file_name in file_names:
                os.system("cp " + file_name + ' ' + tmp_log_path)
            write_log("[INFO] Finish to copy logs!")
            file_path = '/tmp/tomcat_proof'
            tar_file = '/tmp/tomcat_proof.tar.gz'
            os.system("tar czf " + tar_file + ' -C ' + file_path + ' .')
            write_log("[INFO] Finish to tar!")
        else:
            write_log("[ERROR] Free spcace is limited!\n[INFO] free space: {free_space} \n[INFO] files_size:{file_size}".format(free_space=free_space, file_size=file_size))
    else:
        write_log("[ERROR]Fail to find log")
    print("FINISH!!")
